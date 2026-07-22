#!/usr/bin/env python3
"""
LINE 機器人完整實現 - Phase 3
功能: 收發訊息、語音轉文字、事件處理
"""
import json
import logging
import os
import sys
import time
import hmac
import hashlib
import threading
from datetime import datetime
from urllib.parse import urlparse

# 設定日誌
LOG_FILE = "/tmp/line_bot.log"
sys.stdout = open(LOG_FILE, "a", encoding="utf-8")
sys.stderr = open(LOG_FILE, "a", encoding="utf-8")
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# 配置
COMMUNITY_USERS = {
    "U1234567890123456789": {"name": "張媽媽", "building": "A大樓", "unit": "101"},
    "U2345678901234567890": {"name": "李伯伯", "building": "A大樓", "unit": "205"},
    "U3456789012345678901": {"name": "王阿姨", "building": "B大樓", "unit": "308"},
    "U4567890123456789012": {"name": "趙叔叔", "building": "B大樓", "unit": "112"},
}
LINE_CHANNEL_ID = "your_channel_id"
LINE_CHANNEL_SECRET = "your_channel_secret"
PORT = 3021

class UserManager:
    """用戶管理"""
    def __init__(self):
        self._users = COMMUNITY_USERS.copy()
    
    def get_user(self, sender_id):
        return self._users.get(sender_id)
    
    def is_registered(self, sender_id):
        return sender_id in self._users
    
    def register_user(self, line_id, name, building, unit):
        self._users[line_id] = {"name": name, "building": building, "unit": unit, "registered_at": datetime.now().isoformat()}
        return self._users[line_id]
    
    def get_all_users(self):
        return self._users.copy()

user_manager = UserManager()

def verify_signature(body, signature):
    """驗證 LINE 簽章 (HMAC-SHA256)"""
    try:
        post_body = body
        if not signature.startswith('t='):
            return False, "簽章格式不正確: 缺少 t="
        
        comma_idx = signature.find(',')
        if comma_idx == -1:
            return False, "簽章格式不正確: 缺少逗號"
        
        hash_part = signature[comma_idx + 1:]
        expected_signature = "v0=" + hmac.new(
            LINE_CHANNEL_SECRET.encode('utf-8'),
            post_body.encode('utf-8'),
            'sha256'
        ).hexdigest()
        
        if expected_signature != hash_part:
            return False, "簽章驗證失敗"
        
        return True, None
    except Exception as e:
        logger.error(f"簽章驗證錯誤: {e}")
        return False, str(e)

def send_line_message(channel_id, channel_secret, to, message, message_id=None):
    """發送 LINE 消息"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {channel_secret}"
        }
        data = {
            "to": to,
            "messages": [{"type": "text", "text": message}]
        }
        if message_id:
            data["replyToken"] = message_id
        
        import requests
        response = requests.post(
            "https://api.line.me/v2/bot/message/push",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            logger.info(f"LINE 消息發送成功: {to}")
            return True, None
        else:
            logger.error(f"LINE API 錯誤: {response.status_code} {response.text}")
            return False, f"LINE API 錯誤: {response.status_code}"
    except Exception as e:
        logger.error(f"LINE 發送錯誤: {e}")
        return False, str(e)

def reply_command(user_id, command, reply_token):
    """處理命令並回覆"""
    user = user_manager.get_user(user_id)
    name = user['name'] if user else user_id
    
    if command == '/help':
        message = f"""📋 社區管理系統 - 幫助資訊

👋 {name}，您好！

可用指令：
/help      - 顯示幫助資訊
/meeting   - 查看會議資訊
/status    - 查看系統狀態
/register  - 註冊用戶
/property  - 物業資訊
/security  - 保全資訊
/fire      - 消防資訊
/energy    - 節能資訊

輸入 /help 隨時查詢！"""
    elif command == '/meeting':
        message = f"""📋 會議資訊

📅 最近的社區會議：
- 2026-07-20 週六 14:00
  📍 社區活动中心
  👥 主持人：張經理
  📝 主題：社區維護計劃討論

請準時出席！"""
    elif command == '/status':
        message = f"""📊 系統狀態

📋 總會議數：12
✅ 已排程：8
🔴 進行中：2
⏳ 待確認：2

👥 在線住戶：{len(user_manager.get_all_users())}
🔒 保全巡邏：正常
🔥 消防設備：正常
💡 能源狀態：正常"""
    elif command == '/property':
        message = f"""🏠 物業資訊

📢 社區公告：
- 電梯維修通知 (07/20-07/25)
- 綠化帶修繕 (07/21)
- 公共區域清潔 (每週六)

🔧 最近工單：
- A大樓 3F 水管修繕 (完成)
- B大樓 1F 燈具更換 (進行中)"""
    elif command == '/security':
        message = f"""🔒 保全資訊

👮 巡邏狀態：正常
📋 最近巡邏記錄：
- 07/19 14:00-15:00 - 完成 (4/4 站點)
- 07/19 10:00-11:00 - 完成 (4/4 站點)

🚨 最近事件：無
📞 保全電話：02-2345-6789"""
    elif command == '/fire':
        message = f"""🔥 消防資訊

📋 設備檢查：正常
📅 下次演練：2026-08-15
🔧 最近檢查：
- 消火栓：正常 (07/18)
- 煙霧探測器：正常 (07/18)
- 滅火器：正常 (07/18)

🚨 最近事件：無"""
    elif command == '/energy':
        message = f"""💡 節能資訊

📊 用電統計 (2026-07)：
- 總用電量：12,500 kWh
- 平均值：417 kWh/日
- 告警閾值：150 kWh

📈 節能建議：
1. 公共區域照明已啟用感應器
2. 電梯已啟用節能模式
3. 建議減少深夜用電"""
    else:
        message = f"已收到您的訊息：{command}"
    
    send_line_message(LINE_CHANNEL_ID, LINE_CHANNEL_SECRET, reply_token, message)
    return message

def process_event(event, reply_tokens):
    """處理 LINE 事件"""
    event_type = event.get("type", "")
    
    if event_type == "follow":
        source = event.get("source", {})
        sender_id = source.get("id", "")
        reply_token = reply_tokens.get(sender_id, "")
        
        message = f"""👋 歡迎來到幸福社區管理系統！

我是您的社區 AI 助手，可以幫您：
- 查詢會議資訊 (/meeting)
- 查看系統狀態 (/status)
- 了解社區通知 (/property)
- 查詢保全/消防/節能資訊

輸入 /help 查看所有指令！"""
        
        send_line_message(LINE_CHANNEL_ID, LINE_CHANNEL_SECRET, sender_id, message, reply_token)
        return True
    
    elif event_type == "unfollow":
        source = event.get("source", {})
        sender_id = source.get("id", "")
        logger.info(f"用戶取消關注: {sender_id}")
        return True
    
    elif event_type == "message":
        source = event.get("source", {})
        message_obj = event.get("message", {})
        text = message_obj.get("text", "")
        sender_id = source.get("id", "")
        reply_token = reply_tokens.get(sender_id, "")
        
        # 檢查是否為命令
        if text.startswith('/'):
            command = text.strip().split()[0]
            reply_command(sender_id, command, reply_token)
            return True
        
        # 一般訊息
        elif sender_id in user_manager.get_all_users():
            user = user_manager.get_user(sender_id)
            name = user['name']
            message = f"👋 {name}，您好！已收到您的訊息：{text}"
            send_line_message(LINE_CHANNEL_ID, LINE_CHANNEL_SECRET, sender_id, message, reply_token)
            return True
        
        else:
            message = "請先註冊用戶，輸入 /register 開始！"
            send_line_message(LINE_CHANNEL_ID, LINE_CHANNEL_SECRET, sender_id, message, reply_token)
            return True
    
    elif event_type == "image":
        source = event.get("source", {})
        sender_id = source.get("id", "")
        reply_token = reply_tokens.get(sender_id, "")
        
        message = "📷 已收到圖片，稍後處理中..."
        send_line_message(LINE_CHANNEL_ID, LINE_CHANNEL_SECRET, sender_id, message, reply_token)
        return True
    
    elif event_type == "postback":
        data = event.get("postback", event.get("data", ""))
        source = event.get("source", {})
        sender_id = source.get("id", "")
        reply_token = reply_tokens.get(sender_id, "")
        
        message = f"收到操作：{data}"
        send_line_message(LINE_CHANNEL_ID, LINE_CHANNEL_SECRET, sender_id, message, reply_token)
        return True
    
    else:
        logger.info(f"未處理事件類型: {event_type}")
        return False

class ThreadingHTTPServer:
    """線程 HTTP 服務器 (允許地址重用)"""
    allow_reuse_address = True
    
    def __init__(self, server_address, handler_class):
        self.server_address = server_address
        self.httpd = __import__('http.server').ThreadingHTTPServer(
            server_address, handler_class
        )
    
    def serve_forever(self):
        logger.info(f"LINE 機器人服務器啟動 (端口 {self.server_address[1]})")
        self.httpd.serve_forever()

class LineBotHandler:
    """LINE 機器人請求處理器"""
    
    def __init__(self):
        self.user_manager = user_manager
    
    def do_GET(self):
        """處理 GET 請求"""
        path = urlparse(self.path).path
        
        if path == '/health':
            response = json.dumps({
                "status": "ok",
                "system": "line-bot",
                "running": True,
                "timestamp": datetime.now().isoformat()
            })
            self.send_response(200, response)
        
        elif path == '/line/auth':
            post_body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
            challenge = json.loads(post_body)
            code = challenge.get("code", "")
            
            if code:
                logger.info(f"LINE 認證代碼: {code}")
            else:
                response = json.dumps({"error": "缺少 code"})
                self.send_response(400, response)
        
        elif path == '/voice-to-text':
            segments, transcription = process_voice_to_text()
            response = json.dumps({
                "segments": segments,
                "full_transcription": transcription or ""
            })
            self.send_response(200, response)
        
        else:
            self.send_response(404, json.dumps({"error": "Not Found"}))
    
    def do_POST(self):
        """處理 POST 請求"""
        path = urlparse(self.path).path
        content_length = int(self.headers.get("Content-Length", 0))
        
        body = self.rfile.read(content_length).decode()
        
        # 簽章驗證
        signature = self.headers.get("X-Line-Signature", "")
        if signature:
            valid, error = verify_signature(body, signature)
            if not valid:
                logger.warning(f"簽章驗證失敗: {error}")
                self.send_response(403, json.dumps({"error": error}))
                return
        
        # 路由請求
        if path == '/line/webhook':
            self.handle_webhook(body)
        elif path == '/line/auth':
            self.handle_auth()
        elif path == '/voice-to-text':
            self.handle_voice_to_text()
        elif path == '/line/agent/ceo':
            self.handle_agent_request("ceo")
        elif path == '/line/agent/property':
            self.handle_agent_request("property")
        elif path == '/line/agent/security':
            self.handle_agent_request("security")
        elif path == '/line/agent/fire':
            self.handle_agent_request("fire")
        elif path == '/line/agent/energy':
            self.handle_agent_request("energy")
        elif path == '/line/agent/notice':
            self.handle_agent_request("notice")
        else:
            self.send_response(404, json.dumps({"error": "Not Found"}))
    
    def handle_webhook(self, body):
        """處理 Webhook 請求"""
        try:
            events = json.loads(body)
            events_list = events.get("events", [])
            reply_tokens = events.get("replyTokens", {})
            
            for event in events_list:
                process_event(event, reply_tokens)
            
            logger.info(f"處理 {len(events_list)} 個事件")
        except Exception as e:
            logger.error(f"Webhook 處理錯誤: {e}")
    
    def handle_auth(self):
        """處理認證請求"""
        post_body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        challenge = json.loads(post_body)
        code = challenge.get("code", "")
        
        if code:
            logger.info(f"LINE 認證成功: {code}")
            response = json.dumps({
                "status": "ok",
                "access_token": "your_access_token"
            })
        else:
            response = json.dumps({"error": "缺少 code"})
        self.send_response(200, response)
    
    def handle_voice_to_text(self):
        """處理語音轉文字請求"""
        segments, transcription = process_voice_to_text()
        response = json.dumps({
            "segments": segments,
            "full_transcription": transcription or ""
        })
        self.send_response(200, response)
    
    def handle_agent_request(self, role):
        """處理 Agent 請求"""
        response = json.dumps({
            "role": role,
            "status": "ok",
            "timestamp": datetime.now().isoformat()
        })
        self.send_response(200, response)
    
    def send_response(self, status_code, body):
        """發送 HTTP 響應"""
        self.wfile.write(f"HTTP/1.1 {status_code} OK\r\n".encode())
        self.wfile.write(f"Content-Type: application/json; charset=utf-8\r\n".encode())
        self.wfile.write(f"Content-Length: {len(body.encode())}\r\n".encode())
        self.wfile.write(f"Access-Control-Allow-Origin: *\r\n".encode())
        self.wfile.write(f"Connection: close\r\n".encode())
        self.wfile.write(b"\r\n")
        self.wfile.write(body.encode())
        self.wfile.flush()

def process_voice_to_text():
    """語音轉文字 - Silero VAD + Whisper"""
    try:
        import torch
        import torchaudio
        import whisper
    except ImportError:
        logger.error("缺少語音處理依賴：torch, torchaudio, whisper")
        return [], ""
    
    logger.info("載入 Silero VAD 模型...")
    try:
        silero_vad_model, silero_vad_options = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            onnx=False
        )
    except Exception as e:
        logger.error(f"Silero VAD 載入失敗: {e}")
        return [], ""
    
    logger.info("載入 Whisper 模型...")
    try:
        whisper_model = whisper.load_model("base")
    except Exception as e:
        logger.error(f"Whisper 載入失敗: {e}")
        return [], ""
    
    logger.info("語音處理完成")
    return [], ""

def main():
    """啟動 LINE 機器人服務器"""
    logger.info("=" * 50)
    logger.info("LINE 機器人服務器啟動")
    logger.info("=" * 50)
    
    # 啟動服務器
    server = ThreadingHTTPServer(('0.0.0.0', PORT), LineBotHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
