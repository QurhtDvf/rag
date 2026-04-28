
# 二項独立モデル (BIM) の実装

このリポジトリには、情報検索のための二項独立モデル (BIM) のシンプルかつカスタムな実装が含まれています。BIMは、与えられたクエリに対する文書の関連性の確率に基づいて文書をランク付けする確率的検索モデルです。

## 特徴
- NLTKを使用したテキスト前処理（トークン化、小文字化、レンマ化）。
- 語彙構築とバイナリターム頻度計算。
- 初期ヒューリスティック推定（擬似カウント）を使用した、関連文書 ($P(t|R)$) および非関連文書 ($P(t|nR)$) における用語の確率推定。
- BIMスコアに基づく文書ランキング。
- 簡単に実行できる自己完結型Pythonスクリプト (`bim_model.py`)。

## はじめに

### 前提条件
- Python 3.x
- `nltk` ライブラリ

```bash
pip install nltk
```

### 使用方法

BIMのデモンストレーションを実行するには、`bim_model.py`スクリプトを単に実行します。

```bash
python bim_model.py
```

これにより、以下のステップが実行されます。
1. 必要なNLTKリソース（punkt、stopwords、wordnet）をダウンロードします。
2. サンプル文書とクエリを定義します。
3. 文書とクエリを前処理します。
4. 語彙を構築し、文書頻度を計算します。
5. BIM確率 $P(t|R)$ と $P(t|nR)$ を推定します。
6. 各サンプルクエリに対して文書をランク付けし、結果を出力します。

### コード構造

- `download_nltk_resources()`: 必要なすべてのNLTKデータがダウンロードされていることを確認します。
- `preprocess_english_text(text)`: 英語のテキストをトークン化、小文字化、ストップワード除去、レンマ化してクリーニングおよび前処理します。
- `calculate_bim_probabilities(document_frequencies, num_documents, pseudo_count_r, pseudo_count_nr)`: 語彙内の各用語について、$P(t|R)$ と $P(t|nR)$ の確率を推定します。
- `calculate_bim_score(query_tokens, document_tf, p_t_R, p_t_nR)`: クエリが与えられた単一の文書のBIMスコアを計算します。
- `rank_documents(queries_raw, all_documents_raw, preprocessed_documents, binary_term_frequencies, p_t_R, p_t_nR, preprocess_func)`: 複数のクエリに対して文書コレクションをランク付けします。

### サンプルデータ

`bim_model.py`スクリプトには、デモンストレーション目的で事前に定義されたサンプル文書とクエリが含まれています。

**文書:**
```
[
    "The quick brown fox jumps over the lazy dog.",
    "The dog barks loudly at the cat.",
    "A brown fox is a wild animal.",
    "The cat sleeps peacefully on the mat.",
    "Quickly, the fox ran away from the barking dog."
]
```

**クエリ:**
```
[
    "brown fox",
    "lazy dog sleeps",
    "cat barking"
]
```

## 日本語BIMデモンストレーション

このリポジトリには、日本語テキストにBIMを適用するためのデモンストレーションスクリプトも含まれています。日本語の形態素解析には`Janome`ライブラリを使用します。

### 前提条件
- Python 3.x
- `Janome` ライブラリ

```bash
pip install janome
```

### 使用方法

日本語BIMのデモンストレーションを実行するには、`bim_model_japanese.py`スクリプトを単に実行します。

```bash
python bim_model_japanese.py
```

これにより、以下のステップが実行されます。
1. 日本語のサンプル文書とクエリを定義します。
2. `Janome`を使用して、日本語の文書とクエリを前処理（形態素解析、ストップワード除去、原形抽出）します。
3. 語彙を構築し、文書頻度を計算します。
4. BIM確率 $P(t|R)$ と $P(t|nR)$ を推定します。
5. 各サンプルクエリに対して文書をランク付けし、結果を出力します。

## BIMの仕組み (詳細版)

二項独立モデル (BIM) は、情報検索における確率的関連性モデルの一種であり、クエリと文書の関連性を確率論に基づいて評価します。BIMは、以下の主要な仮定に基づいています。

1.  **二項表現**: 文書とクエリは、用語の有無を示すバイナリベクトルとして表現されます。各用語は文書に出現するか ($1$) しないか ($0$) のいずれかです。
2.  **用語の独立性**: 文書内における各用語の出現は、他のすべての用語の出現から統計的に独立しています。
3.  **関連性の仮定**: 各文書は、特定のクエリに対して「関連 (Relevant, $R$)」または「非関連 (Non-Relevant, $nR$)」のいずれかに分類されます。

BIMの目標は、与えられたクエリ $Q$ に対して文書 $D$ が関連する確率 $P(R|D, Q)$ を推定することです。ベイズの定理と上記の仮定を用いて、ランキング関数は以下のように導出されます。

まず、関連性オッズ $O(R|D, Q)$ を考えます。

$$
O(R|D, Q) = \frac{P(R|D, Q)}{P(nR|D, Q)}
$$

各用語が独立であるという仮定のもと、このオッズは以下のように分解できます。

$$
O(R|D, Q) = O(R) \cdot \prod_{t \in Q \cap D} \frac{P(t|R)}{P(t|nR)} \cdot \prod_{t \in Q \setminus D} \frac{P(\neg t|R)}{P(\neg t|nR)}
$$

ここで、$P(t|R)$ は用語 $t$ が関連文書に出現する確率、$P(t|nR)$ は用語 $t$ が非関連文書に出現する確率です。$P(\neg t|R) = 1 - P(t|R)$ および $P(\neg t|nR) = 1 - P(t|nR)$ です。

実際のランキングでは、文書のスコア $RSV$ (Retrieval Status Value) が使用され、これは一般的に対数オッズ比として計算されます。

$$
RSV_D = \log \left[ \frac{O(R|D, Q)}{O(R)} \right]
$$

$$
RSV_D = \sum_{t \in Q \cap D} \log \left[ \frac{P(t|R)}{P(t|nR)} \right] + \sum_{t \in Q \setminus D} \log \left[ \frac{1 - P(t|R)}{1 - P(t|nR)} \right]
$$

簡略化のため、クエリに含まれない用語や文書に出現しないクエリ用語に関する項は、定数オフセットとして無視されることがよくあります。これにより、以下の形式がよく使われます。

$$
RSV_D = \sum_{t \in Q \cap D} W_t
$$

ここで $W_t$ は用語 $t$ の関連性重み (Relevance Weight) であり、次のように定義されます。

$$
W_t = \log \left[ \frac{P(t|R) / (1 - P(t|R))}{P(t|nR) / (1 - P(t|nR))} \right]
$$

**確率の推定:**

BIMを初期段階で適用する際、関連文書に関する情報（つまり $P(t|R)$）は通常未知です。そのため、ヒューリスティックな推定値や擬似カウント (pseudo-counts) が使用されます。

*   **$P(t|R)$ (関連文書に出現する確率)**: 関連性フィードバックがない場合、初期推定として $0.5$ を使用したり、擬似カウント（例: 　$0.5 + \texttt{pseudo\_count}$　）を用いることがあります。これは、すべてのクエリ用語が関連文書に均等に出現する可能性があるという仮定に基づきます。
    *    $$P(t|R) = \frac{\texttt{relevant\_docs\_with\_term\_t} + \texttt{pseudo\_count\_r}}{\texttt{relevant\_docs\_total} + 2 \cdot \texttt{pseudo\_count\_r}}$$
    *   関連文書が不明な初期段階では、`pseudo_count_r` を小さく設定し、`relevant_docs_total` を特定の定数と仮定することで、全ての用語に対して $P(t|R) = 0.5$ となるようにします（例: `pseudo_count_r=0.5` とすれば $0.5 / (0.5+0.5) = 0.5$）。
*   **$P(t|nR)$ (非関連文書に出現する確率)**: これは、全文書コレクションにおける用語の出現頻度から推定されます。
    *   **$$P(t|nR) = \frac{df_t + \texttt{pseudo\_count\_nr}}{N + 2 \cdot \texttt{pseudo\_count\_nr}}$$**
    *   $df_t$: 用語 $t$ を含む文書の数 (document frequency)
    *   $N$: 全文書数
    *   `pseudo_count_nr`: 非関連文書における擬似カウント（一般的には $0.5$ など）

これらの確率を推定した後、$W_t$ を計算し、クエリ用語を含む文書の $RSV_D$ を合計することで文書をランキングします。関連性フィードバックが得られた場合（例えば、ユーザーが特定の文書を関連または非関連と評価した場合）、これらの確率はベイズ更新ルールに従って調整され、より正確なランキングが可能になります。

## ライセンス

このプロジェクトはオープンソースであり、MITライセンスの下で利用可能です。
