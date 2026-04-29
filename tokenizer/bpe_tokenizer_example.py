
# bpe_tokenizer.py から BPETokenizer クラスをインポート
from bpe_tokenizer import BPETokenizer

# トークナイザーのインスタンス化
tokenizer = BPETokenizer()

# サンプルテキスト
sample_text = "こんにちは、世界！これはBPEトークナイザーのテストです。"

# 語彙サイズを設定（初期の256バイト + 新しいトークン数）
vocab_size = 300 # 例として、256個の初期バイトに44個のマージを追加

# トークナイザーを訓練
print(f"訓練テキスト: '{sample_text}'")
print(f"目標語彙サイズ: {vocab_size}")
tokenizer.train(sample_text, vocab_size)
print("トークナイザーの訓練が完了しました。")

# エンコード
encoded_tokens = tokenizer.encode(sample_text)
print(f"
エンコードされたトークンID: {encoded_tokens}")

# デコード
decoded_text = tokenizer.decode(encoded_tokens)
print(f"デコードされたテキスト: '{decoded_text}'")

# 語彙リストの表示
print(f"
最終的な語彙数: {len(tokenizer.vocab)}")
print("語彙リストの例 (最初の20個と最後の20個):")
example_vocab = tokenizer.get_vocab_list()
for i, token_str in enumerate(example_vocab):
    if i < 20 or i >= len(example_vocab) - 20:
        print(f"  ID {sorted(tokenizer.vocab.keys())[i]}: '{token_str}'")
    elif i == 20:
        print("  ...")
