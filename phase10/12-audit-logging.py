#!/usr/bin/env python3
"""
Phase 10C: Audit Logging
================================================================================
"""
import sys
import os
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional


class AuditEntry:
    """審計記錄"""

    def __init__(self, action: str, user: str, timestamp: datetime, details: Dict):
        self.action = action
        self.user = user
        self.timestamp = timestamp
        self.details = details

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            'action': self.action,
            'user': self.user,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details,
        }


class AuditLog:
    """審計日誌"""

    def __init__(self):
        self.entries: List[AuditEntry] = []

    def log_operation(self, action: str, user: str, details: Dict) -> AuditEntry:
        """記錄操作"""
        entry = AuditEntry(action, user, datetime.now(), details)
        self.entries.append(entry)
        return entry

    def log_security_event(self, event_type: str, user: str, details: Dict) -> AuditEntry:
        """記錄安全事件"""
        entry = AuditEntry(f'security_{event_type}', user, datetime.now(), details)
        self.entries.append(entry)
        return entry

    def get_entries(self) -> List[Dict]:
        """獲取記錄"""
        return [entry.to_dict() for entry in self.entries]

    def get_entries_by_user(self, user: str) -> List[Dict]:
        """按用戶獲取記錄"""
        return [entry.to_dict() for entry in self.entries if entry.user == user]

    def get_entries_by_action(self, action: str) -> List[Dict]:
        """按操作獲取記錄"""
        return [entry.to_dict() for entry in self.entries if entry.action == action]


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 10C: Audit Logging")
    print("=" * 60)

    audit_log = AuditLog()

    # 測試記錄操作
    print("\n--- Log Operation ---")
    entry = audit_log.log_operation('login', 'admin', {'ip': '192.168.1.1'})
    print(f"  操作: {entry.action}")
    print(f"  用戶: {entry.user}")
    print(f"  時間: {entry.timestamp}")

    # 測試記錄安全事件
    print("\n--- Log Security Event ---")
    security_entry = audit_log.log_security_event('login_attempt', 'admin', {'ip': '192.168.1.1'})
    print(f"  事件: {security_entry.action}")
    print(f"  用戶: {security_entry.user}")
    print(f"  時間: {security_entry.timestamp}")

    # 測試獲取記錄
    print("\n--- Get Entries ---")
    entries = audit_log.get_entries()
    print(f"  記錄數: {len(entries)}")

    # 測試按用戶獲取記錄
    print("\n--- Get Entries By User ---")
    user_entries = audit_log.get_entries_by_user('admin')
    print(f"  用戶記錄: {len(user_entries)}")

    # 測試按操作獲取記錄
    print("\n--- Get Entries By Action ---")
    action_entries = audit_log.get_entries_by_action('login')
    print(f"  操作記錄: {len(action_entries)}")

    print("\n" + "=" * 60)
    print("審計日誌測試完成")
    print("=" * 60)
