# 🗜️ Prompt Compression Advanced System v3

**セマンティックキャッシュ × 全手法並列評価 × 最良自動選択** を統合した、LLMプロンプト圧縮の研究・実験基盤。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Notebook](https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter)](prompt_compression_v3.ipynb)
[![LLMLingua](https://img.shields.io/badge/Uses-LLMLingua-blueviolet)](https://github.com/microsoft/LLMLingua)
[![SelectiveContext](https://img.shields.io/badge/Uses-SelectiveContext-blue)](https://github.com/liyucheng09/selective_context)

---

## 概要

大規模言語モデル（LLM）への入力プロンプトを圧縮することで、**APIコストの削減・推論速度の向上**を実現するシステムです。

プロンプトが来るたびに**全圧縮手法で圧縮・評価を行い、そのクエリに最も適した手法を自動選択**してLLMに投げます。手法を固定指定する必要がなく、クエリの性質によって最良手法が変わる状況に自動対応します。

---

## パイプライン

```
プロンプト入力
    │
    ▼
┌─────────────────────────┐   ヒット
│  セマンティックキャッシュ検索  │──────────────────→ キャッシュ応答を返す
│  （類似度 × 時間減衰 × 応答価値） │
└────────────┬────────────┘
             │ ミス
             ▼
┌─────────────────────────┐
│  全手法で圧縮・評価       │
│                         │
│  ┌─────────────────┐    │
│  │ TF-IDF          │    │
│  │ SelectiveContext │    │  それぞれ独立して圧縮を実行
│  │ LLMLingua        │    │  → ROUGE / 意味類似度 / レイテンシ を評価
│  │ LongLLMLingua    │    │  → 総合スコアを算出
│  │ AttentionPruning │    │
│  └─────────────────┘    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  総合スコア最高の手法を選択 │  ← このクエリに最も適した圧縮結果
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  LLM 呼び出し            │  採用した圧縮後プロンプトで
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  キャッシュ保存（Redis）  │  採用手法名も記録
└─────────────────────────┘
```

---

## ✨ 主な機能

| 機能 | 説明 |
|------|------|
| 🔄 **全手法評価・自動選択** | 毎回全手法で圧縮・評価し、そのクエリに最適な手法を自動採用 |
| 🔌 **プラグイン設計** | `BaseCompressor`を継承して1行追加するだけで新手法が使用可能 |
| 📦 **本家パッケージ使用** | LLMLingua・SelectiveContextの公式実装を直接使用 |
| 📊 **多角的評価** | ROUGE-1/L・意味類似度・レイテンシ・BERTScore・総合スコア |
| 🧠 **セマンティックキャッシュ** | 類似クエリをembeddingで検出・再利用（Redis） |
| ⏱️ **時間減衰スコアリング** | クエリの性質に応じたTTL自動調整 |
| 📋 **完全可視化ログ** | 全手法のスコアと採用理由をリアルタイム表示 |

---

## 🗜️ 対応圧縮手法

### 1. TF-IDF (`tfidf`) — 自前実装
文単位のTF-IDFスコアで重要文を抽出。外部モデル不要で最速。
- 依存: `scikit-learn`
- 強み: 速度・安定性

### 2. SelectiveContext (`selective`) — 本家パッケージ使用
**[selective-context](https://github.com/liyucheng09/selective_context)** を直接使用。GPT-2で各トークンの自己情報量（−log p）を計算し、情報量の低いトークンを削除する。
- 依存: `pip install selective-context`（GPT-2をダウンロード・約500MB）
- 強み: トークンレベルの精密な削減

### 3. LLMLingua (`llmlingua`) — 本家パッケージ使用
**[Microsoft LLMLingua](https://github.com/microsoft/LLMLingua)** を直接使用。多言語BERTモデルがトークンの条件付き確率を計算し、予測しやすいトークンを削除する。
- 依存: `pip install llmlingua`（llmlingua-2-bert-multilingualをダウンロード・約700MB）
- 強み: 日本語を含む多言語対応・品質と速度のバランス

### 4. LongLLMLingua (`longlingua`) — 本家パッケージ使用
**llmlingua パッケージ内の LongLLMLingua** を使用。クエリとの関連度を優先し、後半位置にバイアスをかける長文特化手法。
- 依存: `pip install llmlingua`（LLMLinguaと共通）
- 強み: 1000トークン超の長文・RAGのコンテキスト圧縮

### 5. AttentionPruning (`attention`) — 自前実装
エンコーダのAttentionスコアを全レイヤー・全ヘッドで集計し、他のトークンから多く参照されるトークンを保持する。
- 依存: `transformers`（flan-t5-baseを使用）
- 強み: 構造的な重要語抽出

---

## 📦 パッケージの位置づけ

| 手法 | 実装 | 使用パッケージ | モデル | 初回DL |
|------|------|--------------|--------|--------|
| TF-IDF | 自前 | `scikit-learn` | なし | なし |
| SelectiveContext | **本家** | `selective-context` | GPT-2 | ~500MB |
| LLMLingua | **本家** | `llmlingua` | llmlingua-2-bert-multilingual | ~700MB |
| LongLLMLingua | **本家** | `llmlingua`（同パッケージ） | 同上 | 共有 |
| AttentionPruning | 自前 | `transformers` | flan-t5-base | ~1GB |

---

## 📊 評価メトリクスと総合スコア

| メトリクス | 重み | 説明 |
|-----------|------|------|
| 意味的類似度 | 40% | 元文と圧縮後のcosine類似度（Sentence-BERT） |
| ROUGE-L | 30% | 最長共通部分列による文構造保持率 |
| 圧縮率 | 20% | 削減されたトークン割合（多いほど高スコア） |
| 速度スコア | 10% | 100ms以内=1.0、1000ms以上=0.0 |
| BERTScore F1 | オプション | `use_bert_score=True` で有効 |

**総合スコア** = 意味類似度×0.40 + ROUGE-L×0.30 + 圧縮率×0.20 + 速度×0.10

このスコアが最も高い手法の圧縮結果がLLMに渡されます。

---

## 🚀 クイックスタート

### 必要環境
- Python 3.10+
- Redis サーバー
- GPU推奨（CPUでも動作可、LLMLingua系は低速になる）

### インストール

```bash
git clone https://github.com/YOUR_USERNAME/prompt-compression-advanced.git
cd prompt-compression-advanced

# システムパッケージ
apt-get install redis-server

# 基盤パッケージ
pip install redis sentence-transformers transformers scikit-learn rouge-score

# 本家圧縮パッケージ
pip install selective-context   # SelectiveContext（GPT-2をDL）
pip install llmlingua           # LLMLingua + LongLLMLingua（BERTをDL）

# オプション（BERTScore使用時）
pip install bert-score
```

### Jupyter で実行

```bash
jupyter notebook prompt_compression_v3.ipynb
```

---

## 💻 使い方

### 基本：全手法で評価して最良を自動選択

```python
result = smart_llm(
    prompt="量子力学とは何ですか",
    # compressor_names 省略 → 全手法を使用
    compression_ratio=0.3,   # 30%削減
    cache_threshold=0.5,
)

print(f"採用手法: {result['best_method']}")
print(f"LLM回答 : {result['response']}")

# 全手法のスコアを確認
for ev in result['all_evals']:
    marker = " ← 採用" if ev.method == result['best_method'] else ""
    print(ev.summary_line() + marker)
```

出力例：
```
  [TF-IDF         ] 総合=0.721 意味=0.891 ROUGE-L=0.643 圧縮率=31.2%  12ms
  [LLMLingua      ] 総合=0.758 意味=0.923 ROUGE-L=0.701 圧縮率=28.9% 342ms ← 採用
  [SelectiveContext] 総合=0.698 意味=0.867 ROUGE-L=0.612 圧縮率=33.1% 198ms
  ...
```

### 試す手法を絞る

```python
result = smart_llm(
    prompt="最新のAIニュースを教えて",
    compressor_names=["tfidf", "selective"],  # 軽量手法のみ
    compression_ratio=0.2,
)
```

### カスタム手法の追加

```python
class MyCompressor(BaseCompressor):
    @property
    def name(self): return "MyMethod"

    def _compress(self, text: str, ratio: float) -> str:
        # 圧縮ロジックを実装
        return compressed_text

# 1行追加するだけで評価対象に自動追加される
COMPRESSOR_REGISTRY["mymethod"] = MyCompressor

result = smart_llm(prompt="...", compressor_names=["tfidf", "mymethod"])
```

---

## 📁 ファイル構成

```
.
├── prompt_compression_v3.ipynb  # メインノートブック（全機能）
├── README.md                    # このファイル
└── (オプション拡張)
    ├── compressors/   # 圧縮手法を個別モジュールとして切り出す場合
    ├── evaluators/    # 評価モジュール
    └── cache/         # キャッシュ管理モジュール
```

---

## ⚙️ キャッシュの時間減衰設定

| クエリの種類 | TTL | キーワード例 |
|------------|-----|------------|
| 時事・ニュース系 | 5分 | ニュース・速報・最新・今日 |
| 手順・方法系 | 6時間 | 方法・手順・使い方 |
| デフォルト | 1時間 | （上記以外） |
| 概念・定義系 | 24時間 | とは・定義・概念・原理 |

キャッシュスコア = cosine類似度 × e^(−経過時間/τ) × 応答の豊富さ

---

## 🔗 関連プロジェクト

- [LLMLingua](https://github.com/microsoft/LLMLingua) — Microsoft公式（本システムで使用）
- [selective-context](https://github.com/liyucheng09/selective_context) — 自己情報量ベース圧縮（本システムで使用）
- [PCToolkit](https://github.com/3DAgentWorld/Toolkit-for-Prompt-Compression) — 圧縮ツールキット（参考元）
- [Sentence-Transformers](https://github.com/UKPLab/sentence-transformers) — 意味的類似度計算

---

## 📄 ライセンス

MIT License

---

## 📚 参考文献

1. Jiang et al. "LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models." EMNLP 2023.
2. Jiang et al. "LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression." arXiv 2023.
3. Pan et al. "LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression." arXiv 2024.
4. Li et al. "Compressing Context to Enhance Inference Efficiency of Large Language Models." EMNLP 2023.
5. Li et al. "PCToolkit: A Unified Plug-and-Play Prompt Compression Toolkit of Large Language Models." arXiv 2024.
