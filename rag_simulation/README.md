# 🔍 RAG シミュレーション

**API キー不要 / Google Colab 完結**

---

## システム構成

```
ユーザー (httpx)
  ↕ HTTP POST /ask
RAG サーバー (FastAPI)
  ├─ RDB 検索      (SQLite)   → 価格・カテゴリ等の構造化フィルタ
  └─ ベクトル DB 検索 (ChromaDB) → 説明文の意味検索
       ↕ 両結果をマージしてプロンプトに組み込む
  ↕ HTTP POST /v1/chat/completions
LLM サーバー (llama-cpp-python)
  └─ Qwen2.5-0.5B-Instruct GGUF（約 400 MB）
```

### RAG サーバーの内部通信

```
RAG サーバー (FastAPI)
  │
  ├─→ SQL クエリ  → SQLite（構造化検索）
  │                  （価格・カテゴリ・在庫で絞り込み）
  │
  ├─→ 埋め込みベクトル検索 → ChromaDB（意味検索）
  │                           （説明文のコサイン類似度）
  │
  └─→ HTTP POST http://localhost:8000/v1/chat/completions → llama.cpp
                                                             （JSON で回答を返す）
```

---

## データ題材：商品カタログ

| コンポーネント | 役割 |
|---|---|
| SQLite（RDB） | 商品名・価格・カテゴリ・在庫の構造化検索 |
| ChromaDB（ベクトル DB） | 商品説明文の意味検索 |
| FastAPI | RAG サーバー（`POST /ask`・`GET /products`） |
| httpx | ユーザーを模擬した HTTP クライアント |

---

## 2 種類の検索の使い分け

| 検索 | 方法 | 向いているクエリ例 |
|---|---|---|
| RDB 検索 | SQL WHERE 句 | 「3000 円以下」「在庫あり」「カテゴリ: オーディオ」 |
| ベクトル検索 | コサイン類似度 | 「静かで軽いもの」「集中できる」「アウトドア向け」 |

クエリに応じて両方を実行し、結果をマージしてから LLM のプロンプトに渡します。

---

## 使用モデル

| モデル | サイズ | 用途 |
|---|---|---|
| [Qwen2.5-0.5B-Instruct-Q4_K_M](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF) | ~400 MB | テキスト生成 |
| sentence-transformers（`all-MiniLM-L6-v2`） | ~90 MB | 埋め込みベクトル生成 |

---

## 動作確認環境

- Google Colab（無料枠）
- CPU / GPU 両対応（GPU があれば自動的に CUDA を使用）

---

## セットアップ手順

ノートブック `rag_simulation.ipynb` のセルを上から順番に実行します。

### Step 1 — インストール
GPU の有無を自動検出し、適切な llama-cpp-python をインストールします。

```bash
# CPU の場合
pip install llama-cpp-python[server] \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# GPU (CUDA) の場合
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python[server] \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

合わせて以下もインストールします。

```bash
pip install chromadb sentence-transformers fastapi uvicorn httpx huggingface_hub nest_asyncio
```

### Step 2 — モデルのダウンロード
HuggingFace から GGUF モデルを `/content/models/` にダウンロードします（初回のみ、約 400 MB）。

### Step 3 — LLM サーバーの起動（port 8000）
llama-cpp-python を OpenAI 互換 API サーバーとして起動します。

- GPU があれば `--n_gpu_layers 32` で GPU 推論
- CPU のみなら `--n_gpu_layers 0`

### Step 4 — データソースの構築
**SQLite** にサンプル商品データ（10 件）を登録します。

**ChromaDB** に各商品の説明文を `sentence-transformers` で埋め込みベクトル化して格納します。

### Step 5 — 検索関数の定義

`search_rdb()` — SQLite に対して構造化条件で検索します。

```python
search_rdb(category="キッチン家電", max_price=5000, in_stock=True)
```

`search_vector()` — ChromaDB に対してコサイン類似度で意味検索します。

```python
search_vector("静かで軽いもの", top_k=3)
```

`merge_results()` — 両結果を重複排除してマージします。

### Step 6 — RAG サーバーの起動（FastAPI）

`nest_asyncio` で Colab のイベントループと共存させながら uvicorn を起動します。

提供エンドポイント：

| メソッド | パス | 説明 |
|---|---|---|
| POST | `/ask` | 質問を受け取り、RAG + LLM で回答を返す |
| GET | `/products` | 商品一覧をフィルタ付きで返す |

リクエスト例：

```json
{
  "user_id": "user_A",
  "question": "3000円以下のコーヒーメーカーはありますか？",
  "max_price": 3000,
  "category": "キッチン家電"
}
```

レスポンス例：

```json
{
  "answer": "3000円以下のコーヒーメーカーとして...",
  "sources": ["コンパクトコーヒーメーカー", "全自動コーヒーメーカー Pro"],
  "rdb_hits": 2,
  "vector_hits": 3
}
```

### Step 7 — HTTP クライアントで質問を送る
`httpx` でユーザーを模擬し、`POST /ask` に非同期リクエストを送ります。

### Step 8 — 検索の内訳を確認する
RDB 検索とベクトル検索それぞれが何を返しているか個別に確認し、マージ結果も表示します。

---

## パフォーマンス目安（Colab 無料枠 / CPU）

| 操作 | 目安 |
|---|---|
| LLM 回答生成（Qwen2.5-0.5B） | 5〜15 秒 |
| SQLite 検索 | < 0.01 秒 |
| ChromaDB ベクトル検索 | 0.1〜0.5 秒 |

---

## ファイル構成

```
.
├── rag_simulation.ipynb   # メインノートブック
└── README.md              # このファイル
```
