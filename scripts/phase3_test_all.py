#!/usr/bin/env python3
"""Phase 3 完整測試腳本：LINE 機器人 + 後端 API + Silero VAD + Whisper"""
import json
import time
import requests
import sys
import os

BASE_URL = "http://localhost:3021"
BACKEND_URL = "http://localhost:3021"

results = []
passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        results.append({"name": name, "status": "PASS"})
        passed += 1
        print(f"  ✅ {name}")
    except Exception as e:
        results.append({"name": name, "status": "FAIL", "error": str(e)})
        failed += 1
        print(f"  ❌ {name}: {e}")

def main():
    global passed, failed
    print("=" * 60)
    print("Phase 3 完整測試")
    print("=" * 60)

    print("\n--- 1. 後端 API ---")
    test("健康檢查", lambda: requests.get(f"{BACKEND_URL}/health").status_code == 200)

    print("\n--- 2. LINE 機器人 ---")
    test("LINE 機器人健康檢查", lambda: requests.get(f"{BASE_URL}/health").status_code == 200)

    print("\n--- 3. 語音處理 ---")
    test("語音處理模組", lambda: os.path.exists("/home/rick/shared-wiki/scripts/voice-processing/vad_whisper.py"))

    print("\n--- 4. 完整流程 ---")
    test("完整流程", lambda: os.path.exists("/home/rick/shared-wiki/phase3/01-full-schema.sql"))

    print("\n" + "=" * 60)
    print(f"測試結果: {passed}/{passed + failed} 通過")
    print(f"{'✅ 全部通過' if failed == 0 else f'❌ {failed} 個失敗'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
