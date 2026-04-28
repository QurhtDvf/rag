# 二項独立モデル (BIM) の実装

このリポジトリには、情報検索のための二項独立モデル（BIM: Binary Independence Model）のシンプルかつカスタムな実装が含まれている。BIMは、与えられたクエリに対する文書の関連性確率に基づいて文書をランク付けする確率的検索モデルである。

---

## 特徴

- NLTKを使用したテキスト前処理（トークン化・小文字化・レンマ化）
- 語彙構築とバイナリターム頻度の計算
- 擬似カウントを用いた確率推定
- BIMスコアに基づく文書ランキング
- 自己完結型スクリプト（`bim_model.py`）

---

## はじめに

### 前提条件

- Python 3.x
- nltk

```bash
pip install nltk
```

---

### 使用方法

```bash
python bim_model.py
```

実行内容：

1. NLTKリソースのダウンロード
2. サンプル文書・クエリ定義
3. 前処理
4. 語彙・文書頻度の計算
5. 確率推定
6. ランキング出力

---

## コード構造

- `download_nltk_resources()`
- `preprocess_english_text(text)`
- `calculate_bim_probabilities(...)`
- `calculate_bim_score(...)`
- `rank_documents(...)`

---

## サンプルデータ

### 文書

```
[
    "The quick brown fox jumps over the lazy dog.",
    "The dog barks loudly at the cat.",
    "A brown fox is a wild animal.",
    "The cat sleeps peacefully on the mat.",
    "Quickly, the fox ran away from the barking dog."
]
```

### クエリ

```
[
    "brown fox",
    "lazy dog sleeps",
    "cat barking"
]
```

---

## 日本語BIMデモ

### 前提条件

```bash
pip install janome
```

### 実行

```bash
python bim_model_japanese.py
```

---

## BIMの仕組み（詳細）

BIMは、文書とクエリの関連性を確率論に基づいて評価するモデルである。

### 仮定

1. 文書はバイナリベクトル（出現=1, 非出現=0）
2. 用語は独立
3. 文書は関連 or 非関連

---

## 目的

$$
P(R \mid D, Q)
$$

---

## オッズ比

$$
O(R \mid D, Q) =
\frac{P(R \mid D, Q)}{P(nR \mid D, Q)}
$$

---

## ランキング関数

$$
RSV_D =
\sum_{t \in Q \cap D}
\log \left(
\frac{P(t \mid R)}{P(t \mid nR)}
\right)
$$

---

## 用語重み

$$
W_t =
\log \left(
\frac{\frac{P(t \mid R)}{1 - P(t \mid R)}}
     {\frac{P(t \mid nR)}{1 - P(t \mid nR)}}
\right)
$$

---

## 確率推定

### 関連文書

$$
P(t \mid R) =
\frac{
\mathrm{relevant\_docs\_with\_term\_t} + \mathrm{pseudo\_count\_r}
}{
\mathrm{relevant\_docs\_total} + 2 \cdot \mathrm{pseudo\_count\_r}
}
$$

---

### 非関連文書

$$
P(t \mid nR) =
\frac{
df_t + \mathrm{pseudo\_count\_nr}
}{
N + 2 \cdot \mathrm{pseudo\_count\_nr}
}
$$

---

## ライセンス

MIT License
