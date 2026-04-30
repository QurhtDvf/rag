
import collections

class DictionaryCompressor:
    def __init__(self):
        self.rules = {}
        self.next_nonterminal_id = 0
        self.start_symbol = 'S'

    def _generate_nonterminal(self):
        nt = f"NT_{self.next_nonterminal_id}"
        self.next_nonterminal_id += 1
        return nt

    def compress(self, text, K):
        if not text: return {}, self.start_symbol
        initial_rhs = list(text)
        self.rules = {self.start_symbol: initial_rhs}
        self.next_nonterminal_id = 0

        for _ in range(K):
            pair_counts = collections.defaultdict(int)
            for rhs in self.rules.values():
                for i in range(len(rhs) - 1):
                    pair = (rhs[i], rhs[i+1])
                    pair_counts[pair] += 1
            eligible_pairs = {p: c for p, c in pair_counts.items() if c > 1}
            if not eligible_pairs: break
            most_frequent_pair = max(eligible_pairs, key=eligible_pairs.get)
            x, y = most_frequent_pair
            new_nt = self._generate_nonterminal()
            self.rules[new_nt] = [x, y]
            for nt in list(self.rules.keys()):
                if nt == new_nt: continue
                rhs = self.rules[nt]
                new_rhs = []
                i = 0
                while i < len(rhs):
                    if i + 1 < len(rhs) and rhs[i] == x and rhs[i+1] == y:
                        new_rhs.append(new_nt)
                        i += 2
                    else:
                        new_rhs.append(rhs[i])
                        i += 1
                self.rules[nt] = new_rhs
        return self.rules, self.start_symbol

    def decompress(self, compressed_rules, start_symbol):
        if not compressed_rules or start_symbol not in compressed_rules: return ""
        memo = {}
        def expand(symbol):
            if not symbol.startswith('NT_') and symbol != 'S': return [symbol]
            if symbol in memo: return memo[symbol]
            res = []
            for s in compressed_rules[symbol]:
                res.extend(expand(s))
            memo[symbol] = res
            return res
        return "".join(expand(start_symbol))
