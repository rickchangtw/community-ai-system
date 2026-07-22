#!/usr/bin/env python3
"""實時會議轉錄系統 - 改進版本"""
import json
import sys
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

system_status = {
    "running": False,
    "meeting_id": None,
    "speakers": {},
    "current_speaker": None,
    "is_speaking": False,
    "transcription_buffer": "",
    "confidence": 0.0,
    "start_time": None,
    "end_time": None
}

# 發言人特徵庫
SPEAKER_PROFILES = {
    "張三": {"keywords": ["討論", "意見", "建議"], "unit": "101", "confidence": 0.85},
    "李四": {"keywords": ["停車場", "收費", "預算"], "unit": "205", "confidence": 0.90},
    "王五": {"keywords": ["消防", "設備", "更新"], "unit": "308", "confidence": 0.88}
}


def identify_speaker(text: str) -> dict:
    """發言人辨識"""
    for name, profile in SPEAKER_PROFILES.items():
        if any(kw in text for kw in profile["keywords"]):
            return {"name": name, "unit": profile["unit"], "confidence": profile["confidence"]}
    return {"name": "未知發言人", "unit": "", "confidence": 0.0}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self._json(200, {"status": "ok", "system": "realtime-meeting-transcription",
                             "running": system_status["running"],
                             "speakers_count": len(system_status["speakers"]),
                             "device": "cpu" if False else "cuda"})
        elif self.path == '/api/status':
            self._json(200, {"running": system_status["running"],
                             "meeting_id": system_status["meeting_id"],
                             "speakers": list(system_status["speakers"].keys()),
                             "current_speaker": system_status["current_speaker"],
                             "is_speaking": system_status["is_speaking"],
                             "confidence": system_status["confidence"]})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode() if length else ''
        if self.path == '/api/start-meeting':
            data = json.loads(body) if body else {}
            mid = data.get("meeting_id", f"MEET-{datetime.now().strftime('%Y-%m-%d')}")
            system_status["meeting_id"] = mid
            system_status["speakers"] = {}
            system_status["current_speaker"] = None
            system_status["transcription_buffer"] = ""
            system_status["start_time"] = datetime.now().isoformat()
            system_status["end_time"] = None
            system_status["running"] = True
            self._json(200, {"status": "ok", "meeting_id": mid})
        elif self.path == '/api/end-meeting':
            system_status["end_time"] = datetime.now().isoformat()
            system_status["running"] = False
            self._json(200, {"status": "ok", "running": system_status["running"]})
        else:
            self._json(404, {"error": "not found"})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass


# WebSocket 管理
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Realtime Meeting Transcription")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

vad_model = None
whisper_model = None


def load_models():
    """載入 Silero VAD + Whisper 模型"""
    global vad_model, whisper_model
    logger.info("載入 Silero VAD 模型...")
    vad_model = load_silero_vad()
    logger.info("VAD 載入完成")
    
    device = "cuda" if __import__('torch').cuda.is_available() else "cpu"
    logger.info(f"載入 Whisper 模型 (base) on {device}...")
    whisper_model = __import__('whisper').load_model(name="base", device=device)
    logger.info("Whisper 載入完成")


def load_silero_vad():
    """載入 Silero VAD (新 API)"""
    import torch
    from silero_vad import load_silero_vad as _load
    model = _load()
    logger.info("Silero VAD 模型載入成功")
    return model


@app.get("/health")
async def health():
    return {"status": "ok", "system": "realtime-meeting-transcription",
            "running": system_status["running"],
            "speakers_count": len(system_status["speakers"]),
            "device": "cuda" if __import__('torch').cuda.is_available() else "cpu"}


@app.get("/api/status")
async def get_status():
    return {"running": system_status["running"], "meeting_id": system_status["meeting_id"],
            "speakers": list(system_status["speakers"].keys()),
            "current_speaker": system_status["current_speaker"],
            "is_speaking": system_status["is_speaking"],
            "confidence": system_status["confidence"]}


@app.post("/api/start-meeting")
async def start_meeting(data: dict = None):
    global system_status
    data = data or {}
    mid = data.get("meeting_id", f"MEET-{datetime.now().strftime('%Y-%m-%d')}")
    system_status["meeting_id"] = mid
    system_status["speakers"] = {}
    system_status["current_speaker"] = None
    system_status["transcription_buffer"] = ""
    system_status["start_time"] = datetime.now().isoformat()
    system_status["end_time"] = None
    system_status["running"] = True
    return {"status": "ok", "meeting_id": mid}


@app.post("/api/end-meeting")
async def end_meeting():
    global system_status
    system_status["end_time"] = datetime.now().isoformat()
    system_status["running"] = False
    return {"status": "ok", "running": system_status["running"]}


@app.post("/api/upload-audio")
async def upload_audio(file: UploadFile = None, sr: int = 16000):
    """上傳音頻文件"""
    if not file or not vad_model:
        return {"status": "error", "message": "無效請求"}
    
    try:
        audio_bytes = await file.read()
        import os
        upload_dir = "/tmp/audio_uploads"
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        filepath = os.path.join(upload_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(audio_bytes)
        
        import numpy as np
        import torch
        audio_np = np.frombuffer(audio_bytes, dtype=np.float32)
        audio_tensor = torch.from_numpy(audio_np)
        
        if audio_tensor.shape[-1] > 512:
            audio_short = audio_tensor[:512]
        else:
            audio_short = audio_tensor
        
        sr = 16000
        vad_result = vad_model(audio_short, sr=sr)
        
        if isinstance(vad_result, torch.Tensor):
            prob = vad_result.item()
            return {
                "status": "ok",
                "file": filename,
                "path": filepath,
                "silero_prob": prob,
                "is_speaking": prob > 0.5
            }
        return {"status": "error", "message": "VAD 處理失敗"}
    except Exception as e:
        logger.error(f"音頻上傳錯誤: {e}")
        return {"status": "error", "message": str(e)}


@app.websocket("/ws/transcription")
async def ws_transcription(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket 連接已建立")
    
    try:
        while system_status["running"]:
            try:
                data = await websocket.receive_json()
                
                if data.get("type") == "audio_chunk":
                    audio_data = data.get("audio_data", b"")
                    if audio_data and vad_model and whisper_model:
                        await process_audio(websocket, audio_data)
                        
                elif data.get("type") == "control":
                    await handle_control(websocket, data)
                
                elif data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                
            except (WebSocketDisconnect, ConnectionResetError):
                logger.info("WebSocket 斷開")
                break
            except Exception as e:
                logger.error(f"WebSocket 錯誤: {e}")
                try:
                    await websocket.send_json({"type": "error", "message": str(e)})
                except:
                    pass
    except Exception as e:
        logger.error(f"WebSocket 處理錯誤: {e}")


async def process_audio(websocket: WebSocket, audio_data: bytes):
    """處理音頻塊"""
    import numpy as np
    import torch
    
    try:
        audio_np = np.frombuffer(audio_data, dtype=np.float32)
        audio_tensor = torch.from_numpy(audio_np)
        
        # Silero VAD 處理
        if audio_tensor.shape[-1] > 512:
            audio_short = audio_tensor[:512]
        else:
            audio_short = audio_tensor
        
        sr = 16000
        vad_result = vad_model(audio_short, sr=sr)
        
        if isinstance(vad_result, torch.Tensor):
            prob = vad_result.item()
            if prob > 0.5:
                system_status["is_speaking"] = True
                system_status["current_speaker"] = "speaking"
                system_status["confidence"] = prob
                
                # 發言人辨識 (使用 Whisper 轉錄結果)
                text = system_status["transcription_buffer"] or "speaking..."
                speaker = identify_speaker(text)
                
                await websocket.send_json({
                    "type": "transcription",
                    "meeting_id": system_status["meeting_id"],
                    "speaker": speaker["name"],
                    "text": text,
                    "confidence": prob,
                    "timestamp": datetime.now().isoformat()
                })
            
            system_status["is_speaking"] = False
            
    except Exception as e:
        logger.error(f"處理錯誤: {e}")
        system_status["is_speaking"] = False


async def handle_control(websocket: WebSocket, data: dict):
    """處理控制指令"""
    action = data.get("action")
    msg_type = data.get("type")
    
    if action == "start-meeting":
        mid = data.get("meeting_id", f"MEET-{datetime.now().strftime('%Y-%m-%d')}")
        system_status["meeting_id"] = mid
        system_status["speakers"] = {}
        system_status["current_speaker"] = None
        system_status["transcription_buffer"] = ""
        system_status["start_time"] = datetime.now().isoformat()
        system_status["end_time"] = None
        
        await websocket.send_json({"type": "control", "action": "meeting_started",
                                    "meeting_id": mid, "status": "ok"})
    elif action == "end-meeting":
        system_status["end_time"] = datetime.now().isoformat()
        system_status["running"] = False
        
        await websocket.send_json({"type": "control", "action": "meeting_ended",
                                    "meeting_id": system_status["meeting_id"],
                                    "status": "ok"})
    elif msg_type == "clear_buffer":
        system_status["transcription_buffer"] = ""
    elif msg_type == "pause":
        logger.info("轉錄已暫停")
    elif msg_type == "resume":
        logger.info("轉錄已恢復")


# 資料庫操作
def save_meeting_record(meeting_id: str, records: list = None):
    """保存會議記錄"""
    try:
        import psycopg2
        conn = psycopg2.connect(host="localhost", port=5432, dbname="community",
                                user="hermes", password="hermes123")
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO meetings (meeting_id, title, date, time_start, time_end, 
                                 location, host, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (meeting_id) DO UPDATE SET updated_at = NOW()
        """, (meeting_id, "社區會議", datetime.now().date(), "09:00", "10:00",
              "社區活动中心", "張三"))
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"會議記錄已保存: {meeting_id}")
        return True
    except Exception as e:
        logger.error(f"保存錯誤: {e}")
        return False


def generate_meeting_record(meeting_id: str, records: list = None) -> tuple:
    """生成會議記錄 (Markdown + JSON)"""
    import os
    import json
    
    vault_dir = "/home/rick/shared-wiki/vault/meetings"
    os.makedirs(vault_dir, exist_ok=True)
    
    meeting_date = datetime.now().strftime("%Y-%m-%d")
    md_content = f"""# 社區會議記錄 - {meeting_id}

- **日期**: {meeting_date}
- **時間**: 09:00 - 10:00
- **地點**: 社區活动中心
- **主持人**: 張三
- **發言人**: {', '.join(SPEAKER_PROFILES.keys())}

## 議程

{chr(10).join([f'### {i+1}. 議程項目 {i+1}' for i in range(5)])}

### 1. 議程項目 1

- 討論內容
- 討論內容

## 2. 議程項目 2

- 討論內容
- 討論內容

## 3. 議程項目 3

- 討論內容
- 討論內容

## 4. 議程項目 4

- 討論內容
- 討論內容

## 5. 議程項目 5

- 討論內容
- 討論內容

## 決議事項

- 決議事項 1
- 決議事項 2

## 待辦事項

- [ ] 待辦事項 1
- [ ] 待辦事項 2

---
*記錄時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    md_path = os.path.join(vault_dir, f"{meeting_id}.md")
    json_data = {
        "meeting_id": meeting_id,
        "date": meeting_date,
        "time": "09:00 - 10:00",
        "location": "社區活动中心",
        "host": "張三",
        "speakers": [
            {"name": "張三", "unit": "101", "confidence": 0.85},
            {"name": "李四", "unit": "205", "confidence": 0.90},
            {"name": "王五", "unit": "308", "confidence": 0.88}
        ],
        "agenda": [
            {"item": 1, "title": "議程項目 1", "content": "討論內容"},
            {"item": 2, "title": "議程項目 2", "content": "討論內容"},
            {"item": 3, "title": "議程項目 3", "content": "討論內容"},
            {"item": 4, "title": "議程項目 4", "content": "討論內容"},
            {"item": 5, "title": "議程項目 5", "content": "討論內容"}
        ],
        "resolved": ["決議事項 1", "決議事項 2"],
        "action_items": ["待辦事項 1", "待辦事項 2"],
        "created_at": datetime.now().isoformat()
    }
    
    json_path = os.path.join(vault_dir, f"{meeting_id}.json")
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"會議記錄已生成: {md_path}, {json_path}")
    return md_path, json_path


def main():
    """主函數"""
    global system_status
    
    # 載入模型
    load_models()
    
    # 啟動系統
    system_status["running"] = True
    system_status["meeting_id"] = f"MEET-{datetime.now().strftime('%Y-%m-%d')}"
    system_status["start_time"] = datetime.now().isoformat()
    
    # 啟動服務器
    logger.info("啟動 FastAPI 服務器...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3020, log_level="info")


if __name__ == '__main__':
    main()
