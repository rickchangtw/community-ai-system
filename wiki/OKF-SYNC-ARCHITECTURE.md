---
type: Architecture Document
title: OKF 多主機 Agent 知識共享同步架構
description: 跨主機 Hermes Agent 共享維護 OKF v0.1 知識庫的完整方案 — Git + Webhook + Redis
okf_version: "0.1"
timestamp: "2026-07-19T00:00:00Z"
tags: [architecture, sync, multi-host, okf, git]
---

# OKF 多主機 Agent 知識共享同步架構

## 問題

本地知識庫 (`~/shared-wiki/wiki/`) 只能被本機 Agent 訪問。
需要讓**遠端主機上的 Agent** 也能：
1. **讀取** OKF 知識庫
2. **更新** 知識庫
3. **同步** 跨主機變更

## 解決方案

### 架構概覽

```
┌─────────────────────────────────────────────────────────────┐
│                    OKF Knowledge Base                        │
│                     ~/shared-wiki/wiki/                      │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Agent A  │  │ Agent B  │  │ Agent C  │  │ Agent D  │   │
│  │ (本地)   │  │ (本地)   │  │ (本地)   │  │ (遠端)   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │          │
│       ▼              ▼              ▼              ▼          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Git Repository (主副本)                   │   │
│  │           ~/shared-wiki/wiki/ (Git repo)              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Webhook Server (知識庫更新通知)               │   │
│  │              監聽所有 Git push 事件                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Redis Pub/Sub (即時通知)                  │   │
│  │              channel: okf:updates                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 方案一：Git 同步 (推薦)

### 核心原則

**單一源真相比 (Single Source of Truth)**：
- 一個 Git 倉庫作為知識庫的唯一副本
- 所有 Agent 讀寫同一個倉庫
- 通過 Git 版本控制實現變更追蹤

### 部署方式

#### 方式 A：Git Clone (靜態同步)

```bash
# 本地 Agent
git clone /home/rick/shared-wiki/wiki.git ~/wiki-local/
# 讀寫本地副本，定期 pull

# 遠端 Agent
git clone <ssh://user@host:/path/to/wiki.git> ~/wiki-remote/
# 讀寫遠端副本，定期 pull
```

**優點**: 簡單直接
**缺點**: 需要定期同步，不是即時

#### 方式 B：Git Remote + Webhook (推薦)

```bash
# 本機 (主倉庫)
cd ~/shared-wiki/wiki
git remote add origin ssh://user@remote-host:/path/to/wiki.git
git remote -v
```

```bash
# 遠端 Agent 添加本機為 remote
git remote add origin ssh://rick@localhost:/home/rick/shared-wiki/wiki
git fetch origin
git pull origin main
```

**優點**: 即時同步，可追蹤變更
**缺點**: 需要 SSH 配置

#### 方式 C：Git LFS (大文件)

如果知識庫包含大文件（如音頻、圖片）：

```bash
git lfs install
git lfs track "*.mp3"
git lfs track "*.png"
```

---

## 方案二：Webhook 通知 (即時同步)

### 部署 Webhook Server

```python
# webhooks/okf-sync-server.py
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/webhook/okf-update', methods=['POST'])
def okf_update():
    # 接收 Git push 事件
    payload = request.get_json()
    event = payload.get('event')
    ref = payload.get('ref')
    
    # 通知所有 Agent
    redis_pubsub.publish('okf:updates', {
        'event': event,
        'ref': ref,
        'repository': payload.get('repository_url')
    })
    
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3099)
```

### Git Push + Webhook

```bash
# 本機 Agent 推送變更
cd ~/shared-wiki/wiki
git add .
git commit -m "更新消防設備檢查記錄"
git push origin main

# 遠端 Agent 自動收到通知
# Redis channel: okf:updates
# 可以觸發自動 pull 或重新載入知識庫
```

---

## 方案三：Redis Pub/Sub (即時通知)

### 發布/訂閱模式

```python
# 發布端 (本機 Agent)
import redis
r = redis.Redis(host='localhost', port=6379)

# 發布知識庫變更
r.publish('okf:updates', {
    'action': 'update',
    'file': 'fire-equipment/FIRE-EQUIPMENT.md',
    'timestamp': '2026-07-19T10:00:00Z',
    'agent': 'hermes-admin'
})
```

```python
# 訂閱端 (遠端 Agent)
import redis
r = redis.Redis(host='localhost', port=6379)

# 訂閱知識庫變更
sub = r.pubsub()
sub.subscribe('okf:updates')

for message in sub.listen():
    if message['type'] == 'message':
        print(f"Received: {message['data']}")
        # 觸發知識庫重新載入
```

---

## 完整部署方案

### 1. 初始化 Git 倉庫

```bash
# 本機
cd ~/shared-wiki/wiki
git init
git add .
git commit -m "Initial OKF v0.1 knowledge base"

# 遠端配置
git remote add origin ssh://rick@localhost:/home/rick/shared-wiki/wiki
```

### 2. 配置 Webhook (可選)

```bash
# 本機部署 Webhook Server
screen -S webhooks -dm python3 /home/rick/shared-wiki/webhooks/okf-sync-server.py

# 遠端 Agent 添加本機為 webhook URL
git push --add-hook post-push <webhook-url>/webhook/okf-update
```

### 3. 遠端 Agent 配置

```bash
# 遠端 Agent 拉取知識庫
git clone ssh://rick@localhost:/home/rick/shared-wiki/wiki.git ~/wiki/

# 或者添加本機為 remote
git remote add origin ssh://rick@localhost:/home/rick/shared-wiki/wiki
git fetch origin
git pull origin main

# 本地 Agent 讀寫
cd ~/wiki/
# 所有 OKF 文件可被 Hermes Agent 直接讀取
```

### 4. 定期同步腳本

```bash
# sync-okf.sh (遠端 Agent 定期執行)
#!/bin/bash
cd ~/wiki/
git pull origin main 2>/dev/null
# 重新載入知識庫
python3 -c "
from hermes_agent import load_knowledge_base
load_knowledge_base('/home/user/wiki/')
"
```

```bash
# 每小時同步
crontab -e
0 * * * * /home/user/sync-okf.sh >> /var/log/okf-sync.log 2>&1
```

---

## 多 Agent 權限控制

### RBAC 配置

| 權限 | Agent | 說明 |
|------|-------|------|
| **讀取** | 所有 Agent | 可讀取任何 OKF 文件 |
| **寫入** | hermes-admin | 可更新任何文件 |
| **寫入** | hermes-property | 可更新 property 相關文件 |
| **寫入** | hermes-fire | 可更新 fire-equipment 文件 |
| **寫入** | hermes-energy | 可更新 energy 文件 |
| **寫入** | hermes-security | 可更新 security 相關文件 |
| **刪除** | hermes-admin | 僅總幹事可刪除文件 |

### Git 分支隔離

```bash
# 主分支：穩定版本
git checkout main

# 功能分支：開發中
git checkout -b feature/update-fire-equipment

# 合併後推送
git checkout main
git merge feature/update-fire-equipment
git push origin main
```

---

## 驗證

### 本機驗證

```bash
# 1. 讀取 OKF 文件
cat ~/shared-wiki/wiki/fire-equipment/FIRE-EQUIPMENT.md

# 2. 更新文件
echo "# 更新測試" >> ~/shared-wiki/wiki/fire-equipment/FIRE-EQUIPMENT.md
git add .
git commit -m "測試 OKF 更新"
git push origin main

# 3. 遠端拉取
ssh remote-host "cd ~/wiki && git pull origin main && cat FIRE-EQUIPMENT.md"
```

### 遠端驗證

```bash
# 遠端 Agent 讀取
cat ~/wiki/fire-equipment/FIRE-EQUIPMENT.md

# 應該包含最新內容
```

---

## 安全考慮

### SSH 認證

```bash
# 遠端 Agent 配置 SSH 公鑰
ssh-copy-id rick@localhost
ssh-keyscan localhost >> ~/.ssh/known_hosts
```

### 知識庫訪問控制

```yaml
# .gitignore (保護敏感信息)
.env
*.key
*.secret
```

---

## 總結

| 方案 | 即時性 | 複雜度 | 推薦場景 |
|------|--------|--------|----------|
| Git Clone | 延遲 (分鐘級) | 低 | 小型部署 |
| Git Remote + Webhook | 即時 | 中 | 中型部署 |
| Redis Pub/Sub | 即時 (秒級) | 中 | 大型部署 |
| 組合方案 | 即時 | 高 | 生產環境 |

**推薦**: Git Remote + Webhook + Redis Pub/Sub 組合方案
