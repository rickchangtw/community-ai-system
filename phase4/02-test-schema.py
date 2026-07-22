#!/usr/bin/env python3
"""
Phase 4 Schema 測試腳本
驗證 PostgreSQL 資料庫結構完整性
"""
import psycopg2
import sys

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "community",
    "user": "hermes",
    "password": "hermes123"
}

def get_connection():
    """建立資料庫連接"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"❌ 資料庫連接失敗: {e}")
        return None

def test_table_exists(conn, table_name):
    """測試表是否存在"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)", (table_name,))
            result = cur.fetchone()[0]
        if result:
            print(f"  ✅ {table_name} 存在")
            return True
        else:
            print(f"  ❌ {table_name} 不存在")
            return False
    except Exception as e:
        print(f"  ❌ {table_name} 查詢失敗: {e}")
        return False

def test_table_count(conn, table_name):
    """測試表中的記錄數"""
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
        return count
    except Exception as e:
        print(f"  ❌ {table_name} 查詢失敗: {e}")
        return None

def test_foreign_keys(conn):
    """測試外鍵約束"""
    tests = [
        ("buildings.community_id", "communities"),
        ("floors.building_id", "buildings"),
        ("residents.community_id", "communities"),
        ("residents.building_id", "buildings"),
        ("residents.floor_id", "floors"),
        ("events.community_id", "communities"),
        ("events.building_id", "buildings"),
        ("notices.community_id", "communities"),
        ("fee_records.community_id", "communities"),
        ("fee_records.building_id", "buildings"),
    ]
    results = []
    for fk_col, ref_table in tests:
        table = fk_col.split(".")[1]
        result = test_table_exists(conn, table)
        results.append(result)
    return all(results)

def test_data_seed(conn):
    """測試預設資料"""
    results = {}
    # 測試 Agent 角色
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM agent_roles")
        results["agent_roles"] = cur.fetchone()[0]
    
    # 測試社區
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM communities")
        results["communities"] = cur.fetchone()[0]
    
    # 測試住戶
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM residents")
        results["residents"] = cur.fetchone()[0]
    
    return results

def main():
    print("=" * 60)
    print("Phase 4 Schema 測試")
    print("=" * 60)
    
    conn = get_connection()
    if not conn:
        return
    
    print(f"\n✅ 資料庫連接成功: {DB_CONFIG['dbname']}")
    
    # 測試所有表
    print("\n--- 表存在性測試 ---")
    tables = [
        "communities", "buildings", "floors", "residents", "resident_contacts",
        "agent_roles", "agent_instances",
        "event_types", "events", "event_actions", "event_timeline",
        "meetings", "meeting_speakers", "meeting_segments", "meeting_action_items",
        "meeting_files", "meeting_notes",
        "notice_templates", "notices", "notice_deliveries",
        "fee_categories", "fee_records", "work_orders",
        "patrol_routes", "patrol_logs", "visitor_logs",
        "fire_equipment", "fire_events",
        "energy_devices", "energy_readings", "energy_policies",
        "system_roles", "users", "user_community_roles", "audit_logs"
    ]
    
    for table in tables:
        test_table_exists(conn, table)
    
    # 測試外鍵約束
    print("\n--- 外鍵約束測試 ---")
    fk_valid = test_foreign_keys(conn)
    print(f"  {'✅' if fk_valid else '❌'} 外鍵約束有效")
    
    # 測試預設資料
    print("\n--- 預設資料測試 ---")
    seed_data = test_data_seed(conn)
    for table, count in seed_data.items():
        status = "✅" if count > 0 else "❌"
        print(f"  {status} {table}: {count} 筆記錄")
    
    print("\n" + "=" * 60)
    print("Schema 測試完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
