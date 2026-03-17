# 🔗 Graph RAG デモ — スキーマ自動取得版
## Neo4j + Ollama on Google Colab（完全ローカル）

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

![Graph RAG クエリ数比較](graph_rag_auto_schema_result.png)

| 質問 | ホップ数 | Neo4j クエリ数 |
|---|---|---|
| Q1: 組織の管理者は？ | 2ホップ | **2件** |
| Q2: 会社の代表者は？ | 3ホップ | **3件** |
| Q3: メンバーとプロジェクトは？ | 広範囲 | **2件** |

---

## 📚 目次

1. [グラフDBとは](#グラフdbとは)
2. [グラフDBの歴史](#グラフdbの歴史)
3. [Graph RAG とは](#graph-rag-とは)
4. [なぜ複数クエリになるのか](#なぜ複数クエリになるのか)
5. [スキーマ自動取得とは](#スキーマ自動取得とは)
6. [アーキテクチャ](#アーキテクチャ)
7. [ノートブック一覧](#ノートブック一覧)
8. [クイックスタート](#クイックスタート)
9. [ノートブックの構成](#ノートブックの構成)

---

## グラフDBとは

**グラフデータベース（Graph Database）** は、データを **ノード（節点）** と **エッジ（辺）** で表現するデータベースです。RDB のような表形式ではなく、「もの」と「もの同士のつながり」をそのまま保存・検索できます。

```
（田中太郎）──[BELONGS_TO]──▶（開発部）──[PART_OF]──▶（株式会社ABC）
                                  ▲                        ▲
                             [MANAGES]               [REPRESENTS]
                                  │                        │
                             （山田次郎）────────────────────┘
```

### RDB との違い

| 観点 | リレーショナルDB | グラフDB |
|---|---|---|
| データモデル | テーブル・行・列 | ノード・エッジ・プロパティ |
| 関係の表現 | JOIN（結合） | エッジをたどるトラバーサル |
| 多段結合の性能 | ホップ数に比例して急激に低下 | ホップ数に依存しにくい |
| 向いているデータ | 構造が均一な大量データ | 関係が複雑・多様なデータ |
| クエリ言語 | SQL | Cypher（Neo4j）、Gremlin など |

### 得意な用途

- **ソーシャルグラフ** — 友人関係、フォロワー、影響力の分析
- **サプライチェーン** — 部品の依存関係、製造元のトレーサビリティ
- **不正検知** — 取引ネットワーク内の異常パターン発見
- **レコメンデーション** — 「この人が買ったものを買った人は…」
- **ナレッジグラフ** — 企業・人物・概念の関係データベース
- **Graph RAG** — LLM と組み合わせた知識ベース構築（本デモ）

---

## グラフDBの歴史

### 1960年代 — 起源：ネットワーク型DB

グラフDBの概念的な祖先は、1960年代のネットワーク型データベースです。IBM の **IMS（Information Management System）** や CODASYL モデルがレコード間のポインタによる関係表現を採用しており、現代のグラフDBの原型といえます。

### 1970〜80年代 — RDB の台頭と「関係」の後退

Edgar F. Codd が1970年に提唱したリレーショナルモデルが主流となり、ネットワーク型DBは衰退します。しかし「JOIN を多段に重ねると性能が劣化する」という課題は、RDB の普及とともに顕在化していきます。

### 1990年代 — セマンティックウェブと RDF

Web の普及とともに、W3C が推進した **RDF（Resource Description Framework）** が登場。主語・述語・目的語の三つ組（トリプル）で知識を表現するモデルはグラフ的な発想の復権を告げるものでした。

### 2007年 — Neo4j の誕生

スウェーデンの Emil Eifrem らが開発を始めた **Neo4j** が最初の公開リリース。これが現代的なグラフデータベースの事実上の出発点です。ソーシャルネットワーク（Facebook, Twitter）の急成長とともに「関係データ」の重要性が再認識され、注目が高まりました。

### 2010年代 — Cypher の標準化と普及

Neo4j が **Cypher** クエリ言語を公開し、グラフDBの操作が格段に直感的になりました。Amazon Neptune、Azure Cosmos DB など大手クラウドベンダーもグラフDB機能を提供し始めます。

### 2024年 — GQL が ISO 標準へ

ISO/IEC が SQL と並ぶグラフクエリ言語の標準として **GQL（Graph Query Language）** を正式承認。Cypher の構文が GQL に大きく影響を与えており、Neo4j の Cypher は事実上の業界標準として機能しています。

### 2020年代 — LLM との融合：Graph RAG へ

大規模言語モデル（LLM）の台頭により、グラフDBは新たな役割を担います。Microsoft Research の論文（2024）が **Graph RAG** を体系化し、エンタープライズ向け AI システムの標準構成の1つとなりつつあります。

---

## Graph RAG とは

**RAG（Retrieval-Augmented Generation）** は、LLM が回答を生成する前に外部データソースから関連情報を検索し、その内容を文脈として与える手法です。

**Graph RAG** はグラフDBを検索ソースとして使います。これにより、単なる類似度検索では拾えない「関係の連鎖」を活用した回答が可能になります。

### 通常の RAG vs Graph RAG

| 観点 | 通常の RAG（ベクトルDB） | Graph RAG |
|---|---|---|
| 検索の単位 | 文書チャンク（意味的類似度） | ノード・エッジ（関係の連鎖） |
| 多段推論 | 苦手 | 得意（ホップをたどる） |
| 関係の明示性 | 暗黙的（埋め込みベクトル） | 明示的（エッジのラベル） |
| 更新のしやすさ | チャンク再埋め込みが必要 | ノード・エッジの追加のみ |
| 向いている質問 | 「〜について教えて」 | 「AとBはどう繋がっているか」 |

---

## なぜ複数クエリになるのか

自然言語の質問には複数の「ホップ（関係の連鎖）」が含まれることがあります。

**例：「田中太郎が所属する組織が属する会社の代表者は？」**

```
クエリ①  MATCH (p:Person {name:'田中太郎'})-[:BELONGS_TO]->(o:Org)
          RETURN o.name AS org
          → 結果: 開発部

クエリ②  MATCH (a:Org)-[:PART_OF]->(b:Company)
          WHERE a.name IN ['開発部']
          RETURN b.name AS company
          → 結果: 株式会社ABC

クエリ③  MATCH (a:Person)-[:REPRESENTS]->(b:Company)
          WHERE b.name IN ['株式会社ABC']
          RETURN a.name AS representative
          → 結果: 山田次郎
```

> **重要**: この分解は **グラフDBの外側（アプリ層）** で行われます。  
> Neo4j は受け取ったクエリを1件ずつ実行するだけであり、「これらが1つの質問から来た」とは知りません。

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

## ノートブック一覧

| ファイル | 説明 |
|---|---|
| `graph_rag_neo4j_ollama_final.ipynb` | **スキーマ固定版** — LLM が Cypher を直接生成 |
| `graph_rag_auto_schema.ipynb` | **スキーマ自動取得版** — LLM は意図のみ、Cypher はコードで生成（本ノートブック） |

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
