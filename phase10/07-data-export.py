#!/usr/bin/env python3
"""
Phase 10B: Data Export
================================================================================
"""
import sys
import os
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional


class DataExport:
    """數據導出"""

    def __init__(self):
        self.data = {
            'buildings': [
                {'name': 'A棟', 'floor': 10, 'units': 50},
                {'name': 'B棟', 'floor': 8, 'units': 40},
                {'name': 'C棟', 'floor': 12, 'units': 60},
            ],
            'residents': [
                {'name': '住戶A', 'building': 'A', 'phone': '0912345678'},
                {'name': '住戶B', 'building': 'B', 'phone': '0987654321'},
            ],
        }

    def export_to_csv(self) -> str:
        """導出為 CSV"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['name', 'floor', 'units'])
        for building in self.data['buildings']:
            writer.writerow([building['name'], building['floor'], building['units']])
        return output.getvalue()

    def export_to_json(self) -> str:
        """導出為 JSON"""
        return json.dumps(self.data, ensure_ascii=False, indent=2)

    def export_to_text(self) -> str:
        """導出為文字"""
        lines = []
        lines.append("=== 社區數據導出 ===")
        lines.append("")
        lines.append("建物:")
        for building in self.data['buildings']:
            lines.append(f"  - {building['name']}: {building['floor']}層, {building['units']}戶")
        lines.append("")
        lines.append("住戶:")
        for resident in self.data['residents']:
            lines.append(f"  - {resident['name']}: {resident['building']}棟")
        return '\n'.join(lines)


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 10B: Data Export")
    print("=" * 60)

    exporter = DataExport()

    # 測試 CSV 導出
    print("\n--- CSV Export ---")
    csv_data = exporter.export_to_csv()
    print(f"  CSV 內容:\n{csv_data}")

    # 測試 JSON 導出
    print("\n--- JSON Export ---")
    json_data = exporter.export_to_json()
    print(f"  JSON 內容:\n{json_data}")

    # 測試文字導出
    print("\n--- Text Export ---")
    text_data = exporter.export_to_text()
    print(f"  文字內容:\n{text_data}")

    print("\n" + "=" * 60)
    print("數據導出測試完成")
    print("=" * 60)
