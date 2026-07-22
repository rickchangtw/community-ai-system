---
title: Wiki Schema
description: 社區管理知識庫結構規範 — 多 Agent 系統知識表示
created: 2026-07-19
updated: 2026-07-19
type: schema
tags: [schema, conventions, community]
okf_version: "0.1"
---

# Wiki Schema

## Domain

600 戶社區智慧管理系統 — 多 Agent 協作知識庫

## Conventions

- 文件命名：小寫、連接號、無空格（如 `fire-equipment.md`）
- 每頁以 YAML 前端元數據開始（見下方）
- 使用 `[[wikilinks]]` 連結頁面（每頁至少 2 個外聯）
- 更新頁面時必須更新 `updated` 日期
- 每頁必須加入 `index.md`
- 每項操作必須加入 `log.md`
- **溯源標記**: 綜合 3+ 來源的頁面，段落末尾加上 `^[raw/sources/source-file.md]`

## Frontmatter

```yaml
---
title: 頁面標題
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary | sop
tags: [from taxonomy below]
sources: [raw/sources/source-name.md]
confidence: high | medium | low
contested: true
contradictions: [other-page-slug]
okf_version: "0.1"
---
```

## Tag Taxonomy

| 類別 | 標籤 |
|------|------|
| 系統 | system, architecture, multi-agent, deployment |
| 居民 | residents, registry, data, privacy |
| 消防 | fire, equipment, safety, emergency |
| 物業 | property, maintenance, work-order |
| 節能 | energy, sustainability, efficiency |
| 會議 | meetings, template, decision |
| 通訊 | communication, line, telegram, webhook |
| 標準作業 | sop, procedure, standard |
| 連接器 | connectors, configuration, data-sources |
| 驗證 | validation, compliance, okf |

## Page Thresholds

- **建立頁面**: 實體/概念在 2+ 來源出現，或為單一來源核心內容
- **加入現有頁面**: 來源提及了已有內容
- **不要建立頁面**: 順帶提及、次要細節、或超出領域範圍
- **分割頁面**: 超過 200 行時拆分為子主題
- **歸檔頁面**: 內容已被完全取代時移至 `_archive/`

## 更新政策

當新資訊與現有內容衝突時：
1. 比較日期 — 較新來源通常取代較舊內容
2. 若真正矛盾，記錄雙方立場及日期來源
3. 在前端標記矛盾：`contradictions: [page-name]`
4. 在 lint 報告中標記供用戶審查

## 文件結構

```
wiki/
├── SCHEMA.md           # 本文件：結構規範
├── index.md            # 頁面目錄
├── log.md              # 操作日誌
├── raw/                # 原始來源（不可變）
│   ├── articles/       # 文章、剪報
│   ├── papers/         # PDF、論文
│   ├── transcripts/    # 會議記錄、訪談
│   └── assets/         # 圖片、圖表
├── sop/                # 標準作業程序
├── fire-equipment/     # 消防設備
├── residents/          # 居民資料
├── energy/             # 節能管理
├── meetings/           # 會議記錄
├── system/             # 系統架構
├── connectors/         # 連接器配置
└── _archive/           # 歸檔頁面
```
