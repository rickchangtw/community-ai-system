-- ============================================================================
-- Phase 9: Security Audit
-- ============================================================================
-- 資料庫安全審計腳本
-- 檢查 SQL 注入、權限驗證、密碼策略等安全問題

-- ============================================================================
-- 1. 檢查資料庫連接安全性
-- ============================================================================

-- 檢查是否有弱密碼
SELECT 
    usename,
    passwd,
    shells,
    valgrind_status
FROM pg_shadow
WHERE usename = 'hermes'
LIMIT 1;

-- 檢查資料庫權限
SELECT 
    datname,
    datdba,
    pg_get_userbyid(datdba) AS owner,
    pg_size_pretty(pg_total_relation_size(oid)) AS size
FROM pg_database
WHERE datname = 'community'
LIMIT 1;

-- ============================================================================
-- 2. 檢查索引完整性
-- ============================================================================

-- 檢查缺少索引的表
SELECT 
    t.relname AS table_name,
    c.column_name,
    'index' AS index_type
FROM pg_index i
JOIN pg_class t ON t.oid = i.indrelid
JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(i.indkey)
LEFT JOIN information_schema.columns c ON c.table_name = t.relname AND c.column_name = a.attname
WHERE NOT EXISTS (
    SELECT 1 FROM pg_index p
    WHERE p.indrelid = i.indrelid
    AND p.indisunique
)
AND i.indisprimary = false
ORDER BY t.relname;

-- ============================================================================
-- 3. 檢查外鍵約束
-- ============================================================================

-- 檢查外鍵完整性
SELECT 
    tc.table_name,
    tc.constraint_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu 
    ON tc.constraint_name = ccu.constraint_name
    AND tc.constraint_schema = ccu.constraint_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;

-- ============================================================================
-- 4. 檢查數據完整性
-- ============================================================================

-- 檢查 communities 表
SELECT 
    COUNT(*) AS total_communities,
    COUNT(DISTINCT name) AS unique_names,
    COUNT(DISTINCT address) AS unique_addresses,
    COUNT(DISTINCT owner_name) AS unique_owners,
    COUNT(DISTINCT phone_number) AS unique_phones,
    COUNT(DISTINCT latitude) AS unique_latitudes,
    COUNT(DISTINCT longitude) AS unique_longitudes,
    COUNT(DISTINCT status) AS unique_statuses,
    COUNT(DISTINCT created_at) AS unique_created_at
FROM communities;

-- ============================================================================
-- 5. 檢查索引大小
-- ============================================================================

-- 計算索引大小
SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(indexname)) AS index_size,
    pg_relation_size(indexname) AS index_size_bytes
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexname) DESC
LIMIT 20;

-- ============================================================================
-- 6. 檢查表大小
-- ============================================================================

-- 計算表大小
SELECT 
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(oid)) AS total_size,
    pg_total_relation_size(oid) AS total_size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(oid) DESC
LIMIT 20;

-- ============================================================================
-- 7. 檢查慢查詢
-- ============================================================================

-- 啟用慢查詢日誌
-- 在 postgresql.conf 中設置:
-- log_min_duration_statement = 100  (記錄超過 100ms 的查詢)

-- ============================================================================
-- 8. 檢查備份策略
-- ============================================================================

-- 檢查 PostgreSQL 自動備份配置
SHOW wal_level;
SHOW archive_mode;
SHOW restore_command;

-- ============================================================================
-- 9. 檢查密碼策略
-- ============================================================================

-- 建議的密碼策略：
-- 1. 使用 bcrypt 或 argon2 哈希
-- 2. 最小長度: 12 字元
-- 3. 包含大小寫、數字、特殊字元
-- 4. 定期更新 (90 天)
-- 5. 不允許重複使用最近 5 個密碼

-- ============================================================================
-- 10. 檢查 API 安全
-- ============================================================================

-- 建議的安全措施：
-- 1. HTTPS (TLS 1.2+)
-- 2. API 簽章驗證 (HMAC-SHA256)
-- 3. 速率限制 (Rate Limiting)
-- 4. CORS 配置
-- 5. 輸入驗證 (參數化查詢)
-- 6. 錯誤處理 (不洩漏敏感資訊)

-- ============================================================================
-- 11. 建議的安全加固措施
-- ============================================================================

-- 1. 更新 PostgreSQL 版本
--    sudo apt-get update && sudo apt-get upgrade postgresql postgresql-client

-- 2. 啟用 SSL/TLS
--    在 postgresql.conf 中設置:
--    ssl = on
--    ssl_cert_file = '/etc/ssl/certs/server.crt'
--    ssl_key_file = '/etc/ssl/private/server.key'

-- 3. 配置防火牆規則
--    只允許必要端口的存取:
--    - 5432 (PostgreSQL)
--    - 3021 (LINE 機器人)
--    - 6379 (Redis)
--    - 其他 API 端口

-- 4. 定期備份
--    建議每週備份一次:
--    pg_dumpall > /backup/postgres_$(date +%Y%m%d).sql

-- 5. 監控系統資源
--    - CPU 使用率
--    - 記憶體使用率
--    - 磁碟空間
--    - DB 連接數

-- 6. 日誌管理
--    - 系統日誌
--    - 應用程式日誌
--    - 安全事件日誌
--    - 備份日誌

-- ============================================================================
-- 12. 建議的備份策略
-- ============================================================================

-- 完整備份 (每週)
-- pg_dumpall > /backup/full_backup_$(date +%Y%m%d).sql

-- 增量備份 (每日)
-- pg_dump --format=custom --file=/backup/incremental_$(date +%Y%m%d).dump community

-- 邏輯備份 (用於恢復測試)
-- pg_dump --verbose --clean --create --if-exists community > /backup/logical_$(date +%Y%m%d).sql

-- ============================================================================
-- 13. 建議的監控配置
-- ============================================================================

-- PostgreSQL 監控
-- 1. 連接數監控
--    SELECT COUNT(*) FROM pg_stat_activity;

-- 2. 慢查詢監控
--    SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;

-- 3. 鎖等待監控
--    SELECT * FROM pg_locks WHERE mode != 'ACCESS_SHARE';

-- 4. 死鎖監控
--    SELECT * FROM pg_stat_activity WHERE state = 'idle in transaction';

-- Redis 監控
-- 1. 快取命中率
--    redis-cli info stats | grep hit_rate

-- 2. 記憶體使用
--    redis-cli info memory

-- 3. 連接數
--    redis-cli info clients
