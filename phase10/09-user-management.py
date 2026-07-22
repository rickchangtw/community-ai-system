#!/usr/bin/env python3
"""
Phase 10C: User Management
================================================================================
"""
import sys
import os
import json
import time
import random
import hashlib
import secrets
from datetime import datetime
from typing import Dict, List, Optional


class User:
    """用戶"""

    def __init__(self, username: str, password: str, role: str = 'resident'):
        self.username = username
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.role = role
        self.created_at = datetime.now()

    def verify_password(self, password: str) -> bool:
        """驗證密碼"""
        return hashlib.sha256(password.encode()).hexdigest() == self.password_hash

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
        }


class UserManager:
    """用戶管理器"""

    def __init__(self):
        self.users: List[User] = []

    def create_user(self, username: str, password: str, role: str = 'resident') -> User:
        """創建用戶"""
        user = User(username, password, role)
        self.users.append(user)
        return user

    def get_user(self, username: str) -> Optional[User]:
        """獲取用戶"""
        for user in self.users:
            if user.username == username:
                return user
        return None

    def update_user(self, username: str, **kwargs) -> Optional[User]:
        """更新用戶"""
        for user in self.users:
            if user.username == username:
                if 'role' in kwargs:
                    user.role = kwargs['role']
                return user
        return None

    def delete_user(self, username: str) -> bool:
        """刪除用戶"""
        for i, user in enumerate(self.users):
            if user.username == username:
                self.users.pop(i)
                return True
        return False

    def list_users(self) -> List[Dict]:
        """列出用戶"""
        return [user.to_dict() for user in self.users]

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """認證用戶"""
        user = self.get_user(username)
        if user and user.verify_password(password):
            return user
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 10C: User Management")
    print("=" * 60)

    manager = UserManager()

    # 測試創建用戶
    print("\n--- Create User ---")
    user = manager.create_user('testuser', 'password123', 'admin')
    print(f"  用戶: {user.username}")
    print(f"  角色: {user.role}")
    print(f"  密碼哈希: {user.password_hash[:20]}...")

    # 測試獲取用戶
    print("\n--- Get User ---")
    found_user = manager.get_user('testuser')
    assert found_user is not None
    print(f"  用戶: {found_user.username}")
    print(f"  角色: {found_user.role}")

    # 測試驗證密碼
    print("\n--- Verify Password ---")
    assert found_user.verify_password('password123')
    assert not found_user.verify_password('wrongpassword')
    print(f"  密碼驗證: ✅ 正確")
    print(f"  錯誤密碼: ❌ 正確")

    # 測試更新用戶
    print("\n--- Update User ---")
    updated_user = manager.update_user('testuser', role='manager')
    assert updated_user is not None
    print(f"  更新後角色: {updated_user.role}")

    # 測試刪除用戶
    print("\n--- Delete User ---")
    deleted = manager.delete_user('testuser')
    assert deleted
    print(f"  刪除成功: {deleted}")

    # 測試列出用戶
    print("\n--- List Users ---")
    users = manager.list_users()
    print(f"  用戶數: {len(users)}")

    # 測試認證
    print("\n--- Authenticate ---")
    # 重新創建用戶以測試認證
    manager2 = UserManager()
    new_user = manager2.create_user('testuser2', 'password123', 'admin')
    authenticated = manager2.authenticate('testuser2', 'password123')
    assert authenticated is not None
    print(f"  認證成功: {authenticated.username}")

    print("\n" + "=" * 60)
    print("用戶管理測試完成")
    print("=" * 60)
