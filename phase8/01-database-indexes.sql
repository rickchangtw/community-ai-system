-- ============================================================================
-- Phase 8: Database Index Optimization
-- ============================================================================

-- ============================================================================
-- 1. Event Management Indexes
-- ============================================================================

-- 事件狀態 + 優先級 (快速查詢未解決事件)
CREATE INDEX IF NOT EXISTS idx_events_status_priority ON events (status, priority) DESC;

-- 事件社區 + 類型 (快速查詢特定社區的事件)
CREATE INDEX IF NOT EXISTS idx_events_community_type ON events (community_id, event_type_id) WHERE status = 'open';

-- 事件時間範圍 (快速查詢近期事件)
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events (created_at DESC) WHERE status = 'open';

-- 事件處理記錄 (快速查詢事件處理歷史)
CREATE INDEX IF NOT EXISTS idx_event_actions_event_id ON event_actions (event_id) WHERE event_actions.status = 'completed';

-- ============================================================================
-- 2. Meeting System Indexes
-- ============================================================================

-- 會議日期範圍 (快速查詢特定日期的會議)
CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings (date) WHERE meetings.status = 'scheduled';

-- 會議行動項目 (快速查詢待辦事項)
CREATE INDEX IF NOT EXISTS idx_meeting_action_items_owner ON meeting_action_items (owner) WHERE meeting_action_items.status = 'pending';

-- 會議語音段 (快速查詢會議內容)
CREATE INDEX IF NOT EXISTS idx_meeting_segments_meeting ON meeting_segments (meeting_id) WHERE meeting_segments.confidence > 0.8;

-- ============================================================================
-- 3. Notification System Indexes
-- ============================================================================

-- 通知目標角色 (快速查詢特定角色的通知)
CREATE INDEX IF NOT EXISTS idx_notices_target_roles ON notices (target_roles) WHERE notices.priority >= 3;

-- 通知送達記錄 (快速查詢送達狀態)
CREATE INDEX IF NOT EXISTS idx_notice_deliveries_status ON notice_deliveries (status) WHERE notice_deliveries.channel = 'line';

-- 通知模板 (快速查詢模板)
CREATE INDEX IF NOT EXISTS idx_notice_templates_active ON notice_templates (is_active) WHERE notice_templates.priority >= 2;

-- ============================================================================
-- 4. Property Management Indexes
-- ============================================================================

-- 物業工單 (快速查詢未解決工單)
CREATE INDEX IF NOT EXISTS idx_work_orders_status_priority ON work_orders (status, priority) DESC WHERE work_orders.status = 'open';

-- 物業收費記錄 (快速查詢收費狀態)
CREATE INDEX IF NOT EXISTS idx_fee_records_status ON fee_records (status) WHERE fee_records.period_end = CURRENT_DATE;

-- 物業工單分配 (快速查詢分配給特定人員的工單)
CREATE INDEX IF NOT EXISTS idx_work_orders_assigned ON work_orders (assigned_agent) WHERE work_orders.status = 'in_progress';

-- ============================================================================
-- 5. Security Management Indexes
-- ============================================================================

-- 保全巡邏記錄 (快速查詢巡邏狀態)
CREATE INDEX IF NOT EXISTS idx_patrol_logs_status ON patrol_logs (status) WHERE patrol_logs.agent_role = 'security';

-- 訪客記錄 (快速查詢訪客)
CREATE INDEX IF NOT EXISTS idx_visitor_logs_resident ON visitor_logs (resident_id) WHERE visitor_logs.entry_time > CURRENT_DATE;

-- 保全事件 (快速查詢未解決事件)
CREATE INDEX IF NOT EXISTS idx_security_events_status ON events (status) WHERE events.category = 'security';

-- ============================================================================
-- 6. Fire Safety Indexes
-- ============================================================================

-- 消防設備 (快速查詢異常設備)
CREATE INDEX IF NOT EXISTS idx_fire_equipment_status ON fire_equipment (status) WHERE fire_equipment.status IN ('warning', 'alarm', 'offline');

-- 消防事件 (快速查詢未解決事件)
CREATE INDEX IF NOT EXISTS idx_fire_events_severity ON fire_events (severity) WHERE fire_events.status = 'open';

-- ============================================================================
-- 7. Energy Management Indexes
-- ============================================================================

-- 能源設備 (快速查詢異常設備)
CREATE INDEX IF NOT EXISTS idx_energy_devices_status ON energy_devices (status) WHERE energy_devices.status IN ('error', 'offline', 'maintenance');

-- 能耗記錄 (快速查詢能耗數據)
CREATE INDEX IF NOT EXISTS idx_energy_readings_device ON energy_readings (device_id) WHERE energy_readings.reading_type = 'instant';

-- 節能策略 (快速查詢執行中的策略)
CREATE INDEX IF NOT EXISTS idx_energy_policies_active ON energy_policies (status) WHERE energy_policies.priority >= 3;

-- ============================================================================
-- 8. User & Audit Indexes
-- ============================================================================

-- 用戶社區關聯 (快速查詢用戶社區角色)
CREATE INDEX IF NOT EXISTS idx_user_community_roles_user ON user_community_roles (user_id) WHERE user_community_roles.role = 'admin';

-- 審計日誌 (快速查詢操作日誌)
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs (timestamp DESC) WHERE audit_logs.user_role = 'admin';

-- ============================================================================
-- 9. Composite Indexes for Complex Queries
-- ============================================================================

-- 事件查詢 (社區 + 類型 + 狀態)
CREATE INDEX IF NOT EXISTS idx_events_multi ON events (community_id, event_type_id, status) WHERE status = 'open';

-- 工單查詢 (社區 + 類型 + 狀態)
CREATE INDEX IF NOT EXISTS idx_work_orders_multi ON work_orders (community_id, category, status) WHERE status = 'open';

-- 通知查詢 (社區 + 優先級)
CREATE INDEX IF NOT EXISTS idx_notices_multi ON notices (community_id, priority) WHERE priority >= 2;

-- ============================================================================
-- 10. Partial Indexes for Common Queries
-- ============================================================================

-- 未解決事件 (快速查詢所有未解決事件)
CREATE INDEX IF NOT EXISTS idx_events_unresolved ON events (priority DESC) WHERE status = 'open';

-- 待處理工單 (快速查詢待處理工單)
CREATE INDEX IF NOT EXISTS idx_work_orders_pending ON work_orders (priority DESC) WHERE status = 'pending';

-- 緊急通知 (快速查詢緊急通知)
CREATE INDEX IF NOT EXISTS idx_notices_emergency ON notices (priority DESC) WHERE priority >= 3;

-- ============================================================================
-- 11. Unique Indexes for Data Integrity
-- ============================================================================

-- 住戶唯一識別 (社區 + 大樓 + 單位)
CREATE UNIQUE INDEX IF NOT EXISTS idx_residents_unique ON residents (community_id, building_id, unit_number) WHERE is_active;

-- 消防設備唯一識別 (社區 + 大樓 + 樓層 + 單位)
CREATE UNIQUE INDEX IF NOT EXISTS idx_fire_equipment_unique ON fire_equipment (community_id, building_id, floor_id, unit_number) WHERE status IN ('normal', 'warning', 'alarm');

-- 能源設備唯一識別 (社區 + 大樓 + 樓層 + 單位)
CREATE UNIQUE INDEX IF NOT EXISTS idx_energy_devices_unique ON energy_devices (community_id, building_id, floor_id, unit_number) WHERE status = 'active';

-- ============================================================================
-- 12. GIN Indexes for JSONB Fields
-- ============================================================================

-- 會議行動項目 (快速查詢行動項目)
CREATE INDEX IF NOT EXISTS idx_meeting_action_items_json ON meeting_action_items USING GIN ((action_items));

-- 會議筆記 (快速查詢會議筆記)
CREATE INDEX IF NOT EXISTS idx_meeting_notes_json ON meeting_notes USING GIN ((notes));

-- ============================================================================
-- 13. BRIN Indexes for Large Tables (Time-series Data)
-- ============================================================================

-- 能耗記錄時間序列 (快速查詢時間範圍)
CREATE INDEX IF NOT EXISTS idx_energy_readings_timestamp ON energy_readings (created_at DESC) USING brin WHERE reading_type = 'instant';

-- 審計日誌時間序列 (快速查詢時間範圍)
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp_brin ON audit_logs (timestamp DESC) USING brin WHERE user_role = 'admin';

-- ============================================================================
-- 14. Analyze Tables (Update Statistics)
-- ============================================================================

ANALYZE events;
ANALYZE meetings;
ANALYZE notices;
ANALYZE work_orders;
ANALYZE fire_equipment;
ANALYZE energy_devices;
ANALYZE energy_readings;
ANALYZE audit_logs;
ANALYZE user_community_roles;
