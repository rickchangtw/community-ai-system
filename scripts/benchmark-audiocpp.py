#!/usr/bin/env python3
"""
audio.cpp vs Whisper 性能Benchmark測試腳本
測試項目：啟動時間 / 推理速度 / CPU / 記憶體 / 準確率
"""

import time
import json
import subprocess
import psutil
import os
from datetime import datetime

# 配置
AUDIOCPP_URL = "https://github.com/kigner/audio.cpp-webui.git"
AUDIOCPP_REPO = "/home/rick/audio.cpp"
AUDIOCPP_BINARY = "/home/rick/audio.cpp/build/audio.cpp"
AUDIOCPP_SERVER_PORT = 3030
WHISPER_SCRIPT = "/home/rick/shared-wiki/scripts/realtime-meeting-transcription.py"
AUDIOCPP_WEBUI = f"http://localhost:{AUDIOCPP_SERVER_PORT}"

# 測試音頻路徑
TEST_AUDIO_DIR = "/home/rick/shared-wiki/test-audio"
BENCHMARK_RESULTS = "/home/rick/shared-wiki/test-results/benchmark-results.json"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    mem = psutil.virtual_memory()
    return {
        "total": mem.total / 1024**2,
        "used": mem.used / 1024**2,
        "percent": mem.percent
    }

def get_gpu_usage():
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
        gpu_util = pynvml.nvmlDeviceGetUtilizationRates()
        return {
            "memory_used": gpu_mem.used / 1024**2,
            "memory_total": gpu_mem.total / 1024**2,
            "utilization": gpu_util.gpu
        }
    except Exception as e:
        return {"error": str(e)}

# ===== 1. 啟動時間測試 =====
def test_startup_time(system, binary=None):
    """測試啟動時間"""
    log(f"\n{'='*60}")
    log(f"1. 啟動時間測試 ({system})")
    log(f"{'='*60}")

    start_time = time.time()
    if binary:
        result = subprocess.run([binary], capture_output=True, text=True)
    else:
        result = subprocess.run(
            ["python3", WHISPER_SCRIPT],
            capture_output=True, text=True
        )

    elapsed = time.time() - start_time
    log(f"啟動時間: {elapsed:.2f} 秒")
    log(f"退出碼: {result.returncode}")
    log(f"輸出: {result.stdout[:200]}")

    return {
        "system": system,
        "start_time": elapsed,
        "exit_code": result.returncode,
        "output": result.stdout[:500]
    }

# ===== 2. 推理速度測試 =====
def test_inference_speed(system, audio_path):
    """測試推理速度"""
    log(f"\n{'='*60}")
    log(f"2. 推理速度測試 ({system})")
    log(f"{'='*60}")

    results = []

    # 10 秒音頻
    log(f"\n--- 10 秒音頻 ---")
    start = time.time()
    result = subprocess.run(
        ["python3", WHISPER_SCRIPT, "--audio", audio_path, "--duration", "10"],
        capture_output=True, text=True, timeout=120
    )
    elapsed = time.time() - start
    log(f"10 秒轉寫時間: {elapsed:.2f} 秒")
    log(f"轉寫結果: {result.stdout[:200]}")
    results.append({
        "duration": 10,
        "time": elapsed,
        "words_per_second": 10 / elapsed if elapsed > 0 else 0,
        "success": result.returncode == 0
    })

    # 30 秒音頻
    log(f"\n--- 30 秒音頻 ---")
    start = time.time()
    result = subprocess.run(
        ["python3", WHISPER_SCRIPT, "--audio", audio_path, "--duration", "30"],
        capture_output=True, text=True, timeout=300
    )
    elapsed = time.time() - start
    log(f"30 秒轉寫時間: {elapsed:.2f} 秒")
    log(f"轉寫結果: {result.stdout[:200]}")
    results.append({
        "duration": 30,
        "time": elapsed,
        "words_per_second": 30 / elapsed if elapsed > 0 else 0,
        "success": result.returncode == 0
    })

    return results

# ===== 3. 資源占用測試 =====
def test_resource_usage(system, binary=None):
    """測試 CPU / 記憶體 / GPU 占用"""
    log(f"\n{'='*60}")
    log(f"3. 資源占用測試 ({system})")
    log(f"{'='*60}")

    results = []
    start = time.time()

    # 啟動服務
    if binary:
        proc = subprocess.Popen([binary], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        proc = subprocess.Popen(
            ["python3", WHISPER_SCRIPT],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    # 等待啟動
    time.sleep(5)

    # 持續監控 30 秒
    for i in range(6):  # 每 5 秒一次
        cpu = get_cpu_usage()
        mem = get_memory_usage()
        gpu = get_gpu_usage()

        log(f"監控 {i+1}/6: CPU={cpu}% | Memory={mem['used']:.0f}MB/{mem['total']:.0f}MB ({mem['percent']}%) | GPU={gpu}")
        results.append({
            "cpu": cpu,
            "memory": mem,
            "gpu": gpu,
            "timestamp": time.time() - start
        })

        time.sleep(5)

    # 結束服務
    proc.terminate()
    proc.wait()

    # 統計
    avg_cpu = sum(r["cpu"] for r in results) / len(results)
    max_mem = max(r["memory"]["used"] for r in results)
    avg_mem = sum(r["memory"]["used"] for r in results) / len(results)

    log(f"\n平均 CPU: {avg_cpu:.1f}%")
    log(f"最大記憶體: {max_mem:.0f}MB")
    log(f"平均記憶體: {avg_mem:.0f}MB")

    return {
        "system": system,
        "avg_cpu": avg_cpu,
        "max_memory": max_mem,
        "avg_memory": avg_mem,
        "samples": results
    }

# ===== 4. 準確率測試 =====
def test_accuracy(system, audio_path):
    """測試語音轉文字準確率"""
    log(f"\n{'='*60}")
    log(f"4. 準確率測試 ({system})")
    log(f"{'='*60}")

    # 測試語料
    test_texts = [
        "歡迎大家參加今天的社區會議",
        "首先討論停車場收費問題",
        "消防設備需要定期更新",
        "用電異常報告需要處理",
        "維修申請已經簽核通過"
    ]

    # 生成測試音頻 (使用 TTS)
    # 這裡假設已有測試音頻
    log(f"\n測試語料:")
    for i, text in enumerate(test_texts):
        log(f"  [{i+1}] {text}")

    return {
        "system": system,
        "test_texts": test_texts,
        "note": "需要實際音頻文件進行準確率測試"
    }

# ===== 5. 穩定性測試 =====
def test_stability(system, binary=None):
    """測試連續運行穩定性"""
    log(f"\n{'='*60}")
    log(f"5. 穩定性測試 ({system})")
    log(f"{'='*60}")

    results = []
    start = time.time()
    max_duration = 300  # 5 分鐘測試

    # 啟動服務
    if binary:
        proc = subprocess.Popen([binary], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        proc = subprocess.Popen(
            ["python3", WHISPER_SCRIPT],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    # 持續監控
    errors = 0
    health_count = 0

    while time.time() - start < max_duration:
        # 健康檢查
        try:
            health = subprocess.run(
                ["curl", "-s", "http://localhost:3020/health"],
                capture_output=True, text=True, timeout=5
            )
            health_count += 1
        except:
            errors += 1

        # 資源監控
        cpu = get_cpu_usage()
        mem = get_memory_usage()
        log(f"t+{int(time.time()-start)}s: CPU={cpu}% | Mem={mem['used']:.0f}MB")

        time.sleep(10)

    # 結束服務
    proc.terminate()
    proc.wait()

    log(f"\n穩定性測試完成:")
    log(f"  持續時間: {time.time() - start:.0f} 秒")
    log(f"  健康檢查次數: {health_count}")
    log(f"  錯誤次數: {errors}")

    return {
        "system": system,
        "duration": time.time() - start,
        "health_checks": health_count,
        "errors": errors,
        "stability": "PASS" if errors == 0 else "FAIL"
    }

# ===== 主程序 =====
def main():
    log("=" * 60)
    log("🎙️  audio.cpp vs Whisper 性能 Benchmark 測試")
    log("=" * 60)
    log(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"測試路徑: {os.getcwd()}")

    # 創建測試目錄
    os.makedirs("/home/rick/shared-wiki/test-audio", exist_ok=True)
    os.makedirs("/home/rick/shared-wiki/test-results", exist_ok=True)

    # 執行測試
    all_results = {}

    # 1. 啟動時間
    for system, binary in [("Whisper", None), ("audio.cpp", AUDIOCPP_BINARY)]:
        result = test_startup_time(system, binary)
        all_results["startup_time"] = result

    # 2. 推理速度
    for system in ["Whisper", "audio.cpp"]:
        # 需要實際音頻文件
        log(f"\n--- {system} 推理速度測試 ---")
        log(f"請準備測試音頻文件: {TEST_AUDIO_DIR}/")
        log(f"建議使用以下格式:")
        log(f"  - 10 秒：單人朗讀")
        log(f"  - 30 秒：雙人對話")
        log(f"  - 60 秒：三人會議")

    # 3. 資源占用
    for system, binary in [("Whisper", None), ("audio.cpp", AUDIOCPP_BINARY)]:
        result = test_resource_usage(system, binary)
        all_results["resource_usage"] = result

    # 4. 準確率
    for system in ["Whisper", "audio.cpp"]:
        result = test_accuracy(system, None)
        all_results["accuracy"] = result

    # 5. 穩定性
    for system, binary in [("Whisper", None), ("audio.cpp", AUDIOCPP_BINARY)]:
        result = test_stability(system, binary)
        all_results["stability"] = result

    # 保存結果
    output_path = os.path.join("/home/rick/shared-wiki/test-results", f"benchmark-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    log(f"\n{'='*60}")
    log(f"✅ 測試完成！")
    log(f"結果保存: {output_path}")
    log(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"{'='*60}")

if __name__ == "__main__":
    main()
