#!/usr/bin/env python3
"""LINE 機器人完整整合測試 - 模擬完整社區管理流程"""
import json
import http.client
import hashlib
import hmac
import urllib.parse
import time

# 載入配置
import line_bot_config
import line_bot_auth

def generate_signature(body):
    """生成有效的 LINE 簽章"""
    post_body = urllib.parse.unquote(body)
    timestamp = str(int(time.time()))
    signature = f"t={timestamp},v0={hmac.new(
        line_bot_config.LINE_CHANNEL_SECRET.encode('utf-8'),
        post_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()}"
    return signature

def send_request(data, signature=None):
    """發送 LINE Webhook 請求"""
    if signature is None:
        signature = generate_signature(json.dumps(data))
    
    try:
        conn = http.client.HTTPConnection("localhost", 3021)
        headers = {
            "Content-Type": "application/json",
            "X-Line-Signature": signature
        }
        conn.request("POST", "/line/webhook", json.dumps(data), headers)
        response = conn.getresponse()
        body = response.read().decode()
        conn.close()
        return response.status, body
    except Exception as e:
        return None, str(e)

def simulate_complete_workflow():
    """模擬完整社區管理流程"""
    print("=== 模擬完整社區管理流程 ===\n")
    
    # 步驟 1: 用戶註冊
    print("--- 步驟 1: 用戶註冊 ---")
    data = {"events": [{"type": "message", "message": {"type": "text", "text": "/register"}}], "source": {"userId": "Uresident_001"}}
    status, body = send_request(data)
    print(f"狀態: {status}")
    print(f"回應: {body[:200]}")
    print()
    
    # 步驟 2: 查看會議資訊
    print("--- 步驟 2: 查看會議資訊 ---")
    data = {"events": [{"type": "message", "message": {"type": "text", "text": "/meeting"}}], "source": {"userId": "Uresident_001"}}
    status, body = send_request(data)
    print(f"狀態: {status}")
    print(f"回應: {body[:200]}")
    print()
    
    # 步驟 3: 系統狀態查詢
    print("--- 步驟 3: 系統狀態查詢 ---")
    data = {"events": [{"type": "message", "message": {"type": "text", "text": "/status"}}], "source": {"userId": "Uresident_001"}}
    status, body = send_request(data)
    print(f"狀態: {status}")
    print(f"回應: {body[:200]}")
    print()
    
    # 步驟 4: 一般訊息回覆
    print("--- 步驟 4: 一般訊息回覆 ---")
    data = {"events": [{"type": "message", "message": {"type": "text", "text": "你好，有什麼事嗎？"}}], "source": {"userId": "Uresident_001"}}
    status, body = send_request(data)
    print(f"狀態: {status}")
    print(f"回應: {body[:200]}")
    print()
    
    # 步驟 5: 非註冊用戶測試
    print("--- 步驟 5: 非註冊用戶測試 ---")
    data = {"events": [{"type": "message", "message": {"type": "text", "text": "Hello"}}], "source": {"userId": "Uunknown_user"}}
    status, body = send_request(data)
    print(f"狀態: {status}")
    print(f"回應: {body[:200]}")
    print()
    
    # 步驟 6: 追蹤事件測試
    print("--- 步驟 6: 追蹤事件測試 ---")
    data = {"events": [{"type": "event", "event": {"type": "follow", "userId": "Unew_user"}}], "source": {"userId": "Unew_user"}}
    status, body = send_request(data)
    print(f"狀態: {status}")
    print(f"回應: {body[:200]}")
    print()
    
    # 步驟 7: 健康檢查
    print("--- 步驟 7: 健康檢查 ---")
    try:
        conn = http.client.HTTPConnection("localhost", 3021)
        conn.request("GET", "/health")
        response = conn.getresponse()
        body = response.read().decode()
        conn.close()
        print(f"健康檢查狀態: {response.status}")
        print(f"回應: {body}")
    except Exception as e:
        print(f"健康檢查失敗: {e}")
    print()
    
    print("=== 完整流程測試完成 ===")

if __name__ == "__main__":
    simulate_complete_workflow()
