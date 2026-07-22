#!/usr/bin/env python3
"""LINE 機器人認證模組"""
import json
import hashlib
import hmac
import requests
import logging

logger = logging.getLogger(__name__)

import line_bot_config


def verify_signature(body, signature):
    """驗證 LINE 簽章"""
    try:
        # Body is already decoded JSON from self.rfile.read(content_length).decode()
        # NO NEED to unquote - that would corrupt it!
        post_body = body
        
        if not signature.startswith('t='):
            return False, "簽章格式不正確: 缺少 t="
        
        comma_idx = signature.find(',')
        if comma_idx == -1:
            return False, "簽章格式不正確: 缺少逗號"
        
        hash_part = signature[comma_idx + 1:]
        
        # 計算簽章 - 必須使用 'sha256' 字符串，不能用 hashlib.sha256 類別
        expected_signature = "v0=" + hmac.new(
            line_bot_config.LINE_CHANNEL_SECRET.encode('utf-8'),
            post_body.encode('utf-8'),
            'sha256'
        ).hexdigest()
        
        if expected_signature != hash_part:
            return False, "簽章驗證失敗"
        
        return True, None
    except Exception as e:
        return False, str(e)


def send_message(channel_id, channel_secret, to, message, message_id=None):
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
        response = requests.post(
            f"https://api.line.me/v2/bot/message/push",
            headers=headers,
            json=data
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"LINE API 錯誤: {e}")
        return False
