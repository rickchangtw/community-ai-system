#!/usr/bin/env python3
"""LINE 機器人 Webhook 服務器"""
import json
import os
import sys
import logging
import http.client
import hashlib
import hmac
import urllib.parse
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# ========== 根因修復：避免 tcsetattr 終端組衝突 ==========
# Hermes 終端環境中，fd 1/2 非終端會觸發 tcsetattr() 失敗導致 SIGTERM
# 在 import 之前重定向 stdout/stderr 到檔案
LOG_FILE = "/tmp/line_bot.log"
sys.stdout = open(LOG_FILE, "a", encoding="utf-8")
sys.stderr = open(LOG_FILE, "a", encoding="utf-8")
# ========================================================

logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

# 載入配置
import line_bot_config
import line_bot_auth

# 社區管理系統集成
import psycopg2


class LineBotHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/line/webhook':
            self._handle_webhook()
        elif self.path == '/line/auth':
            self._handle_auth()
        elif self.path == '/health':
            self._handle_health()
        else:
            self._send_json(404, {"error": "not found"})

    def do_GET(self):
        if self.path == '/health':
            self._handle_health()
        else:
            self._send_json(404, {"error": "not found"})

    def _handle_health(self):
        """健康檢查端點"""
        self._send_json(200, {
            "status": "ok",
            "system": "line-bot",
            "running": True
        })

    def _handle_webhook(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        signature = self.headers.get('X-Line-Signature', '')

        # 驗證簽章
        verified, error = line_bot_auth.verify_signature(body, signature)
        if not verified:
            logger.error(f"簽章驗證失敗: {error}")
            self._send_json(400, {"error": "signature verification failed"})
            return

        logger.info("簽章驗證成功")

        # 解析事件
        events = json.loads(body)
        if isinstance(events, list):
            event_list = events
        else:
            event_list = [events]

        # 處理每個事件
        for event in event_list:
            if event.get('type') == 'message':
                self._handle_message(event['message'])
            elif event.get('type') == 'postback':
                self._handle_postback(event['postback'])
            elif event.get('type') == 'event':
                self._handle_event(event['event'])

        self._send_json(200, {"status": "ok"})

    def _handle_message(self, message):
        message_type = message.get('type')
        message_id = message.get('id', '')
        sender_id = message.get('source', {}).get('userId', '')
        text = message.get('text', '')

        logger.info(f"收到訊息: {sender_id} - {text}")

        if message_type == 'text':
            self._handle_text_message(sender_id, text)
        elif message_type == 'image':
            self._handle_image_message(sender_id, message_id)

    def _handle_text_message(self, sender_id, text):
        # 檢查是否為社區用戶
        user = line_bot_config.COMMUNITY_USERS.get(sender_id)

        if not user:
            self._send_reply(sender_id, message_id, {
                "type": "text",
                "text": "🤖 您好！請輸入您的 LINE ID 進行註冊"
            })
            return

        # 處理命令
        if text.startswith('/'):
            self._handle_command(sender_id, text)
        else:
            # 一般訊息 - 回覆確認
            self._send_reply(sender_id, message_id, {
                "type": "text",
                "text": f"👋 收到您的訊息:\n\n{text[:200]}"
            })

    def _handle_command(self, sender_id, text):
        command = text.split()[0].lower()

        if command == '/register':
            self._handle_register(sender_id)
        elif command == '/meeting':
            self._handle_meeting_command(sender_id)
        elif command == '/status':
            self._handle_status_command(sender_id)
        elif command == '/help':
            self._send_reply(sender_id, '', {
                "type": "text",
                "text": "📋 可用指令:\n\n"
                       "  /register - 註冊用戶\n"
                       "  /meeting - 查看會議資訊\n"
                       "  /status - 查看系統狀態\n"
                       "  /help - 顯示幫助"
            })

    def _handle_register(self, sender_id):
        user = line_bot_config.COMMUNITY_USERS.get(sender_id)
        if user:
            self._send_reply(sender_id, '', {
                "type": "text",
                "text": f"✅ 已註冊!\n\n👤 {user['name']}\n🏠 {user['unit']}號\n📱 通知: {user['notification']}"
            })
        else:
            self._send_reply(sender_id, '', {
                "type": "text",
                "text": f"👋 您好!\n\n請輸入您的 LINE ID 進行註冊"
            })

    def _handle_meeting_command(self, sender_id):
        try:
            # 查詢最近的會議
            conn = psycopg2.connect(
                host="localhost", port=5432,
                dbname="community",
                user="hermes", password="hermes123"
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT meeting_id, title, date, time_start, time_end, location
                FROM meetings
                ORDER BY created_at DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            conn.close()

            if row:
                meeting_id, title, date, time_start, time_end, location = row
                self._send_reply(sender_id, '', {
                    "type": "text",
                    "text": f"📋 最近的會議:\n\n"
                           f"{title}\n"
                           f"📅 {date}\n"
                           f"🕐 {time_start} - {time_end}\n"
                           f"📍 {location}"
                })
            else:
                self._send_reply(sender_id, '', {
                    "type": "text",
                    "text": "📋 目前沒有會議記錄"
                })
        except Exception as e:
            logger.error(f"查詢會議失敗: {e}")
            self._send_reply(sender_id, '', {
                "type": "text",
                "text": f"❌ 查詢失敗: {str(e)[:100]}"
            })

    def _handle_status_command(self, sender_id):
        try:
            # 查詢系統狀態
            conn = psycopg2.connect(
                host="localhost", port=5432,
                dbname="community",
                user="hermes", password="hermes123"
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COALESCE(SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END), 0) as scheduled
                FROM meetings
            """)
            row = cursor.fetchone()
            conn.close()

            total, scheduled = row
            self._send_reply(sender_id, '', {
                "type": "text",
                "text": f"📊 系統狀態:\n\n"
                       f"📋 總會議數: {total}\n"
                       f"📅 已排程: {scheduled}"
            })
        except Exception as e:
            logger.error(f"查詢狀態失敗: {e}")
            self._send_reply(sender_id, '', {
                "type": "text",
                "text": f"❌ 查詢失敗: {str(e)[:100]}"
            })

    def _handle_image_message(self, sender_id, message_id):
        self._send_reply(sender_id, message_id, {
            "type": "text",
            "text": "📷 已收到圖片，請稍候處理..."
        })

    def _handle_postback(self, postback):
        self._send_reply('', '', {
            "type": "text",
            "text": f"📋 收到PostBack: {postback.get('data', '')}"
        })

    def _handle_event(self, event):
        event_type = event.get('event', '')

        if event_type == 'follow':
            self._send_reply('', '', {
                "type": "text",
                "text": "👋 歡迎加入社區管理系統！\n請輸入 /help 查看指令"
            })
        elif event_type == 'unfollow':
            logger.info("用戶取消關注")

    def _send_reply(self, sender_id, message_id, text_message):
        try:
            # 呼叫 LINE API 發送回覆
            line_bot_auth.send_message(
                channel_id=line_bot_config.LINE_CHANNEL_ID,
                channel_secret=line_bot_config.LINE_CHANNEL_SECRET,
                to=sender_id,
                message=text_message,
                message_id=message_id
            )
            logger.info(f"已回覆用戶: {sender_id}")
        except Exception as e:
            logger.error(f"發送失敗: {e}")

    def _send_json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    """主函數"""
    logger.info("啟動 LINE 機器人服務器...")
    server = ThreadingHTTPServer(("0.0.0.0", 3021), LineBotHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
