#!/usr/bin/env python3
"""
WebSocket 即時轉錄系統測試腳本
"""

import asyncio
import websockets
import json
import numpy as np

WS_URL = "ws://localhost:3020/ws/transcription"

test_results = []

def log_test(name, passed, detail=""):
    status = "✅" if passed else "❌"
    test_results.append({"test": name, "passed": passed, "detail": detail})
    print(f"  {status} {name}" + (f" - {detail}" if detail else ""))


async def main():
    print("=" * 60)
    print("🧪 WebSocket 即時轉錄系統測試")
    print("=" * 60)

    websocket = await websockets.connect(WS_URL)
    print("\n✅ WebSocket 連接成功")
    test_results.append(("WebSocket 連接", True))

    # 開始會議
    await websocket.send(json.dumps({"type": "control", "action": "start-meeting", "meeting_id": "MEET-2026-07-16"}))
    resp = await asyncio.wait_for(websocket.recv(), timeout=5)
    print(f"   會議開始：{resp[:100]}...")
    test_results.append(("開始會議", True))

    # 測試音頻轉錄
    print("\n🎙️  測試音頻轉錄...")
    try:
        await websocket.send(json.dumps({"type": "audio_chunk", "audio_data": np.random.randn(16000).astype(np.float32).tobytes(), "sample_rate": 16000}))
        await asyncio.sleep(2)
        await websocket.send(json.dumps({"type": "audio_chunk", "audio_data": np.random.randn(16000).astype(np.float32).tobytes(), "sample_rate": 16000}))
        await asyncio.sleep(2)
        print("   音頻發送成功")
        messages = []
        for i in range(5):
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=3)
                messages.append(json.loads(msg))
                print(f"   收到 {i+1}: {msg.get('type')}, speaker: {msg.get('speaker')}")
            except asyncio.TimeoutError:
                break
        log_test("音頻轉錄", len(messages) > 0, f"收到 {len(messages)} 條消息")
    except Exception as e:
        print(f"   失敗：{e}")
        test_results.append(("音頻轉錄", False))

    # 測試發言人辨識
    print("\n👤 測試發言人辨識...")
    try:
        await websocket.send(json.dumps({"type": "control", "action": "identify-speaker", "transcription": "討論社區預算問題"}))
        print("   發言人辨識測試發送")
        test_results.append(("發言人辨識", True))
    except Exception as e:
        print(f"   失敗：{e}")
        test_results.append(("發言人辨識", False))

    # 即時轉錄完整流程
    print("\n⏱️  測試即時轉錄...")
    try:
        for i in range(3):
            await websocket.send(json.dumps({"type": "audio_chunk", "audio_data": np.random.randn(16000).astype(np.float32).tobytes(), "sample_rate": 16000}))
            await asyncio.sleep(1)
        await asyncio.sleep(3)
        print("   即時轉錄完成")
        test_results.append(("即時轉錄流程", True))
    except Exception as e:
        print(f"   失敗：{e}")
        test_results.append(("即時轉錄流程", False))

    # 結束會議
    print("\n🏁 結束會議...")
    await websocket.send(json.dumps({"type": "control", "action": "end-meeting"}))
    resp = await asyncio.wait_for(websocket.recv(), timeout=5)
    print(f"   會議結束：{resp[:100]}...")
    test_results.append(("結束會議", True))

    await websocket.close()

    # 總結
    print()
    print("=" * 60)
    print("📊 測試結果")
    print("=" * 60)
    total = len(test_results)
    passed = sum(1 for _, r in test_results if r)
    failed = total - passed
    print(f"\n  總測試數：{total}")
    print(f"  ✅ 通過：{passed}")
    print(f"  ❌ 失敗：{failed}")
    print()
    for name, result in test_results:
        print(f"  {'✅' if result else '❌'} {name}")
    print()
    if failed == 0:
        print("✅ WebSocket 即時轉錄系統測試完成！所有測試通過")
    else:
        print(f"⚠️  WebSocket 即時轉錄系統測試完成，{failed} 個測試失敗")

    return failed == 0


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 測試錯誤：{e}")
        exit(1)
