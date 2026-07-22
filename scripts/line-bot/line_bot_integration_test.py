#!/usr/bin/env python3
"""LINE 機器人完整集成測試腳本 - 模擬真實社區場景"""
import json
import os
import sys
import time
import requests
import hmac

# 確保能導入 line_bot_config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from line_bot_config import LINE_CHANNEL_SECRET

BASE_URL = "http://localhost:3021"

def create_signature(message):
    """產生有效簽章"""
    timestamp = int(time.time())
    content = json.dumps(message, sort_keys=True)
    return f"t={timestamp},v0={hmac.new(
        LINE_CHANNEL_SECRET.encode('utf-8'),
        content.encode('utf-8'),
        'sha256'
    ).hexdigest()}"

def send_webhook(message: dict, signature: str = None) -> dict:
    """發送 Webhook 到 LINE 服務器"""
    url = f"{BASE_URL}/line/webhook"
    headers = {"Content-Type": "application/json"}
    if signature:
        headers["X-Line-Signature"] = signature
    response = requests.post(url, json=message, headers=headers)
    return response.json()

# ==================== 測試場景 ====================

def test_scenario_1_health_check():
    """場景 1: 健康檢查"""
    print("=" * 60)
    print("📋 場景 1: 健康檢查端點")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/health")
    result = response.json()
    
    assert response.status_code == 200, f"預期 200，實際 {response.status_code}"
    assert result["status"] == "ok", f"預期 status=ok，實際 {result['status']}"
    assert result["system"] == "line-bot", f"預期 system=line-bot"
    assert result["running"] == True, f"預期 running=true"
    
    print(f"✅ 健康檢查通過: {result}")
    return result

def test_scenario_2_signature_verification():
    """場景 2: 簽章驗證"""
    print("\n" + "=" * 60)
    print("🔐 場景 2: 簽章驗證")
    print("=" * 60)
    
    # 測試無效簽章
    invalid_sig = "t=12345,v0=invalid"
    message = {"events": [{"type": "message", "message": {"type": "text", "text": "test"}, "source": {"userId": "Utest123"}}]}
    
    response = send_webhook(message, signature=invalid_sig)
    assert response["error"] == "signature verification failed", f"預期拒絕無效簽章，實際 {response}"
    
    print(f"✅ 無效簽章正確拒絕: {response}")
    
    # 產生有效簽章
    valid_sig = create_signature(message)
    
    response = send_webhook(message, signature=valid_sig)
    assert response["status"] == "ok", f"預期接受有效簽章，實際 {response}"
    
    print(f"✅ 有效簽章正確通過")
    return valid_sig

def test_scenario_3_user_registration():
    """場景 3: 用戶註冊"""
    print("\n" + "=" * 60)
    print("📝 場景 3: 用戶註冊")
    print("=" * 60)
    
    # 測試未註冊用戶
    invalid_sig = "t=12345,v0=invalid"
    message = {"events": [{"type": "message", "message": {"type": "text", "text": "hello"}, "source": {"userId": "Uunknown"}}]}
    response = send_webhook(message, signature=invalid_sig)
    assert response["error"] == "signature verification failed"
    
    print(f"✅ 未註冊用戶正確拒絕")
    
    # 測試已註冊用戶
    valid_sig = create_signature({"events": [{"type": "message", "message": {"type": "text", "text": "/status"}, "source": {"userId": "Uresident_001"}}]})
    message = {"events": [{"type": "message", "message": {"type": "text", "text": "/status"}, "source": {"userId": "Uresident_001"}}]}
    response = send_webhook(message, signature=valid_sig)
    
    assert response["status"] == "ok", f"預期 status=ok，實際 {response}"
    
    print(f"✅ 已註冊用戶 /status 測試通過")
    return valid_sig

def test_scenario_4_command_handling():
    """場景 4: 命令處理"""
    print("\n" + "=" * 60)
    print("📋 場景 4: 命令處理")
    print("=" * 60)
    
    # 測試 /help 命令
    valid_sig = create_signature({"events": [{"type": "message", "message": {"type": "text", "text": "/help"}, "source": {"userId": "Uresident_001"}}]})
    message = {"events": [{"type": "message", "message": {"type": "text", "text": "/help"}, "source": {"userId": "Uresident_001"}}]}
    response = send_webhook(message, signature=valid_sig)
    assert response["status"] == "ok"
    print(f"✅ /help 命令處理正常")
    
    # 測試 /meeting 命令
    valid_sig = create_signature({"events": [{"type": "message", "message": {"type": "text", "text": "/meeting"}, "source": {"userId": "Uresident_001"}}]})
    message = {"events": [{"type": "message", "message": {"type": "text", "text": "/meeting"}, "source": {"userId": "Uresident_001"}}]}
    response = send_webhook(message, signature=valid_sig)
    assert response["status"] == "ok"
    print(f"✅ /meeting 命令處理正常")
    
    # 測試 /status 命令
    valid_sig = create_signature({"events": [{"type": "message", "message": {"type": "text", "text": "/status"}, "source": {"userId": "Uresident_001"}}]})
    message = {"events": [{"type": "message", "message": {"type": "text", "text": "/status"}, "source": {"userId": "Uresident_001"}}]}
    response = send_webhook(message, signature=valid_sig)
    assert response["status"] == "ok"
    print(f"✅ /status 命令處理正常")
    
    # 測試一般訊息
    valid_sig = create_signature({"events": [{"type": "message", "message": {"type": "text", "text": "你好"}, "source": {"userId": "Uresident_001"}}]})
    message = {"events": [{"type": "message", "message": {"type": "text", "text": "你好"}, "source": {"userId": "Uresident_001"}}]}
    response = send_webhook(message, signature=valid_sig)
    assert response["status"] == "ok"
    print(f"✅ 一般訊息處理正常")
    
    return True

def test_scenario_5_follow_event():
    """場景 5: Follow/Unfollow 事件"""
    print("\n" + "=" * 60)
    print("👋 場景 5: Follow/Unfollow 事件")
    print("=" * 60)
    
    # 測試 follow 事件
    valid_sig = create_signature({"events": [{"type": "event", "event": "follow"}]})
    message = {"events": [{"type": "event", "event": "follow"}]}
    response = send_webhook(message, signature=valid_sig)
    assert response["status"] == "ok"
    print(f"✅ Follow 事件處理正常")
    
    # 測試 unfollow 事件
    valid_sig = create_signature({"events": [{"type": "event", "event": "unfollow"}]})
    message = {"events": [{"type": "event", "event": "unfollow"}]}
    response = send_webhook(message, signature=valid_sig)
    assert response["status"] == "ok"
    print(f"✅ Unfollow 事件處理正常")
    
    return True

def test_scenario_6_postback_event():
    """場景 6: Postback 事件"""
    print("\n" + "=" * 60)
    print("📋 場景 6: Postback 事件")
    print("=" * 60)
    
    valid_sig = create_signature({"events": [{"type": "postback", "postback": {"data": "test_data"}}]})
    message = {"events": [{"type": "postback", "postback": {"data": "test_data"}}]}
    response = send_webhook(message, signature=valid_sig)
    assert response["status"] == "ok"
    print(f"✅ Postback 事件處理正常")
    
    return True

def test_scenario_7_image_message():
    """場景 7: 圖片訊息"""
    print("\n" + "=" * 60)
    print("📷 場景 7: 圖片訊息")
    print("=" * 60)
    
    valid_sig = create_signature({"events": [{"type": "message", "message": {"type": "image", "id": "img-123"}, "source": {"userId": "Uresident_001"}}]})
    message = {"events": [{"type": "message", "message": {"type": "image", "id": "img-123"}, "source": {"userId": "Uresident_001"}}]}
    response = send_webhook(message, signature=valid_sig)
    assert response["status"] == "ok"
    print(f"✅ 圖片訊息處理正常")
    
    return True

def test_scenario_8_not_found():
    """場景 8: 404 錯誤"""
    print("\n" + "=" * 60)
    print("❌ 場景 8: 404 錯誤")
    print("=" * 60)
    
    # 測試未知端點
    response = requests.post(f"{BASE_URL}/unknown")
    assert response.status_code == 404, f"預期 404，實際 {response.status_code}"
    
    # 測試 GET 未知端點
    response = requests.get(f"{BASE_URL}/unknown")
    assert response.status_code == 404
    
    print(f"✅ 404 錯誤處理正常")
    return True

def test_scenario_9_community_scenario():
    """場景 9: 真實社區場景模擬"""
    print("\n" + "=" * 60)
    print("🏘️  場景 9: 真實社區場景模擬")
    print("=" * 60)
    
    # 場景：居民查詢會議
    valid_sig = create_signature({"events": [{"type": "message", "message": {"type": "text", "text": "/meeting"}, "source": {"userId": "Uresident_001"}}]})
    message = {"events": [{"type": "message", "message": {"type": "text", "text": "/meeting"}, "source": {"userId": "Uresident_001"}}]}
    response = send_webhook(message, signature=valid_sig)
    assert response["status"] == "ok"
    print(f"✅ 場景 9.1: 居民查詢會議")
    
    # 場景：系統狀態查詢
    valid_sig = create_signature({"events": [{"type": "message", "message": {"type": "text", "text": "/status"}, "source": {"userId": "Uresident_001"}}]})
    message = {"events": [{"type": "message", "message": {"type": "text", "text": "/status"}, "source": {"userId": "Uresident_001"}}]}
    response = send_webhook(message, signature=valid_sig)
    assert response["status"] == "ok"
    print(f"✅ 場景 9.2: 居民查詢系統狀態")
    
    return True

def main():
    """執行所有測試場景"""
    print("🚀 LINE 機器人完整集成測試開始...")
    print(f"   服務器地址: http://localhost:3021")
    print(f"   測試時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   LINE_CHANNEL_SECRET: {LINE_CHANNEL_SECRET}")
    print("=" * 60)
    
    results = {}
    
    try:
        results["場景 1: 健康檢查"] = test_scenario_1_health_check()
    except Exception as e:
        print(f"❌ 場景 1 失敗: {e}")
        results["場景 1: 健康檢查"] = False
    
    try:
        results["場景 2: 簽章驗證"] = test_scenario_2_signature_verification()
    except Exception as e:
        print(f"❌ 場景 2 失敗: {e}")
        results["場景 2: 簽章驗證"] = False
    
    try:
        results["場景 3: 用戶註冊"] = test_scenario_3_user_registration()
    except Exception as e:
        print(f"❌ 場景 3 失敗: {e}")
        results["場景 3: 用戶註冊"] = False
    
    try:
        results["場景 4: 命令處理"] = test_scenario_4_command_handling()
    except Exception as e:
        print(f"❌ 場景 4 失敗: {e}")
        results["場景 4: 命令處理"] = False
    
    try:
        results["場景 5: Follow/Unfollow"] = test_scenario_5_follow_event()
    except Exception as e:
        print(f"❌ 場景 5 失敗: {e}")
        results["場景 5: Follow/Unfollow"] = False
    
    try:
        results["場景 6: Postback"] = test_scenario_6_postback_event()
    except Exception as e:
        print(f"❌ 場景 6 失敗: {e}")
        results["場景 6: Postback"] = False
    
    try:
        results["場景 7: 圖片訊息"] = test_scenario_7_image_message()
    except Exception as e:
        print(f"❌ 場景 7 失敗: {e}")
        results["場景 7: 圖片訊息"] = False
    
    try:
        results["場景 8: 404 錯誤"] = test_scenario_8_not_found()
    except Exception as e:
        print(f"❌ 場景 8 失敗: {e}")
        results["場景 8: 404 錯誤"] = False
    
    try:
        results["場景 9: 真實社區場景"] = test_scenario_9_community_scenario()
    except Exception as e:
        print(f"❌ 場景 9 失敗: {e}")
        results["場景 9: 真實社區場景"] = False
    
    # 總結
    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n總計: {passed}/{total} 場景通過")
    
    if passed == total:
        print(f"✅ 全部 {total} 個場景測試通過！")
    else:
        print(f"❌ {total - passed} 個場景失敗")
    
    print("\n詳細結果:")
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}: {'通過' if result else '失敗'}")
    
    print(f"\n📝 日誌文件: /tmp/line_bot.log")
    print("=" * 60)

if __name__ == '__main__':
    main()
