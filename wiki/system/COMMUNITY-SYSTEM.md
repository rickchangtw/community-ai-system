---
type: System Architecture
title: 社區管理系統架構
description: 600 戶社區智慧管理系統 — 多 Agent 架構、技術棧與部署配置
okf_version: "0.1"
timestamp: "2026-07-19T00:00:00Z"
tags: [system, architecture, multi-agent]
---

# 社區管理系統架構

## 多 Agent 架構

| Agent | 角色 | 端口 | 職責 |
|-------|------|------|------|
| `hermes-admin` | 總幹事 | 3010 | 最終決策、公告、簽核 |
| `hermes-property` | 物業管理 | 3011 | 工單、維修排程 |
| `hermes-security` | 保全監控 | 3013 | 事件監控、巡邏記錄 |
| `hermes-fire` | 消防管理 | 3014 | 設備檢查、演練 |
| `hermes-energy` | 節能管理 | 3015 | 能源分析、可持續性 |
| `hermes-notify` | 通知中心 | 3016 | 居民通知、投票 |

## 技術棧

- **AI 引擎**: Silero VAD + Whisper + PostgreSQL JSONB + FastAPI WebSocket
- **通訊**: LINE Webhook + Telegram
- **知識庫**: OKF v0.1 (Google Open Knowledge Format)
- **部署**: Docker Compose (12 services)

## 數據飛輪

所有 Agent 共享同一知識庫，通過 OKF 格式實現：
1. 知識由 Agent 生成
2. 通過 Git 版本控制
3. 多 Agent 共享讀寫
4. 持續更新迭代
