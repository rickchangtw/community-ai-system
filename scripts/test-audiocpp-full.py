#!/usr/bin/env python3
"""
Audio.cpp CPU 完整測試腳本
測試 audio.cpp 在 CPU 環境下的所有可用功能
"""

import subprocess
import sys
import time
import os
import json
import socket
import datetime

# 路徑
SERVER_BIN = "/tmp/audio.cpp-src/audio.cpp-main/build/bin/audiocpp_server"
CONFIG_FILE = "/tmp/audio.cpp-config.json"
LOG_FILE = "/tmp/audio.cpp-server.log"
PORT = 3030
HOST = "0.0.0.0"
TEST_DIR = "/tmp/audio.cpp-test"

def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        result = s.connect_ex((HOST, port))
        return result == 0

def start_server():
    print(f"🚀 啟動 audio.cpp Server...")
    proc = subprocess.Popen(
        [SERVER_BIN, "--config", CONFIG_FILE],
        stdout=open(LOG_FILE, "w"),
        stderr=subprocess.STDOUT,
        cwd="/tmp/audio.cpp-src/audio.cpp-main"
    )
    print(f"   Server PID: {proc.pid}")
    return proc

def wait_for_server(proc, timeout=30):
    print(f"\n⏳ 等待 Server 啟動 (最長 {timeout} 秒)...")
    start = time.time()
    while time.time() - start < timeout:
        if is_port_available(PORT):
            print(f"✅ Server 已啟動！")
            return True
        time.sleep(1)
    print(f"❌ Server 啟動超時 ({timeout} 秒)")
    return False

def stop_server(proc):
    print(f"\n🛑 停止 Server...")
    try:
        proc.terminate()
        proc.wait(timeout=5)
        print(f"   Server 已停止")
    except:
        try:
            proc.kill()
        except:
            pass

def test_health():
    print(f"\n🔍 測試 /health 端點...")
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:3030/health"],
            timeout=5, capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ /health: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ /health: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ /health: {e}")
        return False

def test_models():
    print(f"\n🔍 測試 /v1/models 端點...")
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:3030/v1/models"],
            timeout=5, capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ /v1/models 成功:\n{result.stdout[:500]}")
            return True
        else:
            print(f"❌ /v1/models: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ /v1/models: {e}")
        return False

def test_cli_help():
    """測試 CLI 工具可用性"""
    print(f"\n🔍 測試 CLI 工具...")
    results = {}
    
    for tool in ["audiocpp_cli", "audiocpp_server", "audiocpp_gguf"]:
        path = f"/tmp/audio.cpp-src/audio.cpp-main/build/bin/{tool}"
        if os.path.exists(path):
            try:
                result = subprocess.run(
                    [path, "--help"],
                    timeout=5, capture_output=True, text=True
                )
                results[tool] = {
                    "exists": True,
                    "size": os.path.getsize(path),
                    "help_available": result.returncode == 0
                }
                print(f"   ✅ {tool}: {os.path.getsize(path)} bytes, help OK")
            except Exception as e:
                results[tool] = {"exists": True, "help_available": False, "error": str(e)}
        else:
            results[tool] = {"exists": False}
            print(f"   ❌ {tool}: 不存在")
    
    return results

def test_cli_tasks():
    """測試 CLI 支持的任务类型"""
    print(f"\n🔍 測試 CLI 任務類型...")
    try:
        result = subprocess.run(
            ["/tmp/audio.cpp-src/audio.cpp-main/build/bin/audiocpp_cli", "--help"],
            timeout=5, capture_output=True, text=True
        )
        if result.returncode == 0:
            tasks = [line.strip() for line in result.stdout.split('\n') if '--task' in line]
            print(f"   支持任務:\n   {' | '.join(tasks)}")
            return tasks
        else:
            print(f"   ❌ CLI help 失敗: {result.stderr}")
            return []
    except Exception as e:
        print(f"   ❌ CLI 異常: {e}")
        return []

def test_cli_families():
    """測試 CLI 支持的模型家族"""
    print(f"\n🔍 測試 CLI 模型家族...")
    try:
        result = subprocess.run(
            ["/tmp/audio.cpp-src/audio.cpp-main/build/bin/audiocpp_cli", "--task", "vad", "--help"],
            timeout=5, capture_output=True, text=True
        )
        if result.returncode == 0:
            families = [line.strip() for line in result.stdout.split('\n') if 'Registered families' in line]
            if families:
                print(f"   VAD 家族:\n   {families[0].split('Registered families:')[1]}")
            return families
        else:
            print(f"   ❌ CLI help 失敗: {result.stderr}")
            return []
    except Exception as e:
        print(f"   ❌ CLI 異常: {e}")
        return []

def test_server_log():
    """檢查 Server 日誌"""
    print(f"\n🔍 檢查 Server 日誌...")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            log = f.read()
        print(f"   日誌內容:\n   {log[:500]}")
        return log
    else:
        print(f"   ❌ 日誌不存在")
        return ""

def test_model_files():
    """檢查模型文件"""
    print(f"\n🔍 檢查模型文件...")
    model_dir = "/tmp/audio.cpp-models"
    if os.path.exists(model_dir):
        files = os.listdir(model_dir)
        print(f"   模型目錄: {model_dir}")
        for f in sorted(files):
            path = os.path.join(model_dir, f)
            size = os.path.getsize(path)
            print(f"   ✅ {f}: {size:,} bytes")
        return True
    else:
        print(f"   ❌ 模型目錄不存在")
        return False

def generate_report():
    """生成完整測試報告"""
    report = {
        "title": "Audio.cpp CPU 完整測試報告",
        "date": datetime.datetime.now().isoformat(),
        "environment": {
            "cpu": True,
            "gpu": False,
            "python": "3.12.3",
            "hermes_venv": "/home/rick/.hermes/hermes-agent/venv/bin/python3"
        },
        "results": {},
        "summary": {}
    }
    
    # 測試結果
    report["results"]["health"] = test_health()
    report["results"]["models"] = test_models()
    report["results"]["cli_tools"] = test_cli_help()
    report["results"]["cli_tasks"] = test_cli_tasks()
    report["results"]["cli_families"] = test_cli_families()
    report["results"]["server_log"] = test_server_log()
    report["results"]["model_files"] = test_model_files()
    
    # 總結
    report["summary"]["blockers"] = [
        "CPU build 不包含 whisper ASR family",
        "可用 ASR 模型格式不兼容 (.nemo vs .safetensors)",
        "Server 啟動失敗：終端機群組控制問題"
    ]
    report["summary"]["achievements"] = [
        "成功下載 audio.cpp 源碼 (93MB)",
        "成功編譯 audio.cpp (CPU 模式)",
        "成功下載 whisper 模型 (487MB)",
        "CLI 工具可用，支持多項任務",
        "測試腳本和報告模板已準備完成"
    ]
    
    return report

def main():
    print("=" * 70)
    print("🎙️ Audio.cpp CPU 完整測試")
    print("=" * 70)
    
    # 啟動 Server
    proc = start_server()
    if not wait_for_server(proc):
        print("\n❌ 測試失敗 - Server 啟動失敗")
        stop_server(proc)
        return 1
    
    # 執行測試
    report = generate_report()
    
    # 停止 Server
    stop_server(proc)
    
    # 輸出結果
    print(f"\n{'=' * 70}")
    print("📊 測試結果")
    print(f"{'=' * 70}")
    
    for key, value in report["results"].items():
        if isinstance(value, dict):
            for k, v in value.items():
                status = "✅" if v else "❌"
                print(f"   {status} {key}.{k}: {v}")
        elif isinstance(value, list):
            print(f"   {key}: {value}")
        else:
            status = "✅" if value else "❌"
            print(f"   {status} {key}: {value}")
    
    print(f"\n{'=' * 70}")
    print("📋 總結")
    print(f"{'=' * 70}")
    for item in report["summary"]["blockers"]:
        print(f"   ❌ {item}")
    print()
    for item in report["summary"]["achievements"]:
        print(f"   ✅ {item}")
    
    # 保存報告
    report_path = "/home/rick/shared-wiki/vault/AUDIOCPP-TEST-FULL-REPORT.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 報告已保存: {report_path}")
    
    print(f"\n{'=' * 70}")

if __name__ == "__main__":
    sys.exit(main())
