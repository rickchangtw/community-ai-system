#!/usr/bin/env python3
"""
Phase 10C: Role Permission
================================================================================
"""
import sys
import os
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional


class Role:
    """角色"""

    def __init__(self, name: str, permissions: List[str]):
        self.name = name
        self.permissions = permissions

    def has_permission(self, permission: str) -> bool:
        """檢查是否有權限"""
        return permission in self.permissions

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            'name': self.name,
            'permissions': self.permissions,
        }


class PermissionManager:
    """權限管理器"""

    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, Dict] = {}

        # 定義角色
        self.roles['admin'] = Role('admin', [
            'read', 'write', 'delete', 'manage_users', 'manage_roles', 'manage_system',
        ])
        self.roles['manager'] = Role('manager', [
            'read', 'write', 'manage_events', 'manage_maintenance',
        ])
        self.roles['resident'] = Role('resident', [
            'read', 'view_own_data',
        ])
        self.roles['agent'] = Role('agent', [
            'read', 'write', 'manage_notifications', 'manage_alerts',
        ])

    def check_permission(self, username: str, permission: str) -> bool:
        """檢查權限"""
        user = self.users.get(username)
        if not user:
            return False
        role = self.roles.get(user.get('role'))
        if not role:
            return False
        return role.has_permission(permission)

    def list_roles(self) -> List[Dict]:
        """列出角色"""
        return [role.to_dict() for role in self.roles.values()]

    def list_users(self) -> List[Dict]:
        """列出用戶"""
        return list(self.users.values())


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 10C: Role Permission")
    print("=" * 60)

    manager = PermissionManager()

    # 測試角色
    print("\n--- Roles ---")
    for name, role in manager.roles.items():
        print(f"  {name}: {role.to_dict()['permissions']}")

    # 測試權限檢查
    print("\n--- Permission Check ---")
    # 添加測試用戶
    manager.users['admin'] = {'username': 'admin', 'role': 'admin'}
    manager.users['manager'] = {'username': 'manager', 'role': 'manager'}
    manager.users['resident'] = {'username': 'resident', 'role': 'resident'}

    # 測試 admin 權限
    assert manager.check_permission('admin', 'read')
    assert manager.check_permission('admin', 'write')
    assert manager.check_permission('admin', 'manage_system')
    print(f"  ✅ Admin 權限: read, write, manage_system")

    # 測試 manager 權限
    assert manager.check_permission('manager', 'read')
    assert manager.check_permission('manager', 'write')
    assert not manager.check_permission('manager', 'manage_system')
    print(f"  ✅ Manager 權限: read, write")
    print(f"  ❌ Manager 無權限: manage_system")

    # 測試 resident 權限
    assert manager.check_permission('resident', 'read')
    assert manager.check_permission('resident', 'view_own_data')
    assert not manager.check_permission('resident', 'write')
    print(f"  ✅ Resident 權限: read, view_own_data")
    print(f"  ❌ Resident 無權限: write")

    # 測試未知用戶
    assert not manager.check_permission('unknown', 'read')
    print(f"  ❌ Unknown 無權限: read")

    # 測試列出角色
    print("\n--- List Roles ---")
    roles = manager.list_roles()
    print(f"  角色數: {len(roles)}")

    # 測試列出用戶
    print("\n--- List Users ---")
    users = manager.list_users()
    print(f"  用戶數: {len(users)}")

    print("\n" + "=" * 60)
    print("角色權限測試完成")
    print("=" * 60)
