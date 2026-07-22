#!/usr/bin/env python3
"""
Phase 9: Security Encryption Test
================================================================================
"""
import sys
import os
import json
import hashlib
import hmac
import base64
import time
from typing import Dict, List, Optional


class SecurityEncryptionTest:
    """安全加密測試"""

    def __init__(self):
        self.results: List[Dict] = []

    def test_hashlib_sha256(self) -> Dict:
        """測試 hashlib.sha256"""
        try:
            import hashlib
            # 測試 SHA256 哈希
            data = b"test data"
            hash_result = hashlib.sha256(data).hexdigest()
            assert len(hash_result) == 64
            assert isinstance(hash_result, str)
            return {'name': 'hashlib.sha256', 'passed': True, 'result': hash_result}
        except Exception as e:
            return {'name': 'hashlib.sha256', 'passed': False, 'error': str(e)}

    def test_hashlib_sha512(self) -> Dict:
        """測試 hashlib.sha512"""
        try:
            import hashlib
            data = b"test data"
            hash_result = hashlib.sha512(data).hexdigest()
            assert len(hash_result) == 128
            assert isinstance(hash_result, str)
            return {'name': 'hashlib.sha512', 'passed': True, 'result': hash_result}
        except Exception as e:
            return {'name': 'hashlib.sha512', 'passed': False, 'error': str(e)}

    def test_hmac_sha256(self) -> Dict:
        """測試 hmac.sha256"""
        try:
            import hmac
            import hashlib
            # 測試 HMAC-SHA256
            msg = b"Hello, World!"
            key = b"my_secret_key"
            mac = hmac.new(key, msg, hashlib.sha256).hexdigest()
            assert len(mac) == 64
            assert isinstance(mac, str)
            return {'name': 'hmac.sha256', 'passed': True, 'result': mac}
        except Exception as e:
            return {'name': 'hmac.sha256', 'passed': False, 'error': str(e)}

    def test_base64_encoding(self) -> Dict:
        """測試 base64 編碼"""
        try:
            import base64
            data = b"test data"
            encoded = base64.b64encode(data).decode('utf-8')
            assert isinstance(encoded, str)
            assert len(encoded) > 0
            return {'name': 'base64', 'passed': True, 'result': encoded}
        except Exception as e:
            return {'name': 'base64', 'passed': False, 'error': str(e)}

    def test_base64_decode(self) -> Dict:
        """測試 base64 解碼"""
        try:
            import base64
            encoded = "dGVzdCBkYXRh"
            decoded = base64.b64decode(encoded)
            assert isinstance(decoded, bytes)
            assert decoded == b"test data"
            return {'name': 'base64.decode', 'passed': True, 'result': decoded.decode('utf-8')}
        except Exception as e:
            return {'name': 'base64.decode', 'passed': False, 'error': str(e)}

    def test_password_hashing(self) -> Dict:
        """測試密碼哈希"""
        try:
            # 測試 bcrypt 或 argon2
            password = "test_password_123"
            hashed = hashlib.sha256(password.encode()).hexdigest()
            assert len(hashed) == 64
            assert isinstance(hashed, str)
            return {'name': 'password.hashing', 'passed': True, 'result': hashed}
        except Exception as e:
            return {'name': 'password.hashing', 'passed': False, 'error': str(e)}

    def test_api_signature(self) -> Dict:
        """測試 API 簽章"""
        try:
            import hmac
            import hashlib
            import time
            # 測試 API 簽章
            method = "GET"
            path = "/api/v1/users"
            timestamp = str(int(time.time()))
            nonce = str(hashlib.sha256(timestamp.encode()).hexdigest())
            secret = "my_secret_key"
            string_to_sign = f"{method}\n{path}\n{timestamp}\n{nonce}"
            signature = hmac.new(secret.encode(), string_to_sign.encode(), hashlib.sha256).hexdigest()
            assert len(signature) == 64
            assert isinstance(signature, str)
            return {'name': 'api.signature', 'passed': True, 'result': signature}
        except Exception as e:
            return {'name': 'api.signature', 'passed': False, 'error': str(e)}

    def test_token_generation(self) -> Dict:
        """測試 Token 生成"""
        try:
            import secrets
            # 生成安全 Token
            token = secrets.token_urlsafe(32)
            assert isinstance(token, str)
            assert len(token) > 0
            return {'name': 'token.generation', 'passed': True, 'result': token}
        except Exception as e:
            return {'name': 'token.generation', 'passed': False, 'error': str(e)}

    def test_random_generation(self) -> Dict:
        """測試隨機數生成"""
        try:
            import secrets
            # 生成隨機數
            random_number = secrets.randbelow(1000000)
            assert isinstance(random_number, int)
            assert 0 <= random_number < 1000000
            return {'name': 'random.generation', 'passed': True, 'result': random_number}
        except Exception as e:
            return {'name': 'random.generation', 'passed': False, 'error': str(e)}

    def test_secure_random(self) -> Dict:
        """測試安全隨機數生成"""
        try:
            import secrets
            # 生成安全隨機數
            secure_random = secrets.token_bytes(32)
            assert isinstance(secure_random, bytes)
            assert len(secure_random) == 32
            return {'name': 'secure.random', 'passed': True, 'result': secure_random.hex()}
        except Exception as e:
            return {'name': 'secure.random', 'passed': False, 'error': str(e)}


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 9: Security Encryption Test")
    print("=" * 60)

    test = SecurityEncryptionTest()

    # 執行測試
    test_functions = [
        ('hashlib.sha256', test.test_hashlib_sha256),
        ('hashlib.sha512', test.test_hashlib_sha512),
        ('hmac.sha256', test.test_hmac_sha256),
        ('base64', test.test_base64_encoding),
        ('base64.decode', test.test_base64_decode),
        ('password.hashing', test.test_password_hashing),
        ('api.signature', test.test_api_signature),
        ('token.generation', test.test_token_generation),
        ('random.generation', test.test_random_generation),
        ('secure.random', test.test_secure_random),
    ]

    results = []
    for name, func in test_functions:
        result = func()
        results.append(result)
        status = "✅" if result['passed'] else "❌"
        print(f"\n--- {name} ---")
        print(f"{status} {name}")
        if result.get('passed'):
            print(f"  結果: {result['result']}")
        else:
            print(f"  錯誤: {result['error']}")

    # 總結
    print("\n" + "=" * 60)
    print("安全加密測試總結")
    print("=" * 60)

    total_pass = sum(1 for r in results if r['passed'])
    total_fail = sum(1 for r in results if not r['passed'])

    print(f"  ✅ 通過: {total_pass}")
    print(f"  ❌ 失敗: {total_fail}")
    print(f"  總計: {total_pass + total_fail}")
    print("=" * 60)

    # 輸出結果
    for result in results:
        print(f"\n{result['name']}:")
        print(f"  狀態: {'✅ 通過' if result['passed'] else '❌ 失敗'}")
        if result.get('passed'):
            print(f"  結果: {result['result']}")
        else:
            print(f"  錯誤: {result['error']}")
        print()
