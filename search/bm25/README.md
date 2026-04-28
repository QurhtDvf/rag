# BM25 スパース検索 — ゼロから実装

`my_bm25.py` は、情報検索アルゴリズムである BM25 (Best Match 25) を Python でスクラッチから実装したものです。TF-IDF を改良したモデルであり、Elasticsearch などの検索エンジンでも採用されています。日本語のテキストデータにも対応できるよう、`fugashi` を利用した形態素解析ベースのトークナイザも含まれています。

## 導入

### ファイル構成

- `my_bm25.py`: BM25 クラスとトークナイザクラスの定義
- `(このノートブック)`: `my_bm25.py` の使用例と評価

### インストール

必要なライブラリは `pip` でインストールできます。

```bash
pip install fugashi unidic-lite rank_bm25 numpy matplotlib seaborn
```

## 使い方

### 1. `my_bm25.py` からクラスをインポート

```python
from my_bm25 import BM25, JapaneseTokenizer, SimpleTokenizer, pretty_search
import numpy as np # BM25 クラスが内部で numpy を使用するため
```

### 2. トークナイザの初期化

`JapaneseTokenizer` は `fugashi` を利用しますが、環境によっては初期化に失敗する場合があります。その場合、自動的に `SimpleTokenizer` にフォールバックします。

```python
try:
    temp_tokenizer = JapaneseTokenizer()
    test_sentence = '機械学習とディープラーニングの違いについて説明します'
    test_tokens = temp_tokenizer.tokenize(test_sentence)
    if not test_tokens: 
        raise ValueError("JapaneseTokenizer produced empty tokens for a test sentence.")
    current_tokenizer = temp_tokenizer
    print('JapaneseTokenizer を使用します。')
except Exception as e:
    print(f'JapaneseTokenizer 初期化失敗または機能不全 ({e})。SimpleTokenizer にフォールバックします。')
    current_tokenizer = SimpleTokenizer()
    print('SimpleTokenizer を使用します。')
```

### 3. コーパスの準備と BM25 インデックスの構築

検索対象となる文書のリストを準備し、`BM25` クラスに渡してインデックスを構築します。

```python
documents = [
    "機械学習は統計的手法を用いてコンピュータがデータからパターンを学習する技術です。",
    "ディープラーニングは多層のニューラルネットワークを使った機械学習の手法で、画像認識で高い精度を誇ります。",
    "自然言語処理はテキストデータを解析して意味を理解するAIの分野で、翻訳や要約などに応用されます。",
    "強化学習はエージェントが環境と相互作用しながら報酬を最大化する方法を学ぶ機械学習の手法です。",
    # ... 他の文書
]

bm25 = BM25(k1=1.5, b=0.75)
bm25.fit(documents, tokenizer=current_tokenizer)

print('📊 インデックス統計:')
for k, v in bm25.stats.items():
    print(f'  {k}: {v}')
```

### 4. 検索の実行

`search` メソッドを使ってクエリを実行し、関連度の高い文書を取得します。

```python
query = '機械学習 手法'
pretty_search(bm25, query, documents, top_k=3)
```

## BM25 アルゴリズムの概要

BM25 は、以下の式で文書 $D$ とクエリ $Q$ の関連度スコアを計算します。

$$\text{BM25}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \dfrac{|D|}{\text{avgdl}}\right)}$$

主要なパラメータは以下の通りです。

- `k1`: 単語の出現頻度 (TF) の飽和を調整する係数。値が大きいほど TF の影響が線形に近づきます。
- `b`: 文書長の正規化を調整する係数。0 の場合、文書長による正規化は行われず、1 の場合、完全に正規化されます。
- `f(q,D)`: 文書 $D$ 内での単語 $q$ の出現頻度 (Term Frequency)。
- `IDF(q)`: 単語 $q$ の逆文書頻度 (Inverse Document Frequency)。稀な単語ほど高い値となり、検索における重要度が増します。`my_bm25.py` では Robertson-Sparck Jones の IDF 式を採用し、負の IDF 値は `epsilon` でフロアリングしています。

## `rank_bm25` ライブラリとの比較

本実装は `rank_bm25` ライブラリと比較して検証されています。IDF の計算式や浮動小数点演算の丸め誤差、トークナイザの違いにより、スコアにわずかな差が生じる可能性があります。

## 今後の改善点

- **BM25+ / BM25L**: TF 項をさらに調整したバリアントの実装。
- **ハイブリッド検索**: BM25 スコアと密ベクトル検索 (例: FAISS) の結果を組み合わせることで、検索精度を向上させる。
- **クエリ拡張**: 同義語辞書や大規模言語モデル (LLM) を利用してクエリを拡張し、リコール率を改善する。
