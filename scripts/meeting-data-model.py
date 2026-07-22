#!/usr/bin/env python3
"""
社區會議記錄資料庫模型
PostgreSQL 表結構定義
"""

import json
from datetime import datetime

# 資料庫配置
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "community",
    "user": "hermes",
    "password": "hermes123"
}

# 表結構
TABLES = {
    "meetings": {
        "name": "meetings",
        "columns": {
            "meeting_id": "VARCHAR(50) PRIMARY KEY",
            "title": "VARCHAR(200) NOT NULL",
            "date": "DATE NOT NULL",
            "time_start": "TIME NOT NULL",
            "time_end": "TIME NOT NULL",
            "location": "VARCHAR(200) DEFAULT '社區活动中心'",
            "host": "VARCHAR(100) NOT NULL",
            "agenda": "JSONB",
            "action_items": "JSONB",
            "created_at": "TIMESTAMP DEFAULT NOW()",
            "updated_at": "TIMESTAMP DEFAULT NOW()"
        },
        "description": "社區會議記錄"
    },
    "meeting_speakers": {
        "name": "meeting_speakers",
        "columns": {
            "id": "SERIAL PRIMARY KEY",
            "meeting_id": "VARCHAR(50) REFERENCES meetings(meeting_id)",
            "speaker_name": "VARCHAR(100) NOT NULL",
            "speaker_unit": "VARCHAR(10)",
            "speaker_role": "VARCHAR(50)",
            "voice_profile_id": "UUID",
            "created_at": "TIMESTAMP DEFAULT NOW()"
        },
        "description": "會議發言人"
    },
    "meeting_segments": {
        "name": "meeting_segments",
        "columns": {
            "id": "SERIAL PRIMARY KEY",
            "meeting_id": "VARCHAR(50) REFERENCES meetings(meeting_id)",
            "speaker_id": "INTEGER REFERENCES meeting_speakers(id)",
            "start": "REAL NOT NULL",
            "end": "REAL NOT NULL",
            "text": "TEXT NOT NULL",
            "confidence": "REAL DEFAULT 0.0"
        },
        "description": "會議語音段"
    },
    "meeting_action_items": {
        "name": "meeting_action_items",
        "columns": {
            "id": "SERIAL PRIMARY KEY",
            "meeting_id": "VARCHAR(50) REFERENCES meetings(meeting_id)",
            "item": "TEXT NOT NULL",
            "owner": "VARCHAR(100)",
            "deadline": "DATE",
            "status": "VARCHAR(20) DEFAULT 'pending'",
            "created_at": "TIMESTAMP DEFAULT NOW()"
        },
        "description": "會議行動項目"
    },
    "meeting_files": {
        "name": "meeting_files",
        "columns": {
            "id": "SERIAL PRIMARY KEY",
            "meeting_id": "VARCHAR(50) REFERENCES meetings(meeting_id)",
            "file_name": "VARCHAR(255) NOT NULL",
            "file_path": "TEXT NOT NULL",
            "file_type": "VARCHAR(50) DEFAULT 'audio'",
            "file_size": "BIGINT",
            "created_at": "TIMESTAMP DEFAULT NOW()"
        },
        "description": "會議相關文件"
    },
    "meeting_notes": {
        "name": "meeting_notes",
        "columns": {
            "id": "SERIAL PRIMARY KEY",
            "meeting_id": "VARCHAR(50) REFERENCES meetings(meeting_id)",
            "note": "TEXT NOT NULL",
            "note_type": "VARCHAR(50) DEFAULT 'general'",
            "created_by": "VARCHAR(100)",
            "created_at": "TIMESTAMP DEFAULT NOW()"
        },
        "description": "會議筆記"
    }
}

# 生成 SQL 建表語句
def generate_create_tables_sql():
    """生成建表 SQL"""
    sql_statements = []
    
    for table_name, table_info in TABLES.items():
        # 建表語句
        columns = ", ".join(f"{col_name} {col_type}" for col_name, col_type in table_info["columns"].items())
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        sql_statements.append(sql)
        
        # 索引
        for col_name, col_type in table_info["columns"].items():
            if col_type == "VARCHAR(50)" or col_type == "VARCHAR(100)" or col_type == "VARCHAR(200)":
                sql_statements.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{col_name} ON {table_name} ({col_name})")
    
    return sql_statements

# 示例數據
def generate_sample_data():
    """生成示例數據"""
    
    # 示例會議
    sample_meeting = {
        "meeting_id": "MEET-2026-07-15",
        "title": "社區會議",
        "date": "2026-07-15",
        "time_start": "09:00",
        "time_end": "10:00",
        "location": "社區活动中心",
        "host": "張三",
        "agenda": [
            {
                "title": "停車場收費",
                "speaker": "李四",
                "content": "討論新的收費標準",
                "resolution": "通過"
            },
            {
                "title": "消防設備更新",
                "speaker": "王五",
                "content": "討論設備更新預算",
                "resolution": "待簽核"
            }
        ],
        "action_items": [
            {
                "item": "完成停車場收費方案",
                "owner": "李四",
                "deadline": "2026-07-22",
                "status": "pending"
            },
            {
                "item": "消防設備更新申請",
                "owner": "王五",
                "deadline": "2026-07-29",
                "status": "pending"
            }
        ]
    }
    
    # 示例發言人
    sample_speakers = [
        {"speaker_name": "張三", "speaker_unit": "101", "speaker_role": "總幹事"},
        {"speaker_name": "李四", "speaker_unit": "205", "speaker_role": "委員"},
        {"speaker_name": "王五", "speaker_unit": "308", "speaker_role": "委員"}
    ]
    
    # 示例語音段
    sample_segments = [
        {"speaker_id": 1, "start": 0.0, "end": 10.0, "text": "歡迎大家參加今天的社區會議", "confidence": 0.95},
        {"speaker_id": 2, "start": 10.0, "end": 20.0, "text": "首先討論停車場收費問題", "confidence": 0.92}
    ]
    
    # 示例行動項目
    sample_action_items = [
        {"item": "完成停車場收費方案", "owner": "李四", "deadline": "2026-07-22", "status": "pending"},
        {"item": "消防設備更新申請", "owner": "王五", "deadline": "2026-07-29", "status": "pending"}
    ]
    
    return {
        "meetings": [sample_meeting],
        "meeting_speakers": sample_speakers,
        "meeting_segments": sample_segments,
        "meeting_action_items": sample_action_items
    }

# 主要功能
def main():
    print("=" * 60)
    print("📊 會議記錄資料庫模型")
    print("=" * 60)
    
    # 生成建表 SQL
    print("\n📋 建表 SQL:")
    print("-" * 60)
    for sql in generate_create_tables_sql():
        print(sql)
        print()
    
    # 生成示例數據
    print("\n📦 示例數據:")
    print("-" * 60)
    sample_data = generate_sample_data()
    
    for table_name, data in sample_data.items():
        print(f"\n{table_name}:")
        for item in data:
            print(f"  - {json.dumps(item, ensure_ascii=False)}")
    
    # 保存 SQL 腳本
    sql_path = "/home/rick/shared-wiki/scripts/create_meeting_tables.sql"
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("\n".join(generate_create_tables_sql()))
    
    print(f"\n💾 SQL 腳本已保存至: {sql_path}")
    
    # 保存示例數據
    json_path = "/home/rick/shared-wiki/vault/meetings/sample_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 示例數據已保存至: {json_path}")
    
    print("\n✅ 會議記錄資料庫模型完成!")

if __name__ == "__main__":
    main()
