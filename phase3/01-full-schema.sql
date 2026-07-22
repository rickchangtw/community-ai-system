-- ============================================================================
-- 社區智慧管理系統 - PostgreSQL Schema
-- Phase 3: 完整資料庫結構
-- 日期: 2026-07-19
-- ============================================================================

-- 資料庫設定
CREATE DATABASE IF NOT EXISTS community;
\c community;

-- ============================================================================
-- 一、基礎資料 (Core Entities)
-- ============================================================================

-- 1.1 社區
CREATE TABLE IF NOT EXISTS communities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    manager_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 1.2 大樓
CREATE TABLE IF NOT EXISTS buildings (
    id SERIAL PRIMARY KEY,
    community_id INTEGER REFERENCES communities(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    location VARCHAR(100),
    total_units INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 1.3 樓層
CREATE TABLE IF NOT EXISTS floors (
    id SERIAL PRIMARY KEY,
    building_id INTEGER REFERENCES buildings(id) ON DELETE CASCADE,
    name VARCHAR(20) NOT NULL,
    floor_number INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 1.4 住戶
CREATE TABLE IF NOT EXISTS residents (
    id SERIAL PRIMARY KEY,
    community_id INTEGER REFERENCES communities(id) ON DELETE CASCADE,
    line_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    building_id INTEGER REFERENCES buildings(id) ON DELETE SET NULL,
    unit VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 1.5 聯絡方式
CREATE TABLE IF NOT EXISTS contact_methods (
    id SERIAL PRIMARY KEY,
    resident_id INTEGER REFERENCES residents(id) ON DELETE CASCADE,
    type VARCHAR(20),
    value VARCHAR(100) NOT NULL,
    PRIMARY KEY (resident_id, type)
);

-- ============================================================================
-- 二、Agent 角色 (Agent Roles & Instances)
-- ============================================================================

-- 2.1 Agent 角色
CREATE TABLE IF NOT EXISTS agent_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    capabilities TEXT[] DEFAULT '{}',
    permissions TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2.2 Agent 實例
CREATE TABLE IF NOT EXISTS agent_instances (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES agent_roles(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    config JSONB DEFAULT '{}',
    last_active TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 三、事件管理 (Event Management)
-- ============================================================================

-- 3.1 事件類型
CREATE TABLE IF NOT EXISTS event_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(20) NOT NULL,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3.2 事件
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    event_type_id INTEGER REFERENCES event_types(id) ON DELETE CASCADE,
    agent_instance_id INTEGER REFERENCES agent_instances(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(100)
);

-- 3.3 事件處理記錄
CREATE TABLE IF NOT EXISTS event_actions (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    agent_role VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3.4 事件時間線
CREATE TABLE IF NOT EXISTS event_timeline (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT NOW(),
    agent_role VARCHAR(50),
    action VARCHAR(50),
    description TEXT,
    status VARCHAR(20) DEFAULT 'info'
);

-- ============================================================================
-- 四、會議系統 (Meeting System)
-- ============================================================================

-- 4.1 會議
CREATE TABLE IF NOT EXISTS meetings (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    date TIMESTAMP NOT NULL,
    location VARCHAR(200),
    host VARCHAR(100),
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4.2 會議發言人
CREATE TABLE IF NOT EXISTS meeting_speakers (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    resident_name VARCHAR(100),
    line_id VARCHAR(50),
    role VARCHAR(50),
    topic VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4.3 語音段
CREATE TABLE IF NOT EXISTS voice_segments (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    speaker_name VARCHAR(100),
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    duration REAL NOT NULL,
    transcription TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4.4 行動項目
CREATE TABLE IF NOT EXISTS action_items (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    assigned_to VARCHAR(100),
    status VARCHAR(20) DEFAULT 'open',
    priority INTEGER DEFAULT 0,
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4.5 會議文件
CREATE TABLE IF NOT EXISTS meeting_files (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    file_name VARCHAR(200) NOT NULL,
    file_path TEXT,
    file_size INTEGER,
    file_type VARCHAR(50),
    uploaded_by VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 五、通知系統 (Notification System)
-- ============================================================================

-- 5.1 通知模板
CREATE TABLE IF NOT EXISTS notification_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    template_text TEXT,
    template_type VARCHAR(20) DEFAULT 'text',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5.2 通知
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    template_name VARCHAR(100) REFERENCES notification_templates(name),
    priority VARCHAR(20) DEFAULT 'normal',
    target_roles TEXT[] DEFAULT '{}',
    target_residents TEXT[] DEFAULT '{}',
    sent_at TIMESTAMP DEFAULT NOW(),
    delivery_status VARCHAR(20) DEFAULT 'pending'
);

-- 5.3 送達記錄
CREATE TABLE IF NOT EXISTS delivery_records (
    id SERIAL PRIMARY KEY,
    notification_id INTEGER REFERENCES notifications(id) ON DELETE CASCADE,
    recipient VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    delivered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 六、物業管理 (Property Management)
-- ============================================================================

-- 6.1 收費項目
CREATE TABLE IF NOT EXISTS fee_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    amount DECIMAL(10, 2),
    frequency VARCHAR(20) DEFAULT 'monthly',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6.2 收費記錄
CREATE TABLE IF NOT EXISTS fee_records (
    id SERIAL PRIMARY KEY,
    resident_id INTEGER REFERENCES residents(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES fee_categories(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    period_start DATE,
    period_end DATE,
    status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6.3 工單
CREATE TABLE IF NOT EXISTS work_orders (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    location VARCHAR(200),
    status VARCHAR(20) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'normal',
    assigned_to VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- ============================================================================
-- 七、保全管理 (Security Management)
-- ============================================================================

-- 7.1 巡邏路線
CREATE TABLE IF NOT EXISTS patrol_routes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    waypoints JSONB NOT NULL DEFAULT '[]',
    duration_minutes INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7.2 巡邏記錄
CREATE TABLE IF NOT EXISTS patrol_records (
    id SERIAL PRIMARY KEY,
    route_id INTEGER REFERENCES patrol_routes(id) ON DELETE CASCADE,
    officer_name VARCHAR(100) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    status VARCHAR(20) DEFAULT 'in_progress',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7.3 訪客記錄
CREATE TABLE IF NOT EXISTS visitor_logs (
    id SERIAL PRIMARY KEY,
    resident_name VARCHAR(100),
    visitor_name VARCHAR(100) NOT NULL,
    visitor_phone VARCHAR(20),
    purpose TEXT,
    host_id INTEGER REFERENCES residents(id) ON DELETE SET NULL,
    check_in_time TIMESTAMP DEFAULT NOW(),
    check_out_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 八、消防管理 (Fire Safety)
-- ============================================================================

-- 8.1 消防設備
CREATE TABLE IF NOT EXISTS fire_equipment (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(200),
    serial_number VARCHAR(100),
    inspection_date DATE,
    next_inspection_date DATE,
    status VARCHAR(20) DEFAULT 'normal',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8.2 消防事件
CREATE TABLE IF NOT EXISTS fire_incidents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    location VARCHAR(200),
    severity VARCHAR(20) DEFAULT 'low',
    status VARCHAR(20) DEFAULT 'reported',
    reported_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 九、節能管理 (Energy Management)
-- ============================================================================

-- 9.1 能源設備
CREATE TABLE IF NOT EXISTS energy_devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(200),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    power_rating REAL,
    status VARCHAR(20) DEFAULT 'active',
    last_reading DATE,
    last_reading_value REAL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 9.2 能耗記錄
CREATE TABLE IF NOT EXISTS energy_readings (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES energy_devices(id) ON DELETE CASCADE,
    reading_date DATE NOT NULL,
    reading_value REAL NOT NULL,
    unit VARCHAR(20) DEFAULT 'kWh',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 9.3 節能策略
CREATE TABLE IF NOT EXISTS energy_strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    target_saving REAL,
    status VARCHAR(20) DEFAULT 'active',
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 十、用戶認證 (User Authentication)
-- ============================================================================

-- 10.1 用戶帳號
CREATE TABLE IF NOT EXISTS user_accounts (
    id SERIAL PRIMARY KEY,
    line_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 10.2 通知偏好
CREATE TABLE IF NOT EXISTS notification_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user_accounts(id) ON DELETE CASCADE,
    notification_type VARCHAR(20) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    priority_level VARCHAR(20) DEFAULT 'normal',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 十一、審計日誌 (Audit Log)
-- ============================================================================

-- 11.1 操作日誌
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    agent_instance_id INTEGER REFERENCES agent_instances(id) ON DELETE SET NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    old_value JSONB,
    new_value JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 審計日誌索引
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_resource_type ON audit_log(resource_type);

-- ============================================================================
-- 十二、系統配置 (System Config)
-- ============================================================================

-- 12.1 系統參數
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 十三、設備註冊 (Device Registry)
-- ============================================================================

-- 13.1 IoT 設備
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    serial_number VARCHAR(100) UNIQUE,
    mac_address VARCHAR(17),
    ip_address VARCHAR(45),
    location VARCHAR(200),
    status VARCHAR(20) DEFAULT 'active',
    last_seen TIMESTAMP,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 索引 (Indexes)
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_communities_name ON communities(name);
CREATE INDEX IF NOT EXISTS idx_buildings_community ON buildings(community_id);
CREATE INDEX IF NOT EXISTS idx_floors_building ON floors(building_id);
CREATE INDEX IF NOT EXISTS idx_residents_line_id ON residents(line_id);
CREATE INDEX IF NOT EXISTS idx_residents_community ON residents(community_id);
CREATE INDEX IF NOT EXISTS idx_agent_instances_role ON agent_instances(role_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type_id);
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(date);
CREATE INDEX IF NOT EXISTS idx_notifications_target ON notifications(target_roles);
CREATE INDEX IF NOT EXISTS idx_delivery_records_status ON delivery_records(status);
CREATE INDEX IF NOT EXISTS idx_fee_records_resident ON fee_records(resident_id);

-- ============================================================================
-- 數據種子 (Sample Data)
-- ============================================================================

-- 社區
INSERT INTO communities (name, address, phone, manager_name) VALUES
('幸福社區', '台北市大安區安和路1號', '02-2345-6789', '張經理'),
('祥和花園', '台北市信義區信義路500號', '02-8765-4321', '李經理');

-- 大樓
INSERT INTO buildings (community_id, name, location, total_units) VALUES
(1, 'A大樓', 'A區', 300),
(1, 'B大樓', 'B區', 300),
(2, 'C大樓', 'C區', 300),
(2, 'D大樓', 'D區', 300);

-- 樓層
INSERT INTO floors (building_id, name, floor_number) VALUES
(1, '1F', 1),
(1, '2F', 2),
(1, '3F', 3),
(1, 'B1', -1),
(2, '1F', 1),
(2, '2F', 2),
(2, '3F', 3),
(2, 'B1', -1);

-- 住戶
INSERT INTO residents (community_id, line_id, name, building_id, unit, phone) VALUES
(1, 'U1234567890123456789', '張媽媽', 1, '101', '0912-345-678'),
(1, 'U2345678901234567890', '李伯伯', 1, '205', '0923-456-789'),
(1, 'U3456789012345678901', '王阿姨', 2, '308', '0934-567-890'),
(2, 'U4567890123456789012', '趙叔叔', 2, '112', '0945-678-901');

-- Agent 角色
INSERT INTO agent_roles (name, description, capabilities, permissions) VALUES
('總幹事', '社區總管理', '{"manage": true, "approve": true}', '{"admin": true}'),
('物業', '物業管理', '{"maintenance": true, "billing": true}', '{"property": true}'),
('保全', '保全管理', '{"security": true, "patrol": true}', '{"security": true}'),
('消防', '消防管理', '{"fire_safety": true, "inspection": true}', '{"fire": true}'),
('節能', '節能管理', '{"energy": true, "monitoring": true}', '{"energy": true}'),
('通知', '通知中心', '{"notification": true, "broadcast": true}', '{"notification": true}');

-- Agent 實例
INSERT INTO agent_instances (role_id, name, status, config) VALUES
(1, '總幹事-張經理', 'active', '{"port": 3021}'),
(2, '物業-王阿姨', 'active', '{"port": 3022}'),
(3, '保全-李伯伯', 'active', '{"port": 3023}'),
(4, '消防-趙叔叔', 'active', '{"port": 3024}'),
(5, '節能-張媽媽', 'active', '{"port": 3025}'),
(6, '通知-系統', 'active', '{"port": 3026}');

-- 事件類型
INSERT INTO event_types (name, description, category, priority) VALUES
('會議', '社區會議', 'meeting', 1),
('維修', '維修工單', 'maintenance', 2),
('緊急', '緊急事件', 'emergency', 5),
('通知', '一般通知', 'notification', 1),
('訪客', '訪客登記', 'visitor', 3);

-- 通知模板
INSERT INTO notification_templates (name, description, template_text, template_type) VALUES
('會議通知', '社區會議通知', '📋 社區會議通知\n\n📅 日期：{date}\n🕐 時間：{time}\n📍 地點：社區活动中心\n👥 主持人：{host}\n\n請準時出席！', 'text'),
('緊急通知', '緊急事件通知', '🚨 緊急通知\n\n{title}\n\n{content}\n\n請立即處理！', 'text'),
('維修通知', '維修工單通知', '🔧 維修通知\n\n📝 項目：{item}\n🕐 時間：{time}\n📍 地點：{location}\n\n請配合施工！', 'text');

-- 系統配置
INSERT INTO system_config (key, value, description) VALUES
('system.name', '幸福社區智慧管理系統', '系統名稱'),
('system.version', '1.0.0', '系統版本'),
('system.port', '3021', '系統端口'),
('database.host', 'localhost', '資料庫主機'),
('database.port', '5432', '資料庫端口');

-- 消防設備
INSERT INTO fire_equipment (name, type, location, status) VALUES
('A大樓1F 消火栓', 'hydrant', 'A大樓1F走廊', 'normal'),
('A大樓2F 煙霧探測器', 'smoke_detector', 'A大樓2F走廊', 'normal'),
('A大樓3F 滅火器', 'extinguisher', 'A大樓3F走廊', 'normal');

-- 能源設備
INSERT INTO energy_devices (name, type, location, power_rating) VALUES
('A大樓電梯', 'elevator', 'A大樓', 15.0),
('B大樓電梯', 'elevator', 'B大樓', 15.0),
('公共照明', 'lighting', '公共區域', 5.0),
('停車場照明', 'lighting', '停車場', 3.0);

-- 節能策略
INSERT INTO energy_strategies (name, description, target_saving) VALUES
('電梯節能模式', '電梯節能運行', 10.0),
('照明感應器', '公共照明感應控制', 15.0),
('停車場照明', '停車場照明優化', 20.0);

-- ============================================================================
-- 函數 (Functions)
-- ============================================================================

-- 審計日誌函數
CREATE OR REPLACE FUNCTION log_audit(
    p_action VARCHAR,
    p_user_id INTEGER DEFAULT NULL,
    p_agent_instance_id INTEGER DEFAULT NULL,
    p_resource_type VARCHAR DEFAULT NULL,
    p_resource_id INTEGER DEFAULT NULL,
    p_old_value JSONB DEFAULT NULL,
    p_new_value JSONB DEFAULT NULL,
    p_ip_address VARCHAR DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO audit_log (
        action, user_id, agent_instance_id, resource_type, resource_id,
        old_value, new_value, ip_address, created_at
    ) VALUES (
        p_action, p_user_id, p_agent_instance_id, p_resource_type, p_resource_id,
        p_old_value, p_new_value, p_ip_address, NOW()
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 完成
-- ============================================================================

SELECT 'Phase 3 完整 Schema 建立成功' AS status;
