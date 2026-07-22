#!/usr/bin/env python3
"""
Phase 10B: Dashboard Data
================================================================================
"""
import sys
import os
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional


class DashboardData:
    """儀表板數據"""

    def __init__(self):
        self.buildings: List[Dict] = [
            {'name': 'A棟', 'floor': 10, 'units': 50},
            {'name': 'B棟', 'floor': 8, 'units': 40},
            {'name': 'C棟', 'floor': 12, 'units': 60},
        ]
        self.residents: List[Dict] = [
            {'name': '住戶A', 'building': 'A', 'phone': '0912345678'},
            {'name': '住戶B', 'building': 'B', 'phone': '0987654321'},
            {'name': '住戶C', 'building': 'C', 'phone': '0911111111'},
        ]
        self.events: List[Dict] = [
            {'type': 'maintenance', 'title': '電梯維修', 'date': '2026-07-19', 'status': 'scheduled'},
            {'type': 'emergency', 'title': '火警警報', 'date': '2026-07-18', 'status': 'resolved'},
            {'type': 'notice', 'title': '停水通知', 'date': '2026-07-17', 'status': 'active'},
        ]

    def get_community_overview(self) -> Dict:
        """獲取社區概覽"""
        return {
            'total_buildings': len(self.buildings),
            'total_units': sum(b['units'] for b in self.buildings),
            'total_residents': len(self.residents),
            'total_events': len(self.events),
        }

    def get_event_tracking(self) -> Dict:
        """獲取事件追蹤"""
        return {
            'total_events': len(self.events),
            'by_type': {
                'maintenance': sum(1 for e in self.events if e['type'] == 'maintenance'),
                'emergency': sum(1 for e in self.events if e['type'] == 'emergency'),
                'notice': sum(1 for e in self.events if e['type'] == 'notice'),
            },
            'recent_events': self.events[-3:],
        }

    def get_statistics(self) -> Dict:
        """獲取統計數據"""
        return {
            'total_buildings': len(self.buildings),
            'total_units': sum(b['units'] for b in self.buildings),
            'total_residents': len(self.residents),
            'event_types': list(set(e['type'] for e in self.events)),
        }

    def export_to_csv(self) -> str:
        """導出為 CSV"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['building', 'floor', 'units'])
        for building in self.buildings:
            writer.writerow([building['name'], building['floor'], building['units']])
        return output.getvalue()


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 10B: Dashboard Data")
    print("=" * 60)

    dashboard = DashboardData()

    # 測試社區概覽
    print("\n--- Community Overview ---")
    overview = dashboard.get_community_overview()
    print(f"  建物: {overview['total_buildings']}")
    print(f"  單位: {overview['total_units']}")
    print(f"  住戶: {overview['total_residents']}")
    print(f"  事件: {overview['total_events']}")

    # 測試事件追蹤
    print("\n--- Event Tracking ---")
    tracking = dashboard.get_event_tracking()
    print(f"  事件: {tracking['total_events']}")
    for key, value in tracking['by_type'].items():
        print(f"  {key}: {value}")

    # 測試統計數據
    print("\n--- Statistics ---")
    stats = dashboard.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # 測試 CSV 導出
    print("\n--- CSV Export ---")
    csv_data = dashboard.export_to_csv()
    print(f"  CSV 內容:\n{csv_data}")

    print("\n" + "=" * 60)
    print("儀表板數據測試完成")
    print("=" * 60)
