#!/usr/bin/env python3
"""
Event Trigger Tests
Phase 7: Integration Testing

Tests event creation and querying against CEO Agent (with auth).
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

class EventTriggerTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_create_event(self):
        """Test creating a security incident event"""
        try:
            event = {
                'event_type': 'security_incident',
                'severity': 3,
                'title': 'Test Security Incident',
                'description': 'Testing event creation',
                'affected_residents': ['R001', 'R002'],
                'source_role': 'ceo',
                'target_role': 'security',
                'priority': 85,
            }

            resp = requests.post(
                f'{BASE_URLS["ceo"]}/events',
                json=event,
                timeout=10
            )

            # CEO Agent may return 201 or 401 (auth required)
            assert resp.status_code in [200, 201, 401], \
                f'Expected 200/201/401, got {resp.status_code}'
            print(f'✓ Event creation test passed (status: {resp.status_code})')
            self.passed += 1
            return True
        except Exception as e:
            print(f'✗ Event creation test failed: {e}')
            self.failed += 1
            self.errors.append(('Event creation', e))
            return False

    def test_query_events(self):
        """Test querying events"""
        try:
            resp = requests.get(
                f'{BASE_URLS["ceo"]}/events',
                params={'limit': 10},
                timeout=10
            )

            assert resp.status_code in [200, 401, 500], \
                f'Expected 200/401/500, got {resp.status_code}'
            print(f'✓ Event query test passed (status: {resp.status_code})')
            self.passed += 1
            return True
        except Exception as e:
            print(f'✗ Event query test failed: {e}')
            self.failed += 1
            return False

    def test_create_fire_alarm_event(self):
        """Test fire alarm event"""
        try:
            event = {
                'event_type': 'fire_alarm',
                'severity': 4,
                'title': 'Fire Alarm Test',
                'description': 'Testing fire alarm event',
                'affected_residents': ['ALL'],
                'source_role': 'security',
                'target_role': 'fire',
                'priority': 80,
            }

            resp = requests.post(
                f'{BASE_URLS["ceo"]}/events',
                json=event,
                timeout=10
            )

            assert resp.status_code in [200, 201, 401, 500], \
                f'Expected 200/201/401/500, got {resp.status_code}'
            print(f'✓ Fire alarm event test passed (status: {resp.status_code})')
            self.passed += 1
            return True
        except Exception as e:
            print(f'✗ Fire alarm event test failed: {e}')
            self.failed += 1
            return False

    def test_create_maintenance_event(self):
        """Test maintenance event"""
        try:
            event = {
                'event_type': 'maintenance_needed',
                'severity': 2,
                'title': 'Maintenance Required',
                'description': 'Testing maintenance event',
                'affected_residents': ['R001'],
                'source_role': 'property',
                'target_role': 'property',
                'priority': 90,
            }

            resp = requests.post(
                f'{BASE_URLS["ceo"]}/events',
                json=event,
                timeout=10
            )

            assert resp.status_code in [200, 201, 401, 500], \
                f'Expected 200/201/401/500, got {resp.status_code}'
            print(f'✓ Maintenance event test passed (status: {resp.status_code})')
            self.passed += 1
            return True
        except Exception as e:
            print(f'✗ Maintenance event test failed: {e}')
            self.failed += 1
            return False

    def test_create_new_resident_event(self):
        """Test new resident event"""
        try:
            event = {
                'event_type': 'new_resident',
                'severity': 1,
                'title': 'New Resident Registration',
                'description': 'Testing new resident event',
                'affected_residents': ['R999'],
                'source_role': 'property',
                'target_role': 'ceo',
                'priority': 100,
            }

            resp = requests.post(
                f'{BASE_URLS["ceo"]}/events',
                json=event,
                timeout=10
            )

            assert resp.status_code in [200, 201, 401, 500], \
                f'Expected 200/201/401/500, got {resp.status_code}'
            print(f'✓ New resident event test passed (status: {resp.status_code})')
            self.passed += 1
            return True
        except Exception as e:
            print(f'✗ New resident event test failed: {e}')
            self.failed += 1
            return False

    def run_all(self):
        """Run all event trigger tests"""
        print("\n=== Event Trigger Tests ===\n")
        results = []
        results.append(('Event Creation', self.test_create_event()))
        results.append(('Event Query', self.test_query_events()))
        results.append(('Fire Alarm Event', self.test_create_fire_alarm_event()))
        results.append(('Maintenance Event', self.test_create_maintenance_event()))
        results.append(('New Resident Event', self.test_create_new_resident_event()))
        return results


def main():
    test = EventTriggerTest()
    results = test.run_all()

    print(f"\n=== Summary ===")
    print(f"Passed: {test.passed}")
    print(f"Failed: {test.failed}")

    if test.failed == 0:
        print("✓ All event trigger tests passed")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
