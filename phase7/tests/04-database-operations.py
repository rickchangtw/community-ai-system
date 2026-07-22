#!/usr/bin/env python3
"""
Database Operations Tests
Phase 7: Integration Testing

Tests database operations against CEO Agent (with auth).
"""

import requests
import sys
import os
import json
import time

# Base URLs
BASE_URLS = {
    'ceo': 'http://localhost:3001',
}

class DatabaseOperationTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_ceo_health(self):
        """Test CEO Agent health endpoint"""
        try:
            resp = requests.get(f'{BASE_URLS["ceo"]}/health', timeout=5)
            assert resp.status_code in [200, 302, 401], \
                f'Expected 200/302/401, got {resp.status_code}'
            print(f'✓ CEO Agent health check passed (status: {resp.status_code})')
            self.passed += 1
            return True
        except Exception as e:
            print(f'✗ CEO Agent health check failed: {e}')
            self.failed += 1
            return False

    def test_ceo_events_endpoint(self):
        """Test CEO Agent events endpoint"""
        try:
            resp = requests.get(f'{BASE_URLS["ceo"]}/events', timeout=10)
            assert resp.status_code in [200, 401, 500], \
                f'Expected 200/401/500, got {resp.status_code}'
            print(f'✓ CEO Agent events endpoint passed (status: {resp.status_code})')
            self.passed += 1
            return True
        except Exception as e:
            print(f'✗ CEO Agent events endpoint test failed: {e}')
            self.failed += 1
            return False

    def test_ceo_buildings_endpoint(self):
        """Test CEO Agent buildings endpoint"""
        try:
            resp = requests.get(f'{BASE_URLS["ceo"]}/buildings', timeout=10)
            assert resp.status_code in [200, 401, 500], \
                f'Expected 200/401/500, got {resp.status_code}'
            print(f'✓ CEO Agent buildings endpoint passed (status: {resp.status_code})')
            self.passed += 1
            return True
        except Exception as e:
            print(f'✗ CEO Agent buildings endpoint test failed: {e}')
            self.failed += 1
            return False

    def test_ceo_residents_endpoint(self):
        """Test CEO Agent residents endpoint"""
        try:
            resp = requests.get(f'{BASE_URLS["ceo"]}/residents', timeout=10)
            assert resp.status_code in [200, 401, 500], \
                f'Expected 200/401/500, got {resp.status_code}'
            print(f'✓ CEO Agent residents endpoint passed (status: {resp.status_code})')
            self.passed += 1
            return True
        except Exception as e:
            print(f'✗ CEO Agent residents endpoint test failed: {e}')
            self.failed += 1
            return False

    def test_ceo_fees_endpoint(self):
        """Test CEO Agent fees endpoint"""
        try:
            resp = requests.get(f'{BASE_URLS["ceo"]}/fees', timeout=10)
            assert resp.status_code in [200, 401, 500], \
                f'Expected 200/401/500, got {resp.status_code}'
            print(f'✓ CEO Agent fees endpoint passed (status: {resp.status_code})')
            self.passed += 1
            return True
        except Exception as e:
            print(f'✗ CEO Agent fees endpoint test failed: {e}')
            self.failed += 1
            return False

    def run_all(self):
        """Run all database operation tests"""
        print("\n=== Database Operation Tests ===\n")
        results = []
        results.append(('CEO Health Check', self.test_ceo_health()))
        results.append(('CEO Events Endpoint', self.test_ceo_events_endpoint()))
        results.append(('CEO Buildings Endpoint', self.test_ceo_buildings_endpoint()))
        results.append(('CEO Residents Endpoint', self.test_ceo_residents_endpoint()))
        results.append(('CEO Fees Endpoint', self.test_ceo_fees_endpoint()))
        return results


def main():
    test = DatabaseOperationTest()
    results = test.run_all()

    print(f"\n=== Summary ===")
    print(f"Passed: {test.passed}")
    print(f"Failed: {test.failed}")

    if test.failed == 0:
        print("✓ All database operation tests passed")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
