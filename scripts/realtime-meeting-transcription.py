#!/usr/bin/env python3
"""
實時會議轉錄系統
基於 Silero VAD + Whisper + 發言人辨識 + FastAPI WebSocket

功能：
- 即時語音活動偵測 (Silero VAD)
- 語音轉文字 (Whisper)
- 發言人辨識
- WebSocket 即時推送
- 資料庫儲存
"""

import asyncio
import json
import signal
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import torch
import numpy as np

# 添加項目路徑
sys.path.insert(0, str(Path(__file__).parent))

import torch
import numpy as np
from silero_vad import load_silero_vad, VADIterator
from whisper import load_model as whisper_load_model
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 資料庫配置
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "community",
    "user": "hermes",
    "password": "hermes123"
}

# 模型路徑
MODELS_DIR = Path("/home/rick/models")

# 系統狀態
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

# 初始化 FastAPI 應用
app = FastAPI(title="實時會議轉錄系統", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# 模型載入
vad_model = None
whisper_model = None


def load_models():
    """載入模型"""
    global vad_model, whisper_model
    
    logger.info("載入 Silero VAD 模型...")
    vad_model = load_silero_vad()
    logger.info("Silero VAD 模型載入完成")
    
    logger.info("載入 Whisper 模型 (base)...")
    whisper_model = whisper_load_model(
        name="base",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    logger.info("Whisper 模型載入完成")
    
    logger.info("模型載入完成！")


# WebSocket 連接管理
connected_clients: List[WebSocket] = []


@app.on_event("startup")
async def startup_event():
    """啟動事件"""
    global system_status
    system_status["running"] = True
    logger.info("實時會議轉錄系統啟動")


@app.on_event("shutdown")
async def shutdown_event():
    """關閉事件"""
    global system_status
    system_status["running"] = False
    logger.info("實時會議轉錄系統關閉")


@app.get("/health")
async def health():
    """健康檢查"""
    return {
        "status": "ok",
        "system": "realtime-meeting-transcription",
        "running": system_status["running"],
        "speakers_count": len(system_status["speakers"]),
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }


@app.get("/api/status")
async def get_status():
    """獲取系統狀態"""
    return {
        "running": system_status["running"],
        "meeting_id": system_status["meeting_id"],
        "speakers": list(system_status["speakers"].keys()),
        "current_speaker": system_status["current_speaker"],
        "is_speaking": system_status["is_speaking"],
        "confidence": system_status["confidence"]
    }


@app.post("/api/start-meeting")
async def start_meeting(meeting_data: dict):
    """開始新會議"""
    global system_status
    
    meeting_id = meeting_data.get("meeting_id", f"MEET-{datetime.now().strftime('%Y-%m-%d')}")
    system_status["meeting_id"] = meeting_id
    system_status["speakers"] = {}
    system_status["current_speaker"] = None
    system_status["transcription_buffer"] = ""
    system_status["start_time"] = datetime.now().isoformat()
    system_status["end_time"] = None
    
    logger.info(f"會議開始：{meeting_id}")
    return {"status": "ok", "meeting_id": meeting_id}


@app.post("/api/end-meeting")
async def end_meeting():
    """結束會議"""
    global system_status
    
    if not system_status["running"]:
        return {"status": "error", "message": "系統未運行"}
    
    system_status["end_time"] = datetime.now().isoformat()
    system_status["running"] = False
    
    logger.info(f"會議結束：{system_status['meeting_id']}")
    return {"status": "ok", "meeting_id": system_status["meeting_id"]}


@app.websocket("/ws/transcription")
async def websocket_transcription(websocket: WebSocket):
    """WebSocket 連接 - 接收音頻，返回轉錄結果"""
    await websocket.accept()
    
    logger.info("WebSocket 連接已建立")
    
    try:
        while system_status["running"]:
            # 接收音頻數據
            data = await websocket.receive_json()
            
            if data.get("type") == "audio_chunk":
                # 處理音頻塊
                audio_data = data.get("audio_data", b"")
                if audio_data:
                    await process_audio_chunk(websocket, audio_data)
                    
            elif data.get("type") == "control":
                # 處理控制指令
                await handle_control_command(websocket, data)
                
    except WebSocketDisconnect:
        logger.info("WebSocket 連接斷開")
    except Exception as e:
        logger.error(f"WebSocket 錯誤：{str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


async def process_audio_chunk(websocket: WebSocket, audio_data: bytes):
    """處理音頻塊"""
    global system_status
    
    if vad_model is None or whisper_model is None:
        return
    
    # Silero VAD 語音活動偵測
    audio_np = np.frombuffer(audio_data, dtype=np.float32)
    
    vad = VADIterator()
    vad.update(audio_np)
    
    for segment in vad.get_segments():
        # 語音活動段
        start = segment[0]
        end = segment[1]
        audio_segment = audio_np[start:end]
        
        # Whisper 語音轉文字
        transcription = whisper_transcribe(audio_segment)
        
        # 發言人辨識
        speaker = identify_speaker(transcription)
        
        # 更新系統狀態
        system_status["transcription_buffer"] += transcription
        system_status["current_speaker"] = speaker
        system_status["confidence"] = speaker.get("confidence", 0.0) if speaker else 0.0
        system_status["is_speaking"] = True
        
        # 發送轉錄結果
        await websocket.send_json({
            "type": "transcription",
            "meeting_id": system_status["meeting_id"],
            "speaker": speaker["name"] if speaker else "unknown",
            "text": transcription,
            "confidence": system_status["confidence"],
            "timestamp": datetime.now().isoformat()
        })
    
    system_status["is_speaking"] = False


def whisper_transcribe(audio_np: np.ndarray) -> str:
    """Whisper 語音轉文字"""
    global whisper_model
    
    if whisper_model is None:
        return ""
    
    # 轉換為 16kHz mono
    if audio_np.shape[0] > 16000:
        audio_16k = audio_np[:16000]
    else:
        audio_16k = np.pad(audio_np, (0, 16000 - audio_np.shape[0]))
    
    # 轉錄
    result = whisper_model.transcribe(
        audio_16k,
        language="zh-TW",
        task="transcribe",
        fp16=False
    )
    
    return result["text"]


def identify_speaker(transcription: str) -> dict:
    """發言人辨識（簡化版）"""
    
    # 預定義發言人語音特徵
    for name, profile in SPEAKER_PROFILES.items():
        if any(keyword in transcription for keyword in profile["keywords"]):
            return {
                "name": name,
                "unit": profile["unit"],
                "confidence": profile["confidence"]
            }
    
    # 預設發言人
    return {
        "name": "未知發言人",
        "unit": "",
        "confidence": 0.0
    }


async def handle_control_command(websocket: WebSocket, data: dict):
    """處理控制指令"""
    
    if data.get("type") == "clear_buffer":
        system_status["transcription_buffer"] = ""
        logger.info("轉錄緩衝已清除")
        
    elif data.get("type") == "pause":
        logger.info("轉錄已暫停")
        
    elif data.get("type") == "resume":
        logger.info("轉錄已恢復")


# 資料庫操作
def save_meeting_record(meeting_id: str, records: list = None):
    """保存會議記錄到資料庫"""
    try:
        import psycopg2
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 插入會議記錄
        cursor.execute("""
            INSERT INTO meetings (meeting_id, title, date, time_start, time_end, 
                                 location, host, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (meeting_id) DO UPDATE SET updated_at = NOW()
        """, (
            meeting_id,
            "社區會議",
            datetime.now().date(),
            "09:00",
            "10:00",
            "社區活动中心",
            "張三"
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"會議記錄已保存：{meeting_id}")
        return True
    except Exception as e:
        logger.error(f"保存會議記錄錯誤：{str(e)}")
        return False


# 主函數
def main():
    """主函數 - 啟動 FastAPI 服務"""
    global system_status
    
    # 載入模型
    load_models()
    
    # 啟動系統
    system_status["running"] = True
    system_status["meeting_id"] = f"MEET-{datetime.now().strftime('%Y-%m-%d')}"
    system_status["start_time"] = datetime.now().isoformat()
    
    logger.info("=" * 60)
    logger.info("🎙️  實時會議轉錄系統")
    logger.info("=" * 60)
    logger.info(f"📋 會議編號：{system_status['meeting_id']}")
    logger.info(f"🕐 開始時間：{system_status['start_time']}")
    logger.info(f"🖥️  設備：{torch.cuda.is_available() and 'GPU' or 'CPU'}")
    logger.info("=" * 60)
    
    # 啟動 FastAPI 服務
    logger.info("啟動 FastAPI 服務...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3020,
        log_level="info"
    )
    
    # 保持運行
    import time
    while system_status["running"]:
        time.sleep(1)
    
    logger.info("系統已停止")


if __name__ == "__main__":
    main()
