# 社區會議記錄系統實現計劃

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 建立完整的社區會議記錄系統，包含語音轉文字、發言人辨識、會議記錄生成和資料庫管理。

**Architecture:** PostgreSQL 持久化 + Python 語音處理 + Redis 狀態管理 + Silero VAD + Whisper + Speaker Diarization

**Tech Stack:** PostgreSQL, Python 3.12, Silero VAD, Whisper, Redis

---

## Task 1: 資料庫表結構建立

**Objective:** 創建完整的會議記錄相關資料庫表

**Files:**
- Create: `scripts/create_meeting_tables.sql`

**Step 1: 建表**

SQL 已執行：
- ✅ meetings (會議記錄)
- ✅ meeting_speakers (發言人)
- ✅ meeting_segments (語音段)
- ✅ meeting_action_items (行動項目)
- ✅ meeting_files (會議文件)
- ✅ meeting_notes (會議筆記)

**Verification:**
```
psql -h 127.0.0.1 -U hermes -d community -c "\dt"
List of relations:
- meeting_action_items
- meeting_files
- meeting_notes
- meeting_segments
- meeting_speakers
- meetings
```

**Status:** ✅ 已完成

---

## Task 2: 語音轉文字系統

**Objective:** 建立語音轉文字和發言人辨識系統

**Files:**
- Create: `scripts/meeting-transcription.py`

**Core Classes:**
- `Speaker` - 發言人模型
- `TranscriptionSegment` - 語音轉文字段
- `MeetingRecord` - 會議記錄
- `MeetingTranscriptionSystem` - 語音轉文字系統

**Main Methods:**
- `process_audio_file()` - 處理音頻文件
- `_vad_detect()` - 語音活動偵測
- `_whisper_transcribe()` - 語音轉文字
- `_speaker_diarize()` - 發言人辨識
- `generate_meeting_minutes()` - 生成會議記錄
- `save_meeting_record()` - 保存會議記錄
- `export_to_json()` - 導出 JSON

**Status:** ✅ 已完成

---

## Task 3: 資料庫模型

**Objective:** 建立會議記錄資料庫模型

**Files:**
- Create: `scripts/meeting-data-model.py`

**Database Config:**
- host: localhost
- port: 5432
- dbname: community
- user: hermes
- password: hermes123

**Tables:**
- meetings, meeting_speakers, meeting_segments, meeting_action_items, meeting_files, meeting_notes

**Status:** ✅ 已完成

---

## Task 4: 示例數據插入

**Objective:** 插入示例數據到資料庫

**Verification:**
- ✅ 會議記錄: MEET-2026-07-15
- ✅ 發言人: 張三(101/總幹事), 李四(205/委員), 王五(308/委員)
- ✅ 語音段: 2 個段落

**Status:** ✅ 已完成

---

## Task 5: 完整系統測試

**Objective:** 執行完整系統測試並生成報告

**Files:**
- Update: `~/shared-wiki/scripts/test-system.sh`
- Create: `~/shared-wiki/test-results.json`

**Status:** ⏳ 待執行
