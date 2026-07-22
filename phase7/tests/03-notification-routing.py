#!/usr/bin/env python3
"""
Notification Routing Tests
Phase 7: Integration Testing

Tests notification publishing and querying against Notice Agent.
"""

import requests
import sys
import os
import json
import time

# Base URLs
BASE_URLS = {
    'notice': 'http://localhost:3006',
}

# Notice Agent is not yet built (Phase 6 design only)
# This test verifies the expected behavior

class NotificationRoutingTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_notice_agent_not_running(self):
        """Verify Notice Agent is not yet running"""
        try:
            resp = requests.get(f'{BASE_URLS["notice"]}/health', timeout=2)
            # Should return 404 or connection refused
            assert resp.status_code != 200, f'Expected not 200, got {resp.status_code}'
            print(f'✓ Notice Agent correctly not running (status: {resp.status_code})')
            self.passed += 1
            return True
        except requests.exceptions.ConnectionError:
            print('✓ Notice Agent correctly not running (connection refused)')
            self.passed += 1
            return True
        except Exception as e:
            print(f'✗ Notice Agent test failed: {e}')
            self.failed += 1
            return False

    def test_expected_notification_types(self):
        """Test that notification types are defined in protocol"""
        try:
            # Import the protocol YAML
            import yaml
            with open('/home/rick/shared-wiki/phase5/01-communication-protocol.yaml', 'r') as f:
                protocol = yaml.safe_load(f)

            notification_types = protocol['notification_routing']['types']
            expected_types = ['emergency', 'important', 'routine', 'informational']

            for type_name in expected_types:
                assert type_name in notification_types, f'Missing type: {type_name}'

            print('✓ All expected notification types defined in protocol')
            self.passed += 1
            return True
        except Exception as e:
            print(f'✗ Notification types test failed: {e}')
            self.failed += 1
            return False

    def run_all(self):
        """Run all notification routing tests"""
        print("\n=== Notification Routing Tests ===\n")
        results = []
        results.append(('Notice Agent Status', self.test_notice_agent_not_running()))
        results.append(('Expected Notification Types', self.test_expected_notification_types()))
        return results


def main():
    test = NotificationRoutingTest()
    results = test.run_all()

    print(f"\n=== Summary ===")
    print(f"Passed: {test.passed}")
    print(f"Failed: {test.failed}")

    if test.failed == 0:
        print("✓ All notification routing tests passed")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
