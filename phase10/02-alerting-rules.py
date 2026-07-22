#!/usr/bin/env python3
"""
Phase 10A: Alerting Rules
================================================================================
"""
import sys
import os
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional


class AlertRule:
    """警報規則"""

    def __init__(self, name: str, severity: str, threshold: float, operator: str = '>'):
        self.name = name
        self.severity = severity  # info, warning, critical
        self.threshold = threshold
        self.operator = operator  # >, <, >=, <=, ==

    def check(self, value: float) -> bool:
        """檢查警報規則"""
        if self.operator == '>':
            return value > self.threshold
        elif self.operator == '<':
            return value < self.threshold
        elif self.operator == '>=':
            return value >= self.threshold
        elif self.operator == '<=':
            return value <= self.threshold
        elif self.operator == '==':
            return value == self.threshold
        return False

    def __str__(self):
        return f"{self.name}: {self.operator} {self.threshold} ({self.severity})"


class AlertManager:
    """警報管理器"""

    def __init__(self):
        self.rules: List[AlertRule] = []
        self.alert_history: List[Dict] = []

        # 定義警報規則
        self.rules = [
            AlertRule('CPU Usage > 80%', 'warning', 80.0, '>'),
            AlertRule('CPU Usage > 90%', 'critical', 90.0, '>'),
            AlertRule('CPU Usage < 10%', 'info', 10.0, '<'),
            AlertRule('Memory Usage > 80%', 'warning', 80.0, '>'),
            AlertRule('Memory Usage > 90%', 'critical', 90.0, '>'),
            AlertRule('DB Connections > 100', 'warning', 100.0, '>'),
            AlertRule('DB Connections > 200', 'critical', 200.0, '>'),
            AlertRule('Redis Connections > 50', 'warning', 50.0, '>'),
            AlertRule('Redis Connections > 100', 'critical', 100.0, '>'),
        ]

    def evaluate_rules(self, metrics: Dict) -> List[Dict]:
        """評估警報規則"""
        triggered = []
        for rule in self.rules:
            if rule.check(metrics.get('cpu_usage', 0)):
                triggered.append({'rule': rule.name, 'value': metrics.get('cpu_usage', 0), 'severity': rule.severity})
            elif rule.check(metrics.get('memory_usage', 0)):
                triggered.append({'rule': rule.name, 'value': metrics.get('memory_usage', 0), 'severity': rule.severity})
            elif rule.check(metrics.get('db_connections', 0)):
                triggered.append({'rule': rule.name, 'value': metrics.get('db_connections', 0), 'severity': rule.severity})
            elif rule.check(metrics.get('redis_connections', 0)):
                triggered.append({'rule': rule.name, 'value': metrics.get('redis_connections', 0), 'severity': rule.severity})
        return triggered

    def send_alert(self, severity: str, message: str) -> Dict:
        """發送警報"""
        alert = {
            'severity': severity,
            'message': message,
            'timestamp': datetime.now(),
            'agent': 'alert_manager',
        }
        self.alert_history.append(alert)
        return alert

    def get_alert_history(self) -> List[Dict]:
        """獲取警報歷史"""
        return self.alert_history[-10:]

    def get_alert_summary(self) -> Dict:
        """獲取警報摘要"""
        summary = {
            'total': len(self.alert_history),
            'by_severity': {
                'info': sum(1 for a in self.alert_history if a['severity'] == 'info'),
                'warning': sum(1 for a in self.alert_history if a['severity'] == 'warning'),
                'critical': sum(1 for a in self.alert_history if a['severity'] == 'critical'),
            },
        }
        return summary


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 10A: Alerting Rules")
    print("=" * 60)

    manager = AlertManager()

    # 測試警報規則
    print("\n--- Alert Rules ---")
    for rule in manager.rules:
        print(f"  {rule}")

    # 測試警報評估
    print("\n--- Alert Evaluation ---")
    test_metrics = {
        'cpu_usage': random.uniform(10, 90),
        'memory_usage': random.uniform(30, 80),
        'db_connections': random.randint(5, 50),
        'redis_connections': random.randint(10, 30),
    }
    triggered = manager.evaluate_rules(test_metrics)
    print(f"  觸發警報數: {len(triggered)}")
    for alert in triggered:
        print(f"  {alert['rule']}: {alert['value']} ({alert['severity']})")

    # 測試警報歷史
    print("\n--- Alert History ---")
    history = manager.get_alert_history()
    print(f"  警報歷史: {len(history)}")

    # 測試警報摘要
    print("\n--- Alert Summary ---")
    summary = manager.get_alert_summary()
    print(f"  總計: {summary['total']}")
    print(f"  資訊: {summary['by_severity']['info']}")
    print(f"  警告: {summary['by_severity']['warning']}")
    print(f"  嚴重: {summary['by_severity']['critical']}")

    print("\n" + "=" * 60)
    print("警報規則測試完成")
    print("=" * 60)
