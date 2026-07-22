#!/usr/bin/env python3
"""
Phase 10A: Monitoring Dashboard
================================================================================
"""
import sys
import os
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional


class MonitoringDashboard:
    """監控儀表板"""

    def __init__(self):
        self.agents = {
            '總幹事': {'status': 'online', 'last_heartbeat': datetime.now()},
            '物業': {'status': 'online', 'last_heartbeat': datetime.now()},
            '保全': {'status': 'online', 'last_heartbeat': datetime.now()},
            '消防': {'status': 'online', 'last_heartbeat': datetime.now()},
            '節能': {'status': 'online', 'last_heartbeat': datetime.now()},
            '通知中心': {'status': 'online', 'last_heartbeat': datetime.now()},
        }
        self.metrics = {
            'cpu_usage': random.uniform(10, 30),
            'memory_usage': random.uniform(30, 60),
            'disk_usage': random.uniform(40, 70),
            'db_connections': random.randint(5, 15),
            'redis_connections': random.randint(10, 20),
        }
        self.events: List[Dict] = []

    def get_agent_status(self) -> Dict:
        """獲取 Agent 狀態"""
        result = {'total': len(self.agents), 'online': 0, 'offline': 0, 'agents': []}
        for name, info in self.agents.items():
            entry = {'name': name, 'status': info['status']}
            if info['status'] == 'online':
                entry['status'] = '✅'
                result['online'] += 1
            else:
                entry['status'] = '❌'
                result['offline'] += 1
            result['agents'].append(entry)
        return result

    def get_system_metrics(self) -> Dict:
        """獲取系統指標"""
        return {
            'status': 'healthy' if self.metrics['cpu_usage'] < 80 else 'warning',
            'cpu_usage': self.metrics['cpu_usage'],
            'memory_usage': self.metrics['memory_usage'],
            'disk_usage': self.metrics['disk_usage'],
            'db_connections': self.metrics['db_connections'],
            'redis_connections': self.metrics['redis_connections'],
        }

    def get_event_summary(self) -> Dict:
        """獲取事件摘要"""
        return {
            'total_events': len(self.events),
            'recent_events': self.events[-10:],
        }

    def get_dashboard_data(self) -> Dict:
        """獲取儀表板數據"""
        return {
            'agents': self.get_agent_status(),
            'system_metrics': self.get_system_metrics(),
            'event_summary': self.get_event_summary(),
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 10A: Monitoring Dashboard")
    print("=" * 60)

    dashboard = MonitoringDashboard()

    # 測試 Agent 狀態
    print("\n--- Agent Status ---")
    agent_status = dashboard.get_agent_status()
    print(f"  總計: {agent_status['total']}")
    print(f"  線上: {agent_status['online']}")
    print(f"  離線: {agent_status['offline']}")
    for agent in agent_status['agents']:
        print(f"  {agent['name']}: {agent['status']}")

    # 測試系統指標
    print("\n--- System Metrics ---")
    system_metrics = dashboard.get_system_metrics()
    print(f"  狀態: {system_metrics['status']}")
    for key, value in system_metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.1f}%")
        else:
            print(f"  {key}: {value}")

    # 測試事件摘要
    print("\n--- Event Summary ---")
    event_summary = dashboard.get_event_summary()
    print(f"  事件總數: {event_summary['total_events']}")
    print(f"  最近事件: {event_summary['recent_events']}")

    # 測試儀表板數據
    print("\n--- Dashboard Data ---")
    dashboard_data = dashboard.get_dashboard_data()
    print(f"  Agent 狀態: {dashboard_data['agents']['online']}/{dashboard_data['agents']['total']}")
    print(f"  系統狀態: {dashboard_data['system_metrics']['status']}")
    print(f"  事件數: {dashboard_data['event_summary']['total_events']}")

    print("\n" + "=" * 60)
    print("監控儀表板測試完成")
    print("=" * 60)
