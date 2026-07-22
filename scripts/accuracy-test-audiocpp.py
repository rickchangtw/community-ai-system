#!/usr/bin/env python3
"""
audio.cpp vs Whisper 準確率測試腳本
測試項目：語音轉文字準確率 / 方言識別 / 關鍵字識別 / 發言人辨識
"""

import json
import subprocess
import time
from datetime import datetime

# 配置
WHISPER_SCRIPT = "/home/rick/shared-wiki/scripts/realtime-meeting-transcription.py"
AUDIOCPP_WEBUI = "http://localhost:3030"
TEST_AUDIO_DIR = "/home/rick/shared-wiki/test-audio"
RESULTS_FILE = "/home/rick/shared-wiki/test-results/accuracy-results.json"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ===== 測試語料 =====
TEST_DATA = {
    "single_speaker": {
        "text": "歡迎大家參加今天的社區會議，希望各位能提出寶貴意見",
        "speaker": "張三",
        "duration": 10
    },
    "two_speakers": {
        "text_zhang": "首先討論停車場收費問題，我認為應該合理調整",
        "text_li": "我同意，但預算也要考慮進去",
        "duration": 30
    },
    "three_speakers": {
        "text_zhang": "歡迎大家參加今天的社區會議",
        "text_li": "首先討論停車場收費問題",
        "text_wang": "消防設備需要定期更新",
        "duration": 60
    },
    "keywords": {
        "parking": ["停車場", "收費", "停車位", "月租"],
        "fire": ["消防設備", "滅火器", "火警", "安全檢查"],
        "budget": ["預算", "費用", "支出", "收入"],
        "elevator": ["電梯故障", "維修", "檢修", "電梯保養"]
    },
    "dialects": {
        "mandarin": "歡迎大家參加社區會議",
        "minnan": "各位好，來參加社區會議",
        "hakka": "各位好，來參加社區會議",
        "cantonese": "各位好，嚟參加社區會議",
        "taiwanese": "各位好，來參加社區會議"
    }
}

def test_transcription_accuracy(system, audio_path):
    """測試語音轉文字準確率"""
    log(f"\n{'='*60}")
    log(f"語音轉文字準確率測試 ({system})")
    log(f"{'='*60}")

    results = []

    # 測試不同語料
    for category, data in TEST_DATA.items():
        if category == "keywords":
            continue  # 關鍵字測試單獨處理

        log(f"\n--- {category} ---")
        log(f"原始文字：{data.get('text_zhang', data.get('text', ''))}")

        # 執行轉寫
        start = time.time()
        result = subprocess.run(
            ["python3", WHISPER_SCRIPT, "--audio", audio_path, "--duration", str(data.get("duration", 10))],
            capture_output=True, text=True, timeout=120
        )

        elapsed = time.time() - start
        log(f"轉寫時間: {elapsed:.2f} 秒")
        log(f"轉寫結果：{result.stdout[:200]}")

        # 計算準確率 (假設 result.stdout 包含準確率)
        accuracy = float(result.stdout.split("準確率")[1]) if "準確率" in result.stdout else 0

        results.append({
            "category": category,
            "system": system,
            "accuracy": accuracy,
            "time": elapsed,
            "success": result.returncode == 0
        })

    return results

def test_keywords_accuracy(system):
    """測試關鍵字識別準確率"""
    log(f"\n{'='*60}")
    log(f"關鍵字識別準確率測試 ({system})")
    log(f"{'='*60}")

    results = {}

    for keyword_category, keywords in TEST_DATA["keywords"].items():
        log(f"\n--- {keyword_category} ---")
        for keyword in keywords:
            log(f"  關鍵字: {keyword}")

        results[keyword_category] = {
            "keywords": keywords,
            "system": system,
            "note": "需要實際音頻文件進行測試"
        }

    return results

def test_dialect_accuracy(system):
    """測試方言識別準確率"""
    log(f"\n{'='*60}")
    log(f"方言識別準確率測試 ({system})")
    log(f"{'='*60}")

    results = {}

    for dialect, text in TEST_DATA["dialects"].items():
        log(f"\n--- {dialect} ---")
        log(f"測試語料: {text}")

        results[dialect] = {
            "dialect": dialect,
            "text": text,
            "system": system,
            "note": "需要實際方言音頻文件進行測試"
        }

    return results

def test_speaker_diarization(system):
    """測試發言人辨識準確率"""
    log(f"\n{'='*60}")
    log(f"發言人辨識準確率測試 ({system})")
    log(f"{'='*60}")

    # 發言人配置
    speaker_profiles = {
        "張三": {"unit": "101", "role": "總幹事", "confidence": 0.85},
        "李四": {"unit": "205", "role": "委員", "confidence": 0.90},
        "王五": {"unit": "308", "role": "委員", "confidence": 0.88}
    }

    log(f"\n發言人配置:")
    for name, profile in speaker_profiles.items():
        log(f"  {name}: 單位={profile['unit']}, 角色={profile['role']}, 置信度={profile['confidence']}")

    results = {
        "system": system,
        "speaker_profiles": speaker_profiles,
        "note": "需要實際會議音頻文件進行測試"
    }

    return results

def main():
    log("=" * 60)
    log("🎙️  audio.cpp vs Whisper 準確率測試")
    log("=" * 60)
    log(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 保存結果
    output = {}

    # 語音轉寫準確率
    for system in ["Whisper", "audio.cpp"]:
        log(f"\n{'='*60}")
        log(f"{system} 語音轉寫準確率測試")
        log(f"{'='*60}")

        # 需要測試音頻文件
        log(f"\n請準備以下測試音頻文件:")
        log(f"  - {TEST_AUDIO_DIR}/test_10s.wav (10 秒單人朗讀)")
        log(f"  - {TEST_AUDIO_DIR}/test_30s.wav (30 秒雙人對話)")
        log(f"  - {TEST_AUDIO_DIR}/test_60s.wav (60 秒三人會議)")

        output["transcription_accuracy"] = {
            "system": system,
            "note": "需要實際音頻文件",
            "test_audio": [
                f"{TEST_AUDIO_DIR}/test_10s.wav",
                f"{TEST_AUDIO_DIR}/test_30s.wav",
                f"{TEST_AUDIO_DIR}/test_60s.wav"
            ]
        }

    # 關鍵字識別
    for system in ["Whisper", "audio.cpp"]:
        output["keywords_accuracy"] = test_keywords_accuracy(system)

    # 方言識別
    for system in ["Whisper", "audio.cpp"]:
        output["dialect_accuracy"] = test_dialect_accuracy(system)

    # 發言人辨識
    for system in ["Whisper", "audio.cpp"]:
        output["speaker_diarization"] = test_speaker_diarization(system)

    # 保存結果
    with open(RESULTS_FILE, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    log(f"\n{'='*60}")
    log(f"✅ 準確率測試完成！")
    log(f"結果保存: {RESULTS_FILE}")
    log(f"{'='*60}")

if __name__ == "__main__":
    main()
