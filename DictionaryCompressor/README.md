# Dictionary-Based Compression (辞書的圧縮)

このリポジトリは、文法ベースの圧縮アルゴリズム（辞書的圧縮）のシンプルなPython実装を提供します。

## 1. 辞書的圧縮とは？

辞書的圧縮（Dictionary-Based Compression / Grammar-Based Compression）は、データの中から**繰り返し現れるパターンを見つけ出し、それを短い記号（非終端記号）で置き換える**ことでデータを短くするアルゴリズムです。

### アルゴリズムの仕組み
1.  **文字列の解析**: 入力された文字列（例: `abracadabra`）をスキャンします。
2.  **頻出ペアの特定**: 文字列の中で、隣り合う2つの記号の組み合わせ（ペア）をカウントします。
3.  **置換 (Substitution)**: 最も頻繁に現れるペアを、新しい記号（例: `NT_0`）で置き換えます。
    - 例: `ab` が多い場合、`NT_0 -> ab` というルールを作り、元の文字列の `ab` をすべて `NT_0` に書き換えます。
4.  **反復**: このプロセスを、新しいペアが見つからなくなるか、指定された回数（K回）に達するまで繰り返します。

### メリット
- **自己展開的**: 圧縮結果が「文法ルール」の形式になるため、再帰的に展開することで元のデータを完全に復元（可逆圧縮）できます。
- **構造の抽出**: データ内の隠れた繰り返し構造を視覚化できます。

## 2. ファイル構成

- `compressor.py`: `DictionaryCompressor` クラスの実装。圧縮 (`compress`) と解凍 (`decompress`) のロジックが含まれます。
- `demo.py`: アルゴリズムの動作を確認するためのデモスクリプト。

## 3. 使い方

### 準備
Python環境で `compressor.py` と同じディレクトリに `demo.py` を配置してください。

### デモの実行
```bash
python demo.py
```

### コードでの利用
```python
from compressor import DictionaryCompressor

compressor = DictionaryCompressor()
text = "banana"

# 圧縮 (K=2は2つの新しいルールを作成することを意味します)
grammar, start_symbol = compressor.compress(text, K=2)

# 解凍
original = compressor.decompress(grammar, start_symbol)
print(original) # "banana"
```

## 4. ライセンス
MIT License
