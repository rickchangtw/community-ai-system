#!/usr/bin/env python3
"""
Phase 10C: Authentication
================================================================================
"""
import sys
import os
import json
import time
import random
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class Token:
    """Token"""

    def __init__(self, token: str, expires_at: datetime):
        self.token = token
        self.expires_at = expires_at

    def is_valid(self) -> bool:
        """檢查 Token 是否有效"""
        return datetime.now() < self.expires_at


class AuthenticationManager:
    """認證管理器"""

    def __init__(self):
        self.tokens: Dict[str, Token] = {}

    def generate_token(self) -> str:
        """生成 Token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)
        token_obj = Token(token, expires_at)
        self.tokens[token] = token_obj
        return token

    def validate_token(self, token: str) -> Optional[Token]:
        """驗證 Token"""
        token_obj = self.tokens.get(token)
        if token_obj and token_obj.is_valid():
            return token_obj
        return None

    def revoke_token(self, token: str) -> bool:
        """撤銷 Token"""
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False


class LoginManager:
    """登入管理器"""

    def __init__(self):
        self.users: Dict[str, Dict] = {
            'admin': {'username': 'admin', 'password_hash': 'hashed_password', 'role': 'admin'},
            'manager': {'username': 'manager', 'password_hash': 'hashed_password', 'role': 'manager'},
            'resident': {'username': 'resident', 'password_hash': 'hashed_password', 'role': 'resident'},
        }

    def login(self, username: str, password: str) -> Optional[Dict]:
        """登入"""
        user = self.users.get(username)
        if not user:
            return None
        # 驗證密碼（模擬）
        if user.get('password_hash') == 'hashed_password':
            token = AuthenticationManager().generate_token()
            return {
                'username': username,
                'role': user['role'],
                'token': token,
            }
        return None

    def logout(self, token: str) -> bool:
        """登出"""
        manager = AuthenticationManager()
        return manager.revoke_token(token)


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 10C: Authentication")
    print("=" * 60)

    login_manager = LoginManager()

    # 測試登入
    print("\n--- Login ---")
    result = login_manager.login('admin', 'password')
    assert result is not None
    print(f"  用戶: {result['username']}")
    print(f"  角色: {result['role']}")
    print(f"  Token: {result['token'][:20]}...")

    # 測試登出
    print("\n--- Logout ---")
    assert login_manager.logout(result['token'])
    print(f"  登出成功: True")

    # 測試 Token 生成
    print("\n--- Token Generation ---")
    auth_manager = AuthenticationManager()
    token = auth_manager.generate_token()
    assert token
    print(f"  Token: {token[:20]}...")

    # 測試 Token 驗證
    print("\n--- Token Validation ---")
    token_obj = auth_manager.validate_token(token)
    assert token_obj is not None
    print(f"  Token 有效: True")

    # 測試 Token 撤銷
    print("\n--- Token Revocation ---")
    assert auth_manager.revoke_token(token)
    print(f"  Token 撤銷: True")

    print("\n" + "=" * 60)
    print("認證測試完成")
    print("=" * 60)
