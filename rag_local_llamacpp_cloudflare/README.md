# 完全ローカル RAG サーバー

**llama.cpp + OpenSearch + Cloudflare Tunnel on Google Colab**

API キー不要 / Docker 不要 / GPU 不要 / アカウント不要

---

## システム構成

```
[ブラウザ / curl]
      ↓  Cloudflare Tunnel（アカウント不要）
[RAG サーバー FastAPI :8100]
      ↓                    ↓
[OpenSearch :9200]   [llama.cpp :18080]
（ドキュメント検索）  （テキスト生成）
```

| サービス | ポート | 役割 |
|---|---|---|
| llama.cpp LLM サーバー | 18080 | テキスト生成（OpenAI 互換 API） |
| llama.cpp 埋め込みサーバー | 18081 | 埋め込みベクトル生成 |
| OpenSearch | 9200 | ドキュメント全文検索 |
| RAG サーバー（FastAPI） | 8100 | ユーザーの窓口・RAG ロジック |

---

## RAG の動作フロー

```
① ユーザー → POST /ask {"question": "..."}
                  ↓
② RAG サーバーが OpenSearch に全文検索
   → ヒットしたドキュメントのテキストを取得
                  ↓
③ 検索結果を llama.cpp へのプロンプトに埋め込む

   [system] 以下のドキュメントを参考に答えてください。
   [user]
   === ドキュメント ===
   【タイトル】本文テキスト...

   === 質問 ===
   ユーザーの質問
                  ↓
④ llama.cpp が検索結果を踏まえて回答を生成
                  ↓
⑤ ユーザーへ {"answer": "...", "sources": [...], "elapsed": 12.3}
```

---

## 使用モデル

| モデル | サイズ | 用途 |
|---|---|---|
| [Qwen2.5-3B-Instruct-Q4_K_M](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF) | ~2.0 GB | テキスト生成・日本語対応 |
| [nomic-embed-text-v1.5-Q4_K_M](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF) | ~80 MB | 埋め込みベクトル生成 |

どちらも GGUF 形式で `huggingface_hub` により自動ダウンロードされます。

---

## 動作確認環境

- Google Colab（無料枠）
- Python 3.12
- CPU 2 コア、RAM 12 GB
- GPU なし

---

## セットアップ手順

ノートブック `rag_local_llamacpp_cloudflare.ipynb` のセルを上から順番に実行します。

### ① 環境確認
RAM・CPU・ディスクの空き容量を表示します。

### ② llama.cpp のインストール
CPU 向けビルド済みホイールを使用します。cmake・コンパイラは不要です。

```bash
pip install 'llama-cpp-python[server]' \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### ③ モデルのダウンロード
HuggingFace から GGUF モデルを `/tmp/models/` にダウンロードします（初回のみ、約 2 GB）。

### ④ llama.cpp LLM サーバーの起動（port 18080）
- Colab 内部の node プロセスが 8080 を占有しているため **18080** を使用
- ヘルスチェックは `/health` ではなく `/v1/models` を使用（v0.3.16 以降）
- `--chat_format chatml` でツールコールを有効化

### ⑤ llama.cpp 埋め込みサーバーの起動（port 18081）
- `--embedding true` で埋め込みモードを有効化

### ⑥ OpenSearch の起動（port 9200）
- tar.gz バイナリを直接起動（Docker 不要）
- **Colab は root で動作するため OpenSearch が起動を拒否する**
  → `useradd opensearch` で専用ユーザーを作成し `sudo -u opensearch` で起動
- JVM ヒープを 512 MB に縮小（他サービスとメモリを共有するため）

### ⑦ RAG サーバーの起動（port 8100）
FastAPI で RAG ロジックを実装したサーバーを起動します。

提供エンドポイント：

| メソッド | パス | 説明 |
|---|---|---|
| GET | `/health` | 稼働確認 |
| GET | `/docs_list` | 登録済みドキュメント一覧 |
| POST | `/add_doc` | ドキュメントを追加 |
| POST | `/ask` | 質問して回答を取得 |
| GET | `/docs` | Swagger UI（ブラウザで操作） |

### ⑧ サンプルドキュメントの登録
`POST /add_doc` でサンプルドキュメントを OpenSearch に登録します。

### ⑨ RAG デモの実行
`POST /ask` で質問し、RAG サーバー経由で回答を取得します。

### ⑩ Cloudflare Tunnel で外部公開
アカウント不要の `cloudflared` を使い、外部からアクセス可能な URL を発行します。

```bash
# インストール
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
     -O /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# トンネル起動（アカウント不要）
cloudflared tunnel --url http://localhost:8100
```

起動すると `https://xxxx.trycloudflare.com` の URL が発行されます。

### RAG サーバーの内部通信

```
RAG サーバー (8100)
  │
  ├─→ HTTP GET  http://localhost:9200/rag-docs/_search  → OpenSearch
  │                                                        （JSON で検索結果を返す）
  │
  └─→ HTTP POST http://localhost:18080/v1/chat/completions → llama.cpp
                                                              （JSON で回答を返す）
```

---

## API の使い方

### ヘルスチェック
```bash
curl https://xxxx.trycloudflare.com/health
# → {"status": "ok"}
```

### ドキュメントを追加
```bash
curl -X POST https://xxxx.trycloudflare.com/add_doc \
     -H "Content-Type: application/json" \
     -d '{"title": "タイトル", "content": "本文テキスト"}'
```

### 質問する
```bash
curl -X POST https://xxxx.trycloudflare.com/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "RAGとはどのような技術ですか？"}'
```

レスポンス例：
```json
{
  "answer": "RAGはRetrieval Augmented Generationの略で...",
  "sources": ["RAGとは", "llama.cppとは"],
  "elapsed": 14.2
}
```

### Swagger UI（ブラウザで操作）
```
https://xxxx.trycloudflare.com/docs
```

---

## パフォーマンス目安（Colab 無料枠 / CPU 2 コア）

| 操作 | 目安 |
|---|---|
| LLM 回答生成（Qwen2.5-3B） | 10〜30 秒 |
| OpenSearch 検索 | < 0.1 秒 |
| 埋め込み生成（1 文） | 0.5〜2 秒 |

---

## 既知の問題と対処

| 問題 | 原因 | 対処 |
|---|---|---|
| port 8080 が使えない | Colab 内部の node が占有 | 18080 を使用 |
| `/health` が 404 | llama.cpp v0.3.16 以降で廃止 | `/v1/models` でヘルスチェック |
| OpenSearch が起動しない | root での実行を拒否 | opensearch ユーザーを作成して起動 |

---

## ファイル構成

```
.
├── rag_local_llamacpp_cloudflare.ipynb   # メインノートブック
└── README.md                             # このファイル
```
