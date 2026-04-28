
# 二項独立モデル (BIM) の実装

このリポジトリには、情報検索のための二項独立モデル (BIM) のシンプルかつカスタムな実装が含まれています。BIMは、与えられたクエリに対する文書の関連性の確率に基づいて文書をランク付けする確率的検索モデルです。

## 特徴
- NLTKを使用したテキスト前処理（トークン化、小文字化、レンマ化）。
- 語彙構築とバイナリターム頻度計算。
- 初期ヒューリスティック推定（擬似カウント）を使用した、関連文書 (P(t|R)) および非関連文書 (P(t|nR)) における用語の確率推定。
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
5. BIM確率 P(t|R) と P(t|nR) を推定します。
6. 各サンプルクエリに対して文書をランク付けし、結果を出力します。

### コード構造

- `download_nltk_resources()`: 必要なすべてのNLTKデータがダウンロードされていることを確認します。
- `preprocess_english_text(text)`: 英語のテキストをトークン化、小文字化、ストップワード除去、レンマ化してクリーニングおよび前処理します。
- `calculate_bim_probabilities(document_frequencies, num_documents, pseudo_count_r, pseudo_count_nr)`: 語彙内の各用語について、P(t|R) と P(t|nR) の確率を推定します。
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
4. BIM確率 P(t|R) と P(t|nR) を推定します。
5. 各サンプルクエリに対して文書をランク付けし、結果を出力します。

## BIMの仕組み (簡潔に)

二項独立モデル (BIM) は、用語が統計的に独立しており、文書内の用語の有無が同じ文書内の他の用語の有無とは独立していると仮定します。また、文書はクエリに対して関連または非関連のいずれかに分類できると仮定します。

中心的なアイデアは、各用語の関連性重み (RW) を計算することです。これは、関連文書と非関連文書における用語の出現のオッズ比の対数です。文書の合計スコアは、その文書に存在するクエリ用語のRWの合計です。

初期確率推定 `P(t|R)` と `P(t|nR)` は、しばしばヒューリスティックに（例えば、擬似カウントを使用したり0.5と仮定したりして）行われ、関連性フィードバックを通じて改善することができます。

## ライセンス

このプロジェクトはオープンソースであり、MITライセンスの下で利用可能です。
