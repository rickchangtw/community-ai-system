#!/bin/bash
# ============================================================================
# Phase 9: Firewall Configuration
# ============================================================================
# 防火牆規則配置腳本

# ============================================================================
# 1. 檢查當前防火牆狀態
# ============================================================================

# 檢查 iptables 規則
echo "=== 當前 iptables 規則 ==="
iptables -L -n --line-numbers

# 檢查 ufw 狀態
if command -v ufw &> /dev/null; then
    echo ""
    echo "=== UFW 狀態 ==="
    ufw status verbose
fi

# ============================================================================
# 2. 配置防火牆規則
# ============================================================================

# 允許 PostgreSQL (5432)
echo "=== 允許 PostgreSQL (5432) ==="
iptables -A INPUT -p tcp --dport 5432 -j ACCEPT

# 允許 LINE 機器人 (3021)
echo "=== 允許 LINE 機器人 (3021) ==="
iptables -A INPUT -p tcp --dport 3021 -j ACCEPT

# 允許 Redis (6379)
echo "=== 允許 Redis (6379) ==="
iptables -A INPUT -p tcp --dport 6379 -j ACCEPT

# 允許 HTTPS (443)
echo "=== 允許 HTTPS (443) ==="
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 允許 SSH (22)
echo "=== 允許 SSH (22) ==="
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 允許 ICMP (ping)
echo "=== 允許 ICMP (ping) ==="
iptables -A INPUT -p icmp -j ACCEPT

# ============================================================================
# 3. 拒絕所有其他連接
# ============================================================================

# 拒絕所有其他 TCP 連接
echo "=== 拒絕所有其他 TCP 連接 ==="
iptables -A INPUT -p tcp --dport 1024:65535 -j DROP

# 拒絕所有其他 UDP 連接
echo "=== 拒絕所有其他 UDP 連接 ==="
iptables -A INPUT -p udp -j DROP

# ============================================================================
# 4. 保存規則
# ============================================================================

# 保存 iptables 規則
echo "=== 保存規則 ==="
iptables-save > /etc/iptables/rules.v4

# 保存 ufw 規則
if command -v ufw &> /dev/null; then
    echo "=== 保存 UFW 規則 ==="
    ufw allow 5432/tcp
    ufw allow 3021/tcp
    ufw allow 6379/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    ufw save
fi

# ============================================================================
# 5. 測試規則
# ============================================================================

# 測試防火牆規則
echo "=== 測試防火牆規則 ==="
iptables -L -n --line-numbers

# ============================================================================
# 6. 建議的安全加固措施
# ============================================================================

# 1. 使用非標準端口
#    例如: PostgreSQL 使用 5433 而不是 5432

# 2. 限制來源 IP
#    iptables -A INPUT -p tcp --dport 5432 -s 192.168.1.0/24 -j ACCEPT

# 3. 啟用 SYN Flood 防護
#    iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT

# 4. 啟用 XMAS 防護
#    iptables -A INPUT -p tcp --fin -j DROP
#    iptables -A INPUT -p tcp --all -m tcp --tcp-flags ALL NONE -j DROP

# 5. 啟用 NULL 封包防護
#    iptables -A INPUT -p tcp --tcp-flags FIN,SYN,RST,ACK FIN -j DROP

# 6. 啟用 LAND 封包防護
#    iptables -A INPUT -p tcp --tcp-flags SYN,RST SYN,RST -j DROP

# ============================================================================
# 7. 建議的 UFW 規則
# ============================================================================

# UFW 配置腳本
cat > /etc/ufw/user.rules << 'EOF'
# 允許本地迴圈
allow 22/tcp comment 'SSH'
allow 5432/tcp comment 'PostgreSQL'
allow 3021/tcp comment 'LINE Bot'
allow 6379/tcp comment 'Redis'
allow 443/tcp comment 'HTTPS'

# 拒絕所有其他連接
deny 1024:65535/tcp
deny 65535/udp
EOF

# 應用 UFW 規則
echo "=== 應用 UFW 規則 ==="
ufw allow 22/tcp
ufw allow 5432/tcp
ufw allow 3021/tcp
ufw allow 6379/tcp
ufw allow 443/tcp
ufw deny 1024:65535/tcp
ufw deny 65535/udp
ufw --force enable

# ============================================================================
# 8. 建議的監控配置
# ============================================================================

# 監控防火牆規則
echo "=== 監控防火牆規則 ==="
watch -n 5 'iptables -L -n --line-numbers'

# ============================================================================
# 9. 建議的日誌配置
# ============================================================================

# 配置防火牆日誌
echo "=== 配置防火牆日誌 ==="
# 在 syslog.conf 中添加:
# *.warn    /var/log/firewall.log
# *.debug   /var/log/firewall.log

# 配置 iptables 日誌
echo "=== 配置 iptables 日誌 ==="
# 在 /etc/sysctl.conf 中添加:
# net.ipv4.conf.all.log_martians = 1
# net.ipv4.conf.all.send_redirects = 0

# ============================================================================
# 10. 建議的安全掃描工具
# ============================================================================

# 1. nmap - 網路掃描
#    sudo nmap -sV -sC -O <target>

# 2. sqlmap - SQL 注入測試
#    sqlmap -u "http://localhost:3021/community?id=1" --batch

# 3. nikto - Web 伺服器掃描
#    nikto -h http://localhost:3021

# 4. owasp-zap - Web 應用程式安全掃描
#    zaproxy zap openurl http://localhost:3021

# 5. bandit - Python 安全掃描
#    bandit -r /path/to/code

# 6. trivy - 容器安全掃描
#    trivy image <image>

# ============================================================================
# 11. 建議的備份策略
# ============================================================================

# 完整備份 (每週)
pg_dumpall > /backup/full_backup_$(date +%Y%m%d).sql

# 增量備份 (每日)
pg_dump --format=custom --file=/backup/incremental_$(date +%Y%m%d).dump community

# 邏輯備份 (用於恢復測試)
pg_dump --verbose --clean --create --if-exists community > /backup/logical_$(date +%Y%m%d).sql

# ============================================================================
# 12. 建議的監控配置
# ============================================================================

# PostgreSQL 監控
# 1. 連接數監控
SELECT COUNT(*) FROM pg_stat_activity;

# 2. 慢查詢監控
SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;

# 3. 鎖等待監控
SELECT * FROM pg_locks WHERE mode != 'ACCESS_SHARE';

# 4. 死鎖監控
SELECT * FROM pg_stat_activity WHERE state = 'idle in transaction';

# Redis 監控
# 1. 快取命中率
redis-cli info stats | grep hit_rate

# 2. 記憶體使用
redis-cli info memory

# 3. 連接數
redis-cli info clients
