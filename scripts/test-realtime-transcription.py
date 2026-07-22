#!/usr/bin/env python3
"""
即時轉錄系統測試腳本
測試 FastAPI WebSocket 服務
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path
import numpy as np
import torch
import os

# 測試配置
BASE_URL = "http://localhost:3020"
API_URL = f"{BASE_URL}/api"
WS_URL = f"ws://localhost:3020/ws/transcription"

# 測試結果
test_results = []

def log_test(name, passed, detail=""):
    """記錄測試結果"""
    status = "✅" if passed else "❌"
    result = {"test": name, "passed": passed, "detail": detail}
    test_results.append(result)
    print(f"{status} {name}" + (f" - {detail}" if detail else ""))

async def test_health_endpoint():
    """測試健康檢查端點"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/health")
            data = response.json()
            
            log_test("健康檢查端點", 
                     response.status_code == 200 and data["status"] == "ok",
                     f"status: {data.get('status')}, running: {data.get('running')}")
    except Exception as e:
        log_test("健康檢查端點", False, str(e))

async def test_status_endpoint():
    """測試系統狀態端點"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/status")
            data = response.json()
            
            log_test("系統狀態端點",
                     response.status_code == 200 and "meeting_id" in data,
                     f"meeting_id: {data.get('meeting_id')}, speakers: {data.get('speakers', [])}")
    except Exception as e:
        log_test("系統狀態端點", False, str(e))

async def test_start_meeting():
    """測試開始會議端點"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/start-meeting",
                json={"meeting_id": "MEET-2026-07-16"}
            )
            data = response.json()
            
            log_test("開始會議端點",
                     response.status_code == 200 and data.get("meeting_id") == "MEET-2026-07-16",
                     f"status: {data.get('status')}, meeting_id: {data.get('meeting_id')}")
    except Exception as e:
        log_test("開始會議端點", False, str(e))

async def test_end_meeting():
    """測試結束會議端點"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/end-meeting")
            data = response.json()
            
            log_test("結束會議端點",
                     response.status_code == 200 and data.get("status") == "ok",
                     f"status: {data.get('status')}, meeting_id: {data.get('meeting_id')}")
    except Exception as e:
        log_test("結束會議端點", False, str(e))

async def test_audio_transcription():
    """測試音頻轉錄"""
    try:
        from realtime_meeting_transcription import whisper_transcribe
        
        # 創建測試音頻（16kHz, 1秒）
        test_audio = np.random.randn(16000).astype(np.float32)
        transcription = whisper_transcribe(test_audio)
        
        log_test("音頻轉錄",
                 isinstance(transcription, str),
                     f"transcription: '{transcription[:50]}...'")
    except Exception as e:
        log_test("音頻轉錄", False, str(e))

async def test_speaker_identification():
    """測試發言人辨識"""
    try:
        from realtime_meeting_transcription import identify_speaker
        
        # 測試張三的關鍵字
        result = identify_speaker("討論社區預算問題")
        
        log_test("發言人辨識",
                 result.get("name") == "張三",
                     f"name: {result.get('name')}, confidence: {result.get('confidence')}")
    except Exception as e:
        log_test("發言人辨識", False, str(e))

async def test_silero_vad():
    """測試 Silero VAD 新 API"""
    try:
        from silero_vad import load_silero_vad
        
        # 載入 VAD 模型
        vad_model = load_silero_vad()
        
        # 創建測試音頻（512 sample = 16000Hz）
        test_audio = np.random.randn(512).astype(np.float32)
        test_tensor = torch.from_numpy(test_audio)
        
        # 新 API: forward(x, sr)
        result = vad_model(test_tensor, sr=16000)
        
        log_test("Silero VAD",
                 isinstance(result, torch.Tensor),
                     f"result type: {type(result)}, shape: {result.shape}")
    except Exception as e:
        log_test("Silero VAD", False, str(e))

async def main():
    """主測試函數"""
    print("=" * 60)
    print("🧪 即時轉錄系統測試")
    print("=" * 60)
    print()
    
    # 執行測試
    print("🔗 測試端點連接...")
    await test_health_endpoint()
    await test_status_endpoint()
    await test_start_meeting()
    await test_end_meeting()
    
    print()
    print("🎙️  測試轉錄功能...")
    await test_audio_transcription()
    await test_speaker_identification()
    await test_silero_vad()
    
    # 總結
    print()
    print("=" * 60)
    print("📊 測試結果")
    print("=" * 60)
    
    total = len(test_results)
    passed = sum(1 for r in test_results if r["passed"])
    failed = total - passed
    
    print(f"\n  總測試數: {total}")
    print(f"  ✅ 通過: {passed}")
    print(f"  ❌ 失敗: {failed}")
    
    print()
    print("詳細結果:")
    for result in test_results:
        status = "✅" if result["passed"] else "❌"
        print(f"  {status} {result['test']}: {result.get('detail', '')}")
    
    print()
    
    if failed == 0:
        print("✅ 即時轉錄系統測試完成！所有測試通過")
    else:
        print(f"⚠️  即時轉錄系統測試完成，{failed} 個測試失敗")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except ImportError as e:
        print(f"❌ 缺少依賴: {e}")
        print("   請安裝: pip install httpx")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 測試錯誤: {e}")
        sys.exit(1)
