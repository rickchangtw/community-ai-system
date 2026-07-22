# Phase 4: 社區資料模型設計 (PostgreSQL Schema)

## 完成時間
2026-07-18

## 狀態
✅ 已完成

## 描述
設計完整的 PostgreSQL 資料庫結構，支援 600 戶社區智慧管理系統。

## 資料庫結構

### 1. 基礎資料模型 (Master Data)
- `communities` - 社區主資料
- `buildings` - 大樓
- `floors` - 樓層
- `residents` - 住戶
- `resident_contacts` - 住戶聯絡方式

### 2. 6 個 Agent 角色定義
- `agent_roles` - Agent 角色定義 (ceo, property, security, fire, energy, notice)
- `agent_instances` - Agent 執行者實例

### 3. 事件管理系統
- `event_types` - 事件類型
- `events` - 事件
- `event_actions` - 事件處理記錄
- `event_timeline` - 事件時間線

### 4. 會議系統
- `meetings` - 會議
- `meeting_speakers` - 會議發言人
- `meeting_segments` - 會議語音段
- `meeting_action_items` - 會議行動項目
- `meeting_files` - 會議文件
- `meeting_notes` - 會議筆記

### 5. 通知系統
- `notice_templates` - 通知模板
- `notices` - 通知
- `notice_deliveries` - 通知送達記錄

### 6. 物業管理系統
- `fee_categories` - 收費項目
- `fee_records` - 收費記錄
- `work_orders` - 物業工單

### 7. 保全管理系統
- `patrol_routes` - 巡邏路線
- `patrol_logs` - 巡邏記錄
- `visitor_logs` - 訪客記錄

### 8. 消防管理系統
- `fire_equipment` - 消防設備
- `fire_events` - 消防事件

### 9. 節能管理系統
- `energy_devices` - 能源設備
- `energy_readings` - 能耗記錄
- `energy_policies` - 節能策略

### 10. 權限與角色管理
- `system_roles` - 系統角色
- `users` - 用戶帳號
- `user_community_roles` - 用戶-社區關聯
- `audit_logs` - 操作日誌

## 索引
- 所有外鍵關聯表建立索引
- 常用查詢欄位建立索引
- 事件/會議/通知/收費/工單/設備/能耗記錄

## 預設資料
- 5 個系統角色 (admin, agent, manager, resident, visitor)
- 6 個事件類型 (incident, maintenance, security, fire, energy, notice)
- 6 個收費類別 (管理費, 水費, 電費, 清潔費, 停車費, 維修費)
- 8 個消防設備類型 (灑水頭, 消防栓, 火警警報, 滅火器, 消防控制面板, 攝影機, 緊急照明, 逃生指示標牌)
- 8 個能源設備類型 (電表, 感測器, 執行器, 逆變器, 水泵, 空調, 照明, 電梯)
- 6 個物業工單類別 (維修, 修理, 清潔, 油漆, 電氣, 管線)

## 資料庫配置
```python
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "community",
    "user": "hermes",
    "password": "hermes123"
}
```

## 檔案
- `01-community-schema.sql` - 完整的建表 SQL 腳本
- `02-test-schema.py` - Schema 測試腳本
- `03-documentation.md` - 本文档
