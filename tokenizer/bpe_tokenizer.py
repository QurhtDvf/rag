
import collections

class BPETokenizer:
    def __init__(self):
        self.vocab = {}
        self.merges = {}
        self.inverse_merges = {}

    def train(self, text, vocab_size):
        tokens = list(text.encode('utf-8'))
        self.vocab = {i: bytes([i]) for i in range(256)}
        next_token_id = 256

        for _ in range(vocab_size - next_token_id):
            pairs = self._get_pair_counts(tokens)
            if not pairs:
                break
            best_pair = max(pairs, key=pairs.get)

            new_token_bytes = self.vocab[best_pair[0]] + self.vocab[best_pair[1]]
            self.vocab[next_token_id] = new_token_bytes
            self.merges[best_pair] = next_token_id
            self.inverse_merges[next_token_id] = best_pair
            tokens = self._merge_pair(tokens, best_pair, next_token_id)
            next_token_id += 1

        self.itos = {i: self.vocab[i].decode('utf-8', errors='replace') for i in self.vocab}
        self.stoi = {s: i for i, s in self.itos.items()}

    def _get_pair_counts(self, tokens):
        counts = collections.defaultdict(int)
        for i in range(len(tokens) - 1):
            counts[(tokens[i], tokens[i+1])] += 1
        return counts

    def _merge_pair(self, tokens, pair, new_token_id):
        new_tokens = []
        i = 0
        while i < len(tokens):
            if i + 1 < len(tokens) and (tokens[i], tokens[i+1]) == pair:
                new_tokens.append(new_token_id)
                i += 2
            else:
                new_tokens.append(tokens[i])
                i += 1
        return new_tokens

    def encode(self, text):
        tokens = list(text.encode('utf-8'))
        while True:
            pairs = self._get_pair_counts(tokens)
            best_pair = None
            best_merge_id = -1
            # 最も小さいマージIDを優先することで、訓練時のマージ順序を再現
            # Python 3.7+ ではdictの順序が挿入順になるため、これは merges の順序に依存する
            # より確実には、inverse_merges を使って学習時のマージを逆順に適用していくべきだが
            # ここでは単純化のため、best_pair が None またはより小さい merge_id を持つ場合に更新
            
            # merges.items() から key=(p, merge_id) として取得し、merge_id でソート
            # あるいは、merges を key: merge_id の辞書にして、merge_id の小さいものから順に適用
            # 現在の実装では merges が (pair): merge_id の形なので、ループ内でマージIDを比較
            
            for p, merge_id in self.merges.items():
                if p in pairs:
                    if best_pair is None or merge_id < best_merge_id:
                        best_pair = p
                        best_merge_id = merge_id

            if best_pair is None:
                break
            tokens = self._merge_pair(tokens, best_pair, best_merge_id)
        return tokens

    def decode(self, tokens):
        decoded_bytes = b''
        for token_id in tokens:
            decoded_bytes += self.vocab[token_id]
        return decoded_bytes.decode('utf-8', errors='replace')

    def get_vocab_list(self):
        return [self.vocab[i].decode('utf-8', errors='replace') for i in sorted(self.vocab.keys())]
