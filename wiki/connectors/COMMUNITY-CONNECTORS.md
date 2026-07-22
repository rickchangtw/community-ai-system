---
type: Connector Configuration
title: 社區管理系統連接器配置
description: 多 Agent 系統的數據來源配置 — Git、LINE、PostgreSQL、Redis
okf_version: "0.1"
timestamp: "2026-07-19T00:00:00Z"
tags: [connectors, configuration, data-sources]
---

# 社區管理系統連接器配置

## 連接器列表

| 連接器 | 類型 | 認證方式 | 數據來源 |
|--------|------|----------|----------|
| Git Repo | 本地倉庫 | SSH/HTTPS | 社區管理系統源碼 |
| LINE Webhook | 外部 API | OAuth | 居民 LINE 通知 |
| PostgreSQL | 數據庫 | Connection String | 社區數據 (35 tables) |
| Redis | 緩存 | Connection String | 狀態、排程、健康檢查 |

## 數據飛輪流程

```
居民 (LINE)
  │
  ▼
[LINE Bot] → [Hermes Agent]
  │
  ▼
[PostgreSQL] → [OKF Knowledge Base]
  │
  ▼
[Git Repository] → [多 Agent 共享]
  │
  ▼
[各 Agent 讀寫更新]
```

## 認證配置

```bash
# LINE
LINE_CHANNEL_ID=xxx
LINE_CHANNEL_SECRET=xxx
LINE_CHANNEL_ACCESS_TOKEN=xxx

# PostgreSQL
PGHOST=localhost
PGPORT=5432
PGDATABASE=community
PGUSER=postgres
PGPASSWORD=xxx

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Git
GIT_SSH_COMMAND=ssh -T
```

## 知識庫同步

使用 OKF v0.1 格式，所有 Agent 共享同一知識庫：

- **讀寫權限**: 所有 Agent 可讀，部分 Agent 可寫
- **版本控制**: Git 倉庫管理
- **衝突解決**: 基於時間戳的衝突合併
