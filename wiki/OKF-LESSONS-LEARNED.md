---
type: Lessons Learned
title: OKF 踩坑記錄與解決方案
description: 社區管理系統開發過程中遇到的問題、解決方案與教訓
okf_version: "0.1"
timestamp: "2026-07-22T00:00:00Z"
tags: [lessons, pitfall, troubleshooting, okf]
---

# OKF 踩坑記錄與解決方案

## 2026-07-22 專案提交 GitHub

### 1. GitHub Token 權限不足

| 項目 | 說明 |
|------|------|
| **問題** | 舊 Token (REDACTED_TOKEN) 只有 `public_repo` 權限，無法建立新倉庫 |
| **症狀** | `curl -s -X POST /user/repos` 返回 403 "Resource not accessible by personal access token" |
| **解決** | 使用舊 Token `REDACTED_TOKEN`（有 `repo` 權限） |
| **教訓** | PAT 權限必須包含 `repo` 才能建立倉庫 |

### 2. gh CLI 版本過舊

| 項目 | 說明 |
|------|------|
| **問題** | 系統 gh 版本 0.0.4，無法執行 `gh repo create` 等命令 |
| **症狀** | `gh: error: unrecognized arguments: repo create` |
| **解決** | 直接改用 curl + GitHub REST API |
| **教訓** | 優先檢查 gh CLI 版本，過舊時直接用 API |

### 3. .gitconfig Credential 衝突

| 項目 | 說明 |
|------|------|
| **問題** | 舊 Token 的 credential helper 和 http extraHeader 與新 Token 衝突 |
| **症狀** | Token 驗證通過但 API 返回 403 |
| **解決** | 清除 `~/.gitconfig` 中 credential.helper 和 http.extraHeader |
| **教訓** | 更換 Token 前必須清理 gitconfig |

## 2026-07-18 LINE Bot 開發

### 4. LINE 機器人 Token 格式

| 項目 | 說明 |
|------|------|
| **問題** | LINE 機器人 API Token 格式錯誤 |
| **症狀** | API 返回 401 Unauthorized |
| **解決** | 確認 Token 格式為 `eyJxxx` 開頭 |
| **教訓** | LINE 機器人需要 Pairwise Token 和 Channel Access Token |

### 5. LINE 簽章驗證失敗

| 項目 | 說明 |
|------|------|
| **問題** | 簽章驗證 (Signature Verification) 失敗 |
| **症狀** | `Invalid signature` 錯誤 |
| **解決** | 確認 RSA 公鑰和簽章算法正確 |
| **教訓** | LINE 簽章需要 SHA256 with RSA-PKCS1-v1_5 |

## 2026-07-19 多 Agent 系統

### 6. Agent 通訊協議設計

| 項目 | 說明 |
|------|------|
| **問題** | Agent 之間通訊協議設計複雜 |
| **症狀** | 訊息路由錯誤、事件觸發失敗 |
| **解決** | 簡化協議為 JSON 格式，定義明確的事件類型 |
| **教訓** | 優先定義最小 viable 協議，再逐步擴充 |

### 7. Docker Compose 網路問題

| 項目 | 說明 |
|------|------|
| **問題** | Docker Compose 容器間網路通訊失敗 |
| **症狀** | 容器無法互相訪問 |
| **解決** | 確認 network 配置和 service 名稱正確 |
| **教訓** | Docker Compose 所有容器必須在同一 network |

## 2026-07-20 測試與部署

### 8. 測試腳本執行環境

| 項目 | 說明 |
|------|------|
| **問題** | 測試腳本在生產環境執行失敗 |
| **症狀** | 依賴的庫或服務未安裝 |
| **解決** | 添加 requirements.txt 和環境檢查 |
| **教訓** | 測試腳本必須獨立於環境配置 |

### 9. 資料庫連線問題

| 項目 | 說明 |
|------|------|
| **問題** | 生產環境 PostgreSQL 連線失敗 |
| **症狀** | Connection refused / Authentication failed |
| **解決** | 確認連線參數和憑證正確 |
| **教訓** | 生產環境必須使用環境變數管理憑證 |

## 常見問題排查清單

### GitHub API 問題

1. **401 Unauthorized**: Token 過期或無效
2. **403 Forbidden**: Token 權限不足（需要 `repo` 權限）
3. **404 Not Found**: 資源不存在
4. **422 Validation Failed**: 請求格式錯誤

### Docker Compose 問題

1. **容器無法啟動**: 檢查 port 衝突
2. **服務無法通訊**: 檢查 network 配置
3. **健康檢查失敗**: 檢查 healthcheck 配置

### 連線問題

1. **Connection refused**: 服務未啟動或端口錯誤
2. **Connection timed out**: 網路問題或防火牆
3. **Authentication failed**: 憑證錯誤

## 最佳實踐

1. **Token 管理**: 使用環境變數，不要硬碼
2. **錯誤處理**: 添加完整的錯誤訊息和日誌
3. **環境隔離**: 使用 Docker Compose 隔離環境
4. **測試自動化**: 添加單元測試和集成測試
5. **文檔維護**: 持續更新踩坑記錄

