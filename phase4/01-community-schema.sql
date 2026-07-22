-- ============================================================================
-- 社區智慧管理系統 - PostgreSQL Schema
-- Phase 4: 資料庫結構設計
-- 日期: 2026-07-18
-- ============================================================================

-- 資料庫配置
-- DB_CONFIG = {
--   "host": "localhost",
--   "port": 5432,
--   "dbname": "community",
--   "user": "hermes",
--   "password": "hermes123"
-- }

-- ============================================================================
-- 1. 基礎資料模型 (Master Data)
-- ============================================================================

-- 社區主資料
CREATE TABLE IF NOT EXISTS communities (
    community_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(200),
    manager_name VARCHAR(100),
    manager_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 大樓
CREATE TABLE IF NOT EXISTS buildings (
    building_id VARCHAR(50) PRIMARY KEY,
    community_id VARCHAR(50) REFERENCES communities(community_id),
    name VARCHAR(200) NOT NULL,
    address VARCHAR(200),
    floors INTEGER DEFAULT 0,
    total_units INTEGER DEFAULT 0,
    type VARCHAR(50) DEFAULT 'residential',  -- residential, commercial, mixed
    created_at TIMESTAMP DEFAULT NOW()
);

-- 樓層
CREATE TABLE IF NOT EXISTS floors (
    floor_id VARCHAR(50) PRIMARY KEY,
    building_id VARCHAR(50) REFERENCES buildings(building_id),
    name VARCHAR(50) NOT NULL,        -- 1F, 2F, ... B1, ...
    floor_number INTEGER NOT NULL,     -- 1, 2, -1, ...
    floor_type VARCHAR(20) DEFAULT 'residential',  -- residential, commercial, parking, equipment
    created_at TIMESTAMP DEFAULT NOW()
);

-- 住戶
CREATE TABLE IF NOT EXISTS residents (
    resident_id VARCHAR(50) PRIMARY KEY,
    community_id VARCHAR(50) REFERENCES communities(community_id),
    building_id VARCHAR(50) REFERENCES buildings(building_id),
    floor_id VARCHAR(50) REFERENCES floors(floor_id),
    unit_number VARCHAR(20) NOT NULL,     -- 101, 202, ...
    name VARCHAR(100) NOT NULL,
    id_number VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 住戶聯絡方式
CREATE TABLE IF NOT EXISTS resident_contacts (
    contact_id SERIAL PRIMARY KEY,
    resident_id VARCHAR(50) REFERENCES residents(resident_id),
    phone VARCHAR(20),
    email VARCHAR(200),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(resident_id, phone)
);

-- ============================================================================
-- 2. 6 個 Agent 角色定義
-- ============================================================================

-- Agent 角色
CREATE TABLE IF NOT EXISTS agent_roles (
    role_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 0,     -- 執行優先級 0-100
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6 個核心 Agent 角色
INSERT INTO agent_roles (role_id, name, title, description, priority) VALUES
    ('ceo', '總幹事', 'Chief Executive Officer', '社區整體管理、決策、協調', 100),
    ('property', '物業管理', 'Property Manager', '社區維護、設施管理、收費', 90),
    ('security', '保全管理', 'Security Manager', '安全巡邏、事件處理、訪客管理', 85),
    ('fire', '消防管理', 'Fire Safety Manager', '消防設備、緊急演練、通報', 80),
    ('energy', '節能管理', 'Energy Manager', '能源管理、設備監控、節能策略', 75),
    ('notice', '通知中心', 'Notice Center', '公告發布、訊息推送、通知管理', 70);

-- Agent 執行者 (Agent 實例)
CREATE TABLE IF NOT EXISTS agent_instances (
    instance_id VARCHAR(50) PRIMARY KEY,
    role_id VARCHAR(50) REFERENCES agent_roles(role_id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',  -- active, standby, error, offline
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 預設 Agent 實例
INSERT INTO agent_instances (instance_id, role_id, name, description, status) VALUES
    ('ceo-a1', 'ceo', '總幹事 Agent A1', '主總幹事', 'active'),
    ('property-a1', 'property', '物業管理 Agent A1', '物業管理主 Agent', 'active'),
    ('security-a1', 'security', '保全管理 Agent A1', '保全管理主 Agent', 'active'),
    ('fire-a1', 'fire', '消防管理 Agent A1', '消防管理主 Agent', 'active'),
    ('energy-a1', 'energy', '節能管理 Agent A1', '節能管理主 Agent', 'active'),
    ('notice-a1', 'notice', '通知中心 Agent A1', '通知中心主 Agent', 'active');

-- ============================================================================
-- 3. 事件管理系統
-- ============================================================================

-- 事件類型
CREATE TABLE IF NOT EXISTS event_types (
    type_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),  -- incident, maintenance, security, fire, energy, notice
    priority INTEGER DEFAULT 0,  -- 0=低, 1=中, 2=高, 3=緊急
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 事件
CREATE TABLE IF NOT EXISTS events (
    event_id VARCHAR(50) PRIMARY KEY,
    community_id VARCHAR(50) REFERENCES communities(community_id),
    building_id VARCHAR(50) REFERENCES buildings(building_id),
    floor_id VARCHAR(50) REFERENCES floors(floor_id),
    event_type_id VARCHAR(50) REFERENCES event_types(type_id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'open',  -- open, in_progress, resolved, closed
    priority INTEGER DEFAULT 0,
    reported_by VARCHAR(100),
    reported_at TIMESTAMP DEFAULT NOW(),
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 事件處理記錄
CREATE TABLE IF NOT EXISTS event_actions (
    action_id SERIAL PRIMARY KEY,
    event_id VARCHAR(50) REFERENCES events(event_id),
    agent_role VARCHAR(50),
    action_description TEXT,
    action_taken TIMESTAMP DEFAULT NOW(),
    result TEXT,
    notes TEXT
);

-- 事件時間線
CREATE TABLE IF NOT EXISTS event_timeline (
    timeline_id SERIAL PRIMARY KEY,
    event_id VARCHAR(50) REFERENCES events(event_id),
    timestamp TIMESTAMP DEFAULT NOW(),
    agent_role VARCHAR(50),
    message TEXT NOT NULL,
    attachment_path TEXT
);

-- ============================================================================
-- 4. 會議系統 (擴展版)
-- ============================================================================

-- 會議
CREATE TABLE IF NOT EXISTS meetings (
    meeting_id VARCHAR(50) PRIMARY KEY,
    community_id VARCHAR(50) REFERENCES communities(community_id),
    title VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    time_start TIME NOT NULL,
    time_end TIME NOT NULL,
    location VARCHAR(200) DEFAULT '社區活动中心',
    host VARCHAR(100) NOT NULL,
    agenda JSONB,
    action_items JSONB,
    notes JSONB,
    recorded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 會議發言人
CREATE TABLE IF NOT EXISTS meeting_speakers (
    id SERIAL PRIMARY KEY,
    meeting_id VARCHAR(50) REFERENCES meetings(meeting_id),
    speaker_name VARCHAR(100) NOT NULL,
    speaker_unit VARCHAR(20),
    speaker_role VARCHAR(100),
    resident_id VARCHAR(50) REFERENCES residents(resident_id),
    voice_profile_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_meeting_speakers_role ON meeting_speakers (speaker_role);

-- 會議語音段
CREATE TABLE IF NOT EXISTS meeting_segments (
    id SERIAL PRIMARY KEY,
    meeting_id VARCHAR(50) REFERENCES meetings(meeting_id),
    speaker_id INTEGER REFERENCES meeting_speakers(id),
    start REAL NOT NULL,
    end REAL NOT NULL,
    text TEXT NOT NULL,
    confidence REAL DEFAULT 0.0
);

-- 會議行動項目
CREATE TABLE IF NOT EXISTS meeting_action_items (
    id SERIAL PRIMARY KEY,
    meeting_id VARCHAR(50) REFERENCES meetings(meeting_id),
    item TEXT NOT NULL,
    owner VARCHAR(100),
    owner_resident_id VARCHAR(50) REFERENCES residents(resident_id),
    deadline DATE,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, in_progress, completed, cancelled
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_meeting_action_items_owner ON meeting_action_items (owner);
CREATE INDEX IF NOT EXISTS idx_meeting_action_items_status ON meeting_action_items (status);

-- 會議文件
CREATE TABLE IF NOT EXISTS meeting_files (
    id SERIAL PRIMARY KEY,
    meeting_id VARCHAR(50) REFERENCES meetings(meeting_id),
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50) DEFAULT 'audio',  -- audio, video, document, image
    file_size BIGINT,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 會議筆記
CREATE TABLE IF NOT EXISTS meeting_notes (
    id SERIAL PRIMARY KEY,
    meeting_id VARCHAR(50) REFERENCES meetings(meeting_id),
    note TEXT NOT NULL,
    note_type VARCHAR(50) DEFAULT 'general',  -- general, decision, action, discussion
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_meeting_notes_created_by ON meeting_notes (created_by);

-- ============================================================================
-- 5. 通知系統
-- ============================================================================

-- 通知模板
CREATE TABLE IF NOT EXISTS notice_templates (
    template_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    content_template JSONB,  -- 包含變數佔位符
    target_roles VARCHAR(50)[] DEFAULT '{}',  -- 目標角色
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 通知
CREATE TABLE IF NOT EXISTS notices (
    notice_id VARCHAR(50) PRIMARY KEY,
    community_id VARCHAR(50) REFERENCES communities(community_id),
    template_id VARCHAR(50) REFERENCES notice_templates(template_id),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    content_json JSONB,
    priority INTEGER DEFAULT 0,
    target_roles VARCHAR(50)[] DEFAULT '{}',  -- 目標角色
    target_residents VARCHAR(50)[] DEFAULT '{}',  -- 目標住戶
    sent_at TIMESTAMP,
    read_by VARCHAR(50)[],  -- 已讀住戶
    created_at TIMESTAMP DEFAULT NOW()
);

-- 通知送達記錄
CREATE TABLE IF NOT EXISTS notice_deliveries (
    delivery_id SERIAL PRIMARY KEY,
    notice_id VARCHAR(50) REFERENCES notices(notice_id),
    recipient VARCHAR(100),
    recipient_type VARCHAR(20),  -- resident, agent, system
    channel VARCHAR(50),  -- telegram, line, sms, push
    status VARCHAR(20) DEFAULT 'pending',  -- pending, sent, delivered, failed
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    error_message TEXT
);

-- ============================================================================
-- 6. 物業管理系統
-- ============================================================================

-- 物業收費項目
CREATE TABLE IF NOT EXISTS fee_categories (
    category_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    unit VARCHAR(50),  -- 元/月, 元/坪/月, 元/次
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 收費記錄
CREATE TABLE IF NOT EXISTS fee_records (
    record_id VARCHAR(50) PRIMARY KEY,
    community_id VARCHAR(50) REFERENCES communities(community_id),
    building_id VARCHAR(50) REFERENCES buildings(building_id),
    floor_id VARCHAR(50) REFERENCES floors(floor_id),
    resident_id VARCHAR(50) REFERENCES residents(resident_id),
    category_id VARCHAR(50) REFERENCES fee_categories(category_id),
    amount NUMERIC(10, 2),
    period_start DATE,
    period_end DATE,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, paid, overdue, cancelled
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 物業工單
CREATE TABLE IF NOT EXISTS work_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    community_id VARCHAR(50) REFERENCES communities(community_id),
    building_id VARCHAR(50) REFERENCES buildings(building_id),
    floor_id VARCHAR(50) REFERENCES floors(floor_id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),  -- maintenance, repair, cleaning, painting, electrical, plumbing
    priority INTEGER DEFAULT 0,
    assigned_to VARCHAR(100),
    assigned_agent VARCHAR(50),
    status VARCHAR(20) DEFAULT 'open',  -- open, in_progress, completed, cancelled
    estimated_hours NUMERIC(5, 2),
    actual_hours NUMERIC(5, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 7. 保全管理系統
-- ============================================================================

-- 巡邏路線
CREATE TABLE IF NOT EXISTS patrol_routes (
    route_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    community_id VARCHAR(50) REFERENCES communities(community_id),
    building_id VARCHAR(50) REFERENCES buildings(building_id),
    duration_minutes INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 巡邏記錄
CREATE TABLE IF NOT EXISTS patrol_logs (
    log_id SERIAL PRIMARY KEY,
    route_id VARCHAR(50) REFERENCES patrol_routes(route_id),
    agent_name VARCHAR(100),
    agent_role VARCHAR(50),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'in_progress',  -- in_progress, completed, aborted
    checkpoints_completed INTEGER DEFAULT 0,
    total_checkpoints INTEGER,
    notes TEXT
);

-- 訪客記錄
CREATE TABLE IF NOT EXISTS visitor_logs (
    visitor_id VARCHAR(50) PRIMARY KEY,
    community_id VARCHAR(50) REFERENCES communities(community_id),
    building_id VARCHAR(50) REFERENCES buildings(building_id),
    resident_id VARCHAR(50) REFERENCES residents(resident_id),  -- 預約住戶
    visitor_name VARCHAR(100) NOT NULL,
    visitor_phone VARCHAR(20),
    visitor_id_number VARCHAR(20),
    visit_reason TEXT,
    entry_time TIMESTAMP,
    exit_time TIMESTAMP,
    check_in_by VARCHAR(100),
    check_out_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 8. 消防管理系統
-- ============================================================================

-- 消防設備
CREATE TABLE IF NOT EXISTS fire_equipment (
    equipment_id VARCHAR(50) PRIMARY KEY,
    community_id VARCHAR(50) REFERENCES communities(community_id),
    building_id VARCHAR(50) REFERENCES buildings(building_id),
    floor_id VARCHAR(50) REFERENCES floors(floor_id),
    unit_number VARCHAR(20),
    equipment_type VARCHAR(50),  -- sprinkler, hydrant, alarm, extinguisher, panel, camera
    name VARCHAR(200),
    serial_number VARCHAR(100),
    status VARCHAR(20) DEFAULT 'normal',  -- normal, warning, alarm, offline, maintenance
    last_inspection DATE,
    next_inspection DATE,
    inspection_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 消防事件
CREATE TABLE IF NOT EXISTS fire_events (
    event_id VARCHAR(50) PRIMARY KEY,
    community_id VARCHAR(50) REFERENCES communities(community_id),
    building_id VARCHAR(50) REFERENCES buildings(building_id),
    floor_id VARCHAR(50) REFERENCES floors(floor_id),
    event_type VARCHAR(50),  -- alarm, inspection, drill, incident
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity VARCHAR(20) DEFAULT 'low',  -- low, medium, high, critical
    status VARCHAR(20) DEFAULT 'open',
    reported_by VARCHAR(100),
    reported_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 9. 節能管理系統
-- ============================================================================

-- 能源設備
CREATE TABLE IF NOT EXISTS energy_devices (
    device_id VARCHAR(50) PRIMARY KEY,
    community_id VARCHAR(50) REFERENCES communities(community_id),
    building_id VARCHAR(50) REFERENCES buildings(building_id),
    floor_id VARCHAR(50) REFERENCES floors(floor_id),
    unit_number VARCHAR(20),
    device_type VARCHAR(50),  -- meter, sensor, actuator, inverter, pump, hvac
    name VARCHAR(200),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    manufacturer VARCHAR(200),
    install_date DATE,
    location TEXT,
    status VARCHAR(20) DEFAULT 'active',  -- active, offline, maintenance, error
    protocol VARCHAR(50),  -- modbus, bacnet, mqtt, tcp/ip
    port INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 能耗記錄
CREATE TABLE IF NOT EXISTS energy_readings (
    reading_id VARCHAR(50) PRIMARY KEY,
    device_id VARCHAR(50) REFERENCES energy_devices(device_id),
    timestamp TIMESTAMP DEFAULT NOW(),
    value NUMERIC(10, 4),
    unit VARCHAR(50),  -- kWh, kW, °C, L/min
    reading_type VARCHAR(20) DEFAULT 'instant',  -- instant, cumulative, interval
    quality VARCHAR(20) DEFAULT 'good',  -- good, suspect, bad
    created_at TIMESTAMP DEFAULT NOW()
);

-- 節能策略
CREATE TABLE IF NOT EXISTS energy_policies (
    policy_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    target_devices VARCHAR(50)[] DEFAULT '{}',
    schedule JSONB,  -- cron 排程
    parameters JSONB,  -- 策略參數
    status VARCHAR(20) DEFAULT 'active',  -- active, inactive, paused
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 10. 權限與角色管理
-- ============================================================================

-- 系統角色
CREATE TABLE IF NOT EXISTS system_roles (
    role_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]',  -- 權限列表
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 用戶帳號
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    email VARCHAR(200),
    phone VARCHAR(20),
    role_id VARCHAR(50) REFERENCES system_roles(role_id),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 用戶-社區關聯
CREATE TABLE IF NOT EXISTS user_community_roles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    community_id VARCHAR(50) REFERENCES communities(community_id),
    role VARCHAR(50),  -- admin, manager, resident, staff
    granted_at TIMESTAMP DEFAULT NOW()
);

-- 操作日誌
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_id VARCHAR(50),
    user_role VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(50),
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT
);

-- ============================================================================
-- 11. 索引與最佳化
-- ============================================================================

-- 常用查詢索引
CREATE INDEX IF NOT EXISTS idx_events_community ON events (community_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events (event_type_id);
CREATE INDEX IF NOT EXISTS idx_events_status ON events (status);
CREATE INDEX IF NOT EXISTS idx_events_priority ON events (priority DESC);
CREATE INDEX IF NOT EXISTS idx_events_created ON events (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_meetings_community ON meetings (community_id);
CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings (date DESC);
CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings (recorded);

CREATE INDEX IF NOT EXISTS idx_notices_community ON notices (community_id);
CREATE INDEX IF NOT EXISTS idx_notices_priority ON notices (priority DESC);
CREATE INDEX IF NOT EXISTS idx_notices_sent ON notices (sent_at);

CREATE INDEX IF NOT EXISTS idx_fees_resident ON fee_records (resident_id);
CREATE INDEX IF NOT EXISTS idx_fees_period ON fee_records (period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_fees_status ON fee_records (status);

CREATE INDEX IF NOT EXISTS idx_work_orders_community ON work_orders (community_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_status ON work_orders (status);
CREATE INDEX IF NOT EXISTS idx_work_orders_priority ON work_orders (priority DESC);

CREATE INDEX IF NOT EXISTS idx_fire_equipment_community ON fire_equipment (community_id);
CREATE INDEX IF NOT EXISTS idx_fire_equipment_status ON fire_equipment (status);
CREATE INDEX IF NOT EXISTS idx_fire_equipment_next_inspection ON fire_equipment (next_inspection);

CREATE INDEX IF NOT EXISTS idx_energy_devices_community ON energy_devices (community_id);
CREATE INDEX IF NOT EXISTS idx_energy_devices_status ON energy_devices (status);

CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs (action);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs (timestamp DESC);

-- ============================================================================
-- 12. 預設資料
-- ============================================================================

-- 系統角色
INSERT INTO system_roles (role_id, name, description, permissions) VALUES
    ('admin', '系統管理員', '完整系統管理權限', '["*"]'),
    ('agent', 'Agent 執行者', 'Agent 角色執行權限', '["agent.execute", "agent.read"]'),
    ('manager', '社區管理員', '社區管理權限', '["community.manage", "resident.manage"]'),
    ('resident', '住戶', '住戶基本權限', '["resident.read_own", "notice.read"]'),
    ('visitor', '訪客', '訪客基本權限', '["visitor.read"]');

-- 事件類型
INSERT INTO event_types (type_id, name, description, category, priority) VALUES
    ('incident', '事件', '一般事件', 'incident', 1),
    ('maintenance', '維修', '設施維修', 'maintenance', 1),
    ('security', '安全', '安全事件', 'security', 2),
    ('fire', '消防', '消防事件', 'fire', 2),
    ('energy', '能源', '能源異常', 'energy', 1),
    ('notice', '通知', '公告通知', 'notice', 0);

-- 收費類別
INSERT INTO fee_categories (category_id, name, description, unit) VALUES
    ('management_fee', '管理費', '社區管理費', '元/月'),
    ('water_fee', '水費', '水費', '元/月'),
    ('electricity_fee', '電費', '電費', '元/月'),
    ('garbage_fee', '清潔費', '清潔費', '元/月'),
    ('parking_fee', '停車費', '停車費', '元/月'),
    ('repair_fee', '維修費', '維修費', '元/次');

-- 消防設備類型
INSERT INTO fire_equipment (equipment_type, name) VALUES
    ('sprinkler', '灑水頭'),
    ('hydrant', '消防栓'),
    ('alarm', '火警警報'),
    ('extinguisher', '滅火器'),
    ('panel', '消防控制面板'),
    ('camera', '攝影機'),
    ('emergency_light', '緊急照明'),
    ('evacuation_sign', '逃生指示標牌');

-- 能源設備類型
INSERT INTO energy_devices (device_type, name) VALUES
    ('meter', '電表'),
    ('sensor', '感測器'),
    ('actuator', '執行器'),
    ('inverter', '逆變器'),
    ('pump', '水泵'),
    ('hvac', '空調'),
    ('light', '照明'),
    ('elevator', '電梯');

-- 物業工單類別
INSERT INTO work_orders (category, name) VALUES
    ('maintenance', '維修'),
    ('repair', '修理'),
    ('cleaning', '清潔'),
    ('painting', '油漆'),
    ('electrical', '電氣'),
    ('plumbing', '管線');
