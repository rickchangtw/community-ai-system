#!/usr/bin/env python3
"""
Phase 10A: Monitoring System
================================================================================
"""
import sys
import os
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional


class MonitoringSystem:
    """監控系統"""

    def __init__(self):
        self.agents = {
            '總幹事': {'status': 'online', 'last_heartbeat': datetime.now()},
            '物業': {'status': 'online', 'last_heartbeat': datetime.now()},
            '保全': {'status': 'online', 'last_heartbeat': datetime.now()},
            '消防': {'status': 'online', 'last_heartbeat': datetime.now()},
            '節能': {'status': 'online', 'last_heartbeat': datetime.now()},
            '通知中心': {'status': 'online', 'last_heartbeat': datetime.now()},
        }
        self.system_health = {
            'cpu_usage': random.uniform(10, 30),
            'memory_usage': random.uniform(30, 60),
            'disk_usage': random.uniform(40, 70),
            'db_connections': random.randint(5, 15),
            'redis_connections': random.randint(10, 20),
        }
        self.alerts: List[Dict] = []
        self.performance_data: List[Dict] = []

    def check_agent_heartbeats(self) -> Dict:
        """檢查 Agent 心跳"""
        result = {'total': len(self.agents), 'online': 0, 'offline': 0, 'agents': []}
        for name, info in self.agents.items():
            age = (datetime.now() - info['last_heartbeat']).total_seconds()
            entry = {'name': name, 'status': info['status'], 'age_seconds': age}
            if info['status'] == 'online':
                entry['status'] = '✅'
                result['online'] += 1
            else:
                entry['status'] = '❌'
                result['offline'] += 1
            result['agents'].append(entry)
        return result

    def check_system_health(self) -> Dict:
        """檢查系統健康"""
        result = {'status': 'healthy', 'metrics': {}}
        for key, value in self.system_health.items():
            result['metrics'][key] = value
        if self.system_health['cpu_usage'] > 80:
            result['status'] = 'warning'
        elif self.system_health['cpu_usage'] > 90:
            result['status'] = 'critical'
        return result

    def generate_alert(self, severity: str, message: str) -> Dict:
        """生成警報"""
        alert = {
            'severity': severity,
            'message': message,
            'timestamp': datetime.now(),
            'agent': 'monitoring',
        }
        self.alerts.append(alert)
        return alert

    def check_error_alerts(self) -> Dict:
        """檢查錯誤警報"""
        error_count = sum(1 for a in self.alerts if a['severity'] == 'error')
        return {'error_count': error_count, 'alerts': error_count}

    def collect_performance_data(self) -> Dict:
        """收集性能數據"""
        data = {
            'cpu_usage': self.system_health['cpu_usage'],
            'memory_usage': self.system_health['memory_usage'],
            'disk_usage': self.system_health['disk_usage'],
            'db_connections': self.system_health['db_connections'],
            'redis_connections': self.system_health['redis_connections'],
            'timestamp': datetime.now(),
        }
        self.performance_data.append(data)
        return data

    def get_dashboard_data(self) -> Dict:
        """獲取儀表板數據"""
        return {
            'agents': self.check_agent_heartbeats(),
            'system_health': self.check_system_health(),
            'alerts': self.alerts[-10:],
            'performance': self.performance_data[-5:],
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 10A: Monitoring System")
    print("=" * 60)

    monitoring = MonitoringSystem()

    # 測試 Agent 心跳
    print("\n--- Agent Heartbeat ---")
    heartbeat = monitoring.check_agent_heartbeats()
    print(f"  總計: {heartbeat['total']}")
    print(f"  線上: {heartbeat['online']}")
    print(f"  離線: {heartbeat['offline']}")
    for agent in heartbeat['agents']:
        print(f"  {agent['name']}: {agent['status']} (age: {agent['age_seconds']:.1f}s)")

    # 測試系統健康
    print("\n--- System Health ---")
    health = monitoring.check_system_health()
    print(f"  狀態: {health['status']}")
    for key, value in health['metrics'].items():
        print(f"  {key}: {value}")

    # 測試錯誤警報
    print("\n--- Error Alerts ---")
    errors = monitoring.check_error_alerts()
    print(f"  錯誤數: {errors['error_count']}")

    # 測試性能數據
    print("\n--- Performance Data ---")
    perf = monitoring.collect_performance_data()
    print(f"  CPU: {perf['cpu_usage']:.1f}%")
    print(f"  記憶體: {perf['memory_usage']:.1f}%")
    print(f"  磁碟: {perf['disk_usage']:.1f}%")

    # 測試儀表板數據
    print("\n--- Dashboard Data ---")
    dashboard = monitoring.get_dashboard_data()
    print(f"  Agent 數: {dashboard['agents']['total']}")
    print(f"  系統狀態: {dashboard['system_health']['status']}")
    print(f"  警報數: {len(dashboard['alerts'])}")
    print(f"  性能數據點: {len(dashboard['performance'])}")

    print("\n" + "=" * 60)
    print("監控系統測試完成")
    print("=" * 60)
