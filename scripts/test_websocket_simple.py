#!/usr/bin/env python3
"""
WebSocket 即時轉錄測試腳本
"""

import asyncio
import websockets
import json
import numpy as np

WS_URL = "ws://localhost:3020/ws/transcription"

async def main():
    print("=" * 60)
    print("🧪 WebSocket 即時轉錄系統測試")
    print("=" * 60)
    
    # 連接 WebSocket
    print("\n🔗 連接 WebSocket...")
    try:
        ws = await websockets.connect(WS_URL)
        print("✅ WebSocket 連接成功")
    except Exception as e:
        print(f"❌ WebSocket 連接失敗：{e}")
        return
    
    # 開始會議
    print("\n📋 開始會議...")
    await ws.send(json.dumps({"type": "control", "action": "start-meeting", "meeting_id": "MEET-2026-07-16"}))
    resp = await asyncio.wait_for(ws.recv(), timeout=5)
    print(f"   回應：{resp}")
    
    # 發送測試音頻
    print("\n🎙️  發送測試音頻...")
    test_audio = np.random.randn(16000).astype(np.float32)
    await ws.send(json.dumps({"type": "audio_chunk", "audio_data": test_audio.tobytes(), "sample_rate": 16000}))
    
    # 等待轉錄結果
    print("   等待轉錄結果...")
    try:
        msg = await asyncio.wait_for(ws.recv(), timeout=10)
        data = json.loads(msg)
        print(f"✅ 收到轉錄消息：{data.get('type')}, speaker: {data.get('speaker')}")
        print(f"   文字：{data.get('text', 'N/A')}")
    except asyncio.TimeoutError:
        print("   ⚠️  等待超過 10 秒，沒有收到轉錄結果")
    
    # 發言人辨識
    print("\n👤 測試發言人辨識...")
    await ws.send(json.dumps({"type": "control", "action": "identify-speaker", "transcription": "討論社區預算問題"}))
    print("   發言人辨識發送完成")
    
    # 結束會議
    print("\n🏁 結束會議...")
    await ws.send(json.dumps({"type": "control", "action": "end-meeting"}))
    resp = await asyncio.wait_for(ws.recv(), timeout=5)
    print(f"   回應：{resp}")
    
    await ws.close()
    print("\n✅ 測試完成")


if __name__ == "__main__":
    asyncio.run(main())
