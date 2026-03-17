# 🔗 Graph RAG デモ — スキーマ自動取得版
## Neo4j + Ollama（完全ローカル）

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yourname/graph-rag-demo/blob/main/graph_rag_auto_schema.ipynb)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.18-008CC1?logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Ollama](https://img.shields.io/badge/Ollama-llama3-black?logo=ollama&logoColor=white)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter&logoColor=white)](https://jupyter.org/)

---

> **「1つのユーザークエリが、なぜグラフDBへの複数クエリに展開されるのか」**  
> Neo4j + Ollama を Google Colab 上で動かし、Graph RAG の動作をインタラクティブに体験するデモです。  
> **外部APIキー不要・完全ローカル実行。**

---

## 📊 デモ結果

質問のホップ数に応じて Neo4j へのクエリ数が増加します。クエリ分解はすべてアプリ層（Ollama）が担い、Neo4j は1件ずつ受け取るだけです。


| 質問 | ホップ数 | Neo4j クエリ数 |
|---|---|---|
| Q1: 組織の管理者は？ | 2ホップ | **2件** |
| Q2: 会社の代表者は？ | 3ホップ | **3件** |
| Q3: メンバーとプロジェクトは？ | 広範囲 | **2件** |

---

## 📚 目次

1. [スキーマ自動取得とは](#スキーマ自動取得とは)
2. [アーキテクチャ](#アーキテクチャ)
3. [クイックスタート](#クイックスタート)
4. [ノートブックの構成](#ノートブックの構成)

---

## スキーマ自動取得とは

スキーマ固定版ではプロンプトにノード名・リレーション名をハードコードしていました。

```python
# 固定版（スキーマをプロンプトに直接記述）
PROMPT = """
- ノード: (:Person), (:Org), (:Company), (:Project)
- リレーション: BELONGS_TO, MANAGES, PART_OF ...
"""
```

本ノートブックでは Neo4j の組み込みプロシージャでスキーマを自動取得します。

```python
# 自動取得版（実行時に Neo4j から取得）
def get_schema() -> str:
    labels    = run_cypher("CALL db.labels() YIELD label RETURN label")
    rel_types = run_cypher("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
    props     = run_cypher("CALL db.schema.nodeTypeProperties() ...")
    ...
```

| | 固定版 | **自動取得版（本ノートブック）** |
|---|---|---|
| スキーマの指定 | プロンプトにハードコード | Neo4j から実行時に自動取得 |
| DB 変更時 | プロンプトの書き直しが必要 | **変更不要・自動対応** |
| 汎用性 | 特定の DB 専用 | **どんな Neo4j DBでも動作** |

---

## アーキテクチャ

本ノートブックの最大の工夫は **LLM と Cypher 生成の役割分離** です。

### 問題：LLM に Cypher を直接生成させると…

- リレーション名を間違える（例：`WORKS_ON` を使うべきでない場面で使用）
- 複数ホップを1クエリにまとめる
- `WHERE o IN collect(o)` のような不正な Cypher を生成する

### 解決策：役割を分離する

```
LLM の役割   →  「何を・どのリレーションで・どの順にたどるか」を JSON で返すだけ
コードの役割 →  その JSON から Cypher 文字列を組み立てる
```

```python
# LLM が返す JSON（Cypher ではなく意図）
[
  {"from_label": "Person", "from_name": "田中太郎", "rel": "BELONGS_TO", "to_label": "Org",     "return_as": "org"},
  {"from_label": "Org",    "from_name": "{org}",    "rel": "PART_OF",    "to_label": "Company", "return_as": "company"},
  {"from_label": "Person", "from_name": null,        "rel": "REPRESENTS", "to_label": "Company", "filter_by": "company", "return_as": "representative"}
]

# コードが Cypher を生成（1ステップ = 1リレーション = 1クエリ 保証）
MATCH (a:Person {name:'田中太郎'})-[:BELONGS_TO]->(b:Org) RETURN b.name AS org
MATCH (a:Org)-[:PART_OF]->(b:Company) WHERE a.name IN ['開発部'] RETURN b.name AS company
MATCH (a:Person)-[:REPRESENTS]->(b:Company) WHERE b.name IN ['株式会社ABC'] RETURN a.name AS representative
```

### 全体フロー

```
ユーザークエリ
      │
      ▼
  Neo4j にスキーマを問い合わせ（CALL db.labels() 等）
      │
      ▼
  Ollama（アプリ層）
  検索ステップの意図を JSON で返す（Cypher は書かない）
      │
      ▼
  コードが Cypher を自動生成
  1ステップ = 1リレーション = 1クエリ を保証
      │
   ┌──┴──┬──────┐
   ▼     ▼      ▼
 クエリ① ② ③  ← Neo4j（DB層）各クエリを個別に実行
   └──┬──┴──────┘
      ▼
  Ollama（アプリ層）
  結果を統合して最終回答
```

---





## クイックスタート

### 必要なもの

- Google アカウント（Colab 利用）
- GPU ランタイム推奨（llama3 の推論速度向上のため）
- 約 15〜20 分（Neo4j インストール + モデルダウンロード込み）
- 外部 API キー不要

### 手順

1. 上部の **Open in Colab** バッジをクリック
2. ランタイム → ランタイムのタイプを変更 → **T4 GPU** を選択
3. セルを上から順番に実行（`Shift + Enter`）

### モデルの選択

```python
# STEP 3 のセルで変更可能
MODEL_NAME = "llama3"   # 高精度（約 4.7GB）
# MODEL_NAME = "phi3"   # 軽量版（約 2.3GB）
```

---

## ノートブックの構成

| STEP | 内容 | 所要時間 |
|---|---|---|
| 1 | Neo4j インストール | 約3分 |
| 2 | Neo4j 設定・起動 | 約1分 |
| 3 | Ollama + LLM モデルのダウンロード | 約5〜10分 |
| 4 | ライブラリ・日本語フォント設定 | 約1分 |
| 5 | Neo4j 接続・サンプルデータ投入 | 数秒 |
| 6 | グラフの可視化 | 数秒 |
| 7 | スキーマ自動取得関数の定義 | 数秒 |
| 8 | Graph RAG パイプラインの定義 | 数秒 |
| 9 | デモ①：2ホップの質問 | 約1分 |
| 10 | デモ②：3ホップの質問 | 約1分 |
| 11 | デモ③：広範囲の質問 | 約1分 |
| 12 | 結果の比較グラフ | 数秒 |
| 13 | スキーマ確認とまとめ | 数秒 |

---

## 注意事項

- Colab のセッションが切れると Neo4j・Ollama ともにリセットされます。再実行時は STEP 1 から順に実行してください
- Neo4j の設定セル（STEP 2）は **1セッション内で2回実行しないでください**（設定の重複エラーが発生します）
- 無料の Colab は RAM 約 12GB のため、llama3 と Neo4j の同時起動でメモリが逼迫することがあります。その場合は `phi3` モデルを使用してください
- 起動時の以下の警告は無視して問題ありません
  - `WARNING: systemd is not running`
  - `WARNING: Unable to detect NVIDIA/AMD GPU`
  - `Warning: could not connect to a running Ollama instance`

---

## 参考文献

- [Neo4j 公式ドキュメント](https://neo4j.com/docs/)
- [Ollama 公式サイト](https://ollama.com/)
- [From Local to Global: A Graph RAG Approach — Microsoft Research (2024)](https://arxiv.org/abs/2404.16130)
- [GQL Standard — ISO/IEC 39075:2024](https://www.iso.org/standard/76120.html)
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)

---

## ライセンス

MIT License
