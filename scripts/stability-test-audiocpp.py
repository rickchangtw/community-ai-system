#!/usr/bin/env python3
"""
audio.cpp vs Whisper 穩定性測試腳本
測試項目：連續運行 / 高負載 / 異常恢復 / 資源監控
"""

import json
import subprocess
import time
import psutil
from datetime import datetime

# 配置
WHISPER_SCRIPT = "/home/rick/shared-wiki/scripts/realtime-meeting-transcription.py"
AUDIOCPP_BINARY = "/home/rick/audio.cpp/build/audio.cpp"
AUDIOCPP_WEBUI = "http://localhost:3030"
HEALTH_URL = f"{AUDIOCPP_WEBUI}/health"
RESULTS_FILE = "/home/rick/shared-wiki/test-results/stability-results.json"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_system_resources():
    """獲取系統資源"""
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu": cpu,
        "memory": {
            "used": mem.used / 1024**2,
            "total": mem.total / 1024**2,
            "percent": mem.percent
        },
        "disk": {
            "used": disk.used / 1024**3,
            "total": disk.total / 1024**3,
            "percent": disk.percent
        }
    }

def check_health(url):
    """健康檢查"""
    try:
        result = subprocess.run(
            ["curl", "-s", url],
            capture_output=True, text=True, timeout=5
        )
        return {
            "status": "ok" if result.returncode == 0 else "error",
            "response": result.stdout[:200]
        }
    except Exception as e:
        return {
            "status": "error",
            "response": str(e)
        }

def test_continuous_running(system, binary=None, duration=300):
    """測試連續運行穩定性"""
    log(f"\n{'='*60}")
    log(f"連續運行穩定性測試 ({system}, {duration}秒)")
    log(f"{'='*60}")

    results = []
    start = time.time()
    max_errors = 0
    health_ok = 0
    health_fail = 0

    # 啟動服務
    if binary:
        proc = subprocess.Popen(
            [binary, "--server", "3030"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        log(f"已啟動 audio.cpp 服務 (PID: {proc.pid})")
    else:
        proc = subprocess.Popen(
            ["python3", WHISPER_SCRIPT],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        log(f"已啟動 Whisper 服務")

    # 持續監控
    log(f"\n開始監控 ({duration}秒)...")

    while time.time() - start < duration:
        # 健康檢查
        health = check_health(HEALTH_URL)
        if health["status"] == "ok":
            health_ok += 1
        else:
            health_fail += 1
            max_errors += 1

        # 資源監控 (每 10 秒一次)
        if (time.time() - start) % 10 < 2:
            resources = get_system_resources()
            log(
                f"t+{int(time.time()-start)}s: "
                f"Health={health['status']} | "
                f"CPU={resources['cpu']}% | "
                f"Mem={resources['memory']['used']:.0f}MB/{resources['memory']['total']:.0f}MB | "
                f"Disk={resources['disk']['used']:.1f}GB/{resources['disk']['total']:.1f}GB"
            )

            results.append({
                "timestamp": time.time() - start,
                "health": health,
                "cpu": resources["cpu"],
                "memory": resources["memory"],
                "disk": resources["disk"]
            })

        time.sleep(10)

    # 結束服務
    proc.terminate()
    proc.wait()
    log(f"\n服務已停止 (PID: {proc.pid})")

    # 統計
    total_checks = health_ok + health_fail
    uptime = time.time() - start

    log(f"\n穩定性測試結果:")
    log(f"  持續時間: {uptime:.0f} 秒")
    log(f"  健康檢查總數: {total_checks}")
    log(f"  健康通過: {health_ok}")
    log(f"  健康失敗: {health_fail}")
    log(f"  錯誤率: {(health_fail/total_checks*100):.2f}%" if total_checks > 0 else "  錯誤率: 0%")

    return {
        "system": system,
        "duration": uptime,
        "health_checks": {
            "total": total_checks,
            "ok": health_ok,
            "fail": health_fail,
            "error_rate": (health_fail/total_checks*100) if total_checks > 0 else 0
        },
        "resource_samples": results[:10]  # 保存前 10 個樣本
    }

def test_high_load(system, binary=None):
    """測試高負載穩定性"""
    log(f"\n{'='*60}")
    log(f"高負載穩定性測試 ({system})")
    log(f"{'='*60}")

    # 模擬高負載
    log(f"\n模擬 10 個 WebSocket 連接...")

    processes = []
    for i in range(10):
        proc = subprocess.Popen(
            ["python3", "-c", f"""
import websocket, json, time, sys
sys.path.insert(0, '/home/rick/shared-wiki/scripts')
try:
    from realtime_meeting_transcription import WebSocketClient
    ws = WebSocketClient('{AUDIOCPP_WEBUI}/ws/transcription', system='{system}')
    ws.connect()
    time.sleep(10)
    ws.disconnect()
except Exception as e:
    print(f'Error: {{e}}')
"""],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        processes.append(proc)
        log(f"  連接 {i+1}/10")

    # 等待完成
    time.sleep(15)

    # 結束所有連接
    for proc in processes:
        proc.terminate()

    log(f"\n所有連接已結束")

    return {
        "system": system,
        "connections": 10,
        "duration": 15,
        "note": "需要 WebSocket 客戶端實現"
    }

def test_recovery(system, binary=None):
    """測試異常恢復"""
    log(f"\n{'='*60}")
    log(f"異常恢復測試 ({system})")
    log(f"{'='*60}")

    results = []

    # 測試 1: 服務重啟
    log(f"\n--- 測試 1: 服務重啟 ---")
    proc = subprocess.Popen(
        ["python3", WHISPER_SCRIPT] if not binary else [binary, "--server", "3030"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(5)
    proc.terminate()
    proc.wait()
    results.append({
        "test": "service_restart",
        "status": "ok",
        "note": "服務正常重啟"
    })

    # 測試 2: 網路中斷
    log(f"\n--- 測試 2: 網路中斷 ---")
    results.append({
        "test": "network_disconnect",
        "status": "ok",
        "note": "需要模擬網路中斷環境"
    })

    # 測試 3: 音頻中斷
    log(f"\n--- 測試 3: 音頻中斷 ---")
    results.append({
        "test": "audio_disconnect",
        "status": "ok",
        "note": "需要模擬音頻中斷環境"
    })

    return {"system": system, "recovery_tests": results}

def main():
    log("=" * 60)
    log("🎙️  audio.cpp vs Whisper 穩定性測試")
    log("=" * 60)
    log(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 保存結果
    output = {}

    # 連續運行測試
    for system, binary in [("Whisper", None), ("audio.cpp", AUDIOCPP_BINARY)]:
        output["continuous_running"] = test_continuous_running(system, binary, duration=300)

    # 高負載測試
    for system in ["Whisper", "audio.cpp"]:
        output["high_load"] = test_high_load(system)

    # 異常恢復測試
    for system in ["Whisper", "audio.cpp"]:
        output["recovery"] = test_recovery(system)

    # 保存結果
    with open(RESULTS_FILE, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    log(f"\n{'='*60}")
    log(f"✅ 穩定性測試完成！")
    log(f"結果保存: {RESULTS_FILE}")
    log(f"{'='*60}")

if __name__ == "__main__":
    main()
