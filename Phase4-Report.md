# Phase 4 資料庫結構設計報告

**日期**: 2026-07-19  
**狀態**: ✅ 完成

---

## 一、目標

設計完整的 PostgreSQL 資料庫結構，支援 600 戶社區智慧管理系統。

## 二、資料庫結構

### 1. 基礎資料模型 (Master Data)

| 表 | 描述 | 欄位數 |
|----|------|--------|
| communities | 社區主資料 | 8 |
| buildings | 大樓 | 7 |
| floors | 樓層 | 6 |
| residents | 住戶 | 9 |
| resident_contacts | 住戶聯絡方式 | 6 |

### 2. 6 個 Agent 角色定義

| 表 | 描述 | 欄位數 |
|----|------|--------|
| agent_roles | Agent 角色定義 | 6 |
| agent_instances | Agent 執行者實例 | 7 |

### 3. 事件管理系統

| 表 | 描述 | 欄位數 |
|----|------|--------|
| event_types | 事件類型 | 6 |
| events | 事件 | 12 |
| event_actions | 事件處理記錄 | 6 |
| event_timeline | 事件時間線 | 5 |

### 4. 會議系統

| 表 | 描述 | 欄位數 |
|----|------|--------|
| meetings | 會議 | 11 |
| meeting_speakers | 會議發言人 | 7 |
| meeting_segments | 會議語音段 | 6 |
| meeting_action_items | 會議行動項目 | 8 |
| meeting_files | 會議文件 | 7 |
| meeting_notes | 會議筆記 | 6 |

### 5. 通知系統

| 表 | 描述 | 欄位數 |
|----|------|--------|
| notice_templates | 通知模板 | 7 |
| notices | 通知 | 10 |
| notice_deliveries | 通知送達記錄 | 11 |

### 6. 物業管理系統

| 表 | 描述 | 欄位數 |
|----|------|--------|
| fee_categories | 收費項目 | 6 |
| fee_records | 收費記錄 | 10 |
| work_orders | 物業工單 | 13 |

### 7. 保全管理系統

| 表 | 描述 | 欄位數 |
|----|------|--------|
| patrol_routes | 巡邏路線 | 7 |
| patrol_logs | 巡邏記錄 | 8 |
| visitor_logs | 訪客記錄 | 12 |

### 8. 消防管理系統

| 表 | 描述 | 欄位數 |
|----|------|--------|
| fire_equipment | 消防設備 | 12 |
| fire_events | 消防事件 | 11 |

### 9. 節能管理系統

| 表 | 描述 | 欄位數 |
|----|------|--------|
| energy_devices | 能源設備 | 13 |
| energy_readings | 能耗記錄 | 8 |
| energy_policies | 節能策略 | 8 |

### 10. 權限與角色管理

| 表 | 描述 | 欄位數 |
|----|------|--------|
| system_roles | 系統角色 | 5 |
| users | 用戶帳號 | 9 |
| user_community_roles | 用戶-社區關聯 | 4 |
| audit_logs | 操作日誌 | 6 |

## 三、統計

| 指標 | 數值 |
|------|------|
| 總表數 | 35 |
| 總欄位數 | ~250 |
| 外鍵關聯 | 60+ |
| 索引 | 12+ |
| JSONB 欄位 | 15+ |
| CHECK 約束 | 8+ |
| 預設資料 | 6 角色 + 4 社區/大樓/住戶 |

## 四、關鍵設計決策

### 1. 欄位命名
- 使用 `community_id` 而非 `id`，避免與系統級 ID 衝突
- 使用 `resident_id` 而非 `user_id`，區分住戶與系統用戶

### 2. 資料類型
- 主鍵使用 `VARCHAR(50)` 而非 `SERIAL`，支援 UUID 格式
- 金額使用 `NUMERIC(10, 2)`，避免浮點誤差
- 時間使用 `TIMESTAMP DEFAULT NOW()`，自動記錄

### 3. 外鍵約束
- 所有外鍵使用 `ON DELETE CASCADE`，確保資料一致性
- 住戶資料透過 `community_id` + `building_id` + `unit_number` 唯一識別

### 4. JSONB 使用
- `meetings` 表使用 `JSONB` 儲存 agenda、action_items、notes
- `energy_policies` 表使用 `JSONB` 儲存 schedule、parameters
- `event_timeline` 表使用 `JSONB` 儲存 timeline entries

### 5. 預設資料
- 6 個 Agent 角色：ceo, property, security, fire, energy, notice
- 優先級：100 (CEO) → 70 (Notice)，反映決策權重
- 4 個預設社區：明華社區、德和社區、東昇社區、華豐社區

## 五、索引策略

### 主鍵索引
- 所有表使用 PRIMARY KEY (自動建立索引)

### 外鍵索引
- communities(community_id), buildings(community_id)
- residents(community_id), buildings(building_id), floors(floor_id)
- events(community_id), buildings(building_id), floors(floor_id)
- notices(community_id), communities(community_id)
- fee_records(community_id), buildings(building_id), floors(floor_id), residents(resident_id)

### 業務索引
- events(status, priority) - 快速查詢未解決事件
- notices(target_roles, priority) - 快速查詢通知
- work_orders(status, priority) - 快速查詢工單
- fire_equipment(status) - 快速查詢異常設備
- energy_devices(status) - 快速查詢異常設備

## 六、完整文件清單

| 文件 | 大小 | 描述 |
|------|------|------|
| `phase4/01-community-schema.sql` | 24,620 字元 | 完整建表 SQL (655 行) |
| `phase4/README.md` | 2,721 字元 | Phase 4 文件 |
| `Phase4-Report.md` | 本文件 | Phase 4 測試報告 |

## 七、下一步

1. **Phase 5** - Agent Communication Protocol (已完成)
2. **Phase 6** - Deployment Architecture (已完成)
3. **Phase 7** - Integration Testing (已完成)
4. **Phase 8** - Performance Optimization (待進行)
