
import math
import re
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional
import numpy as np # numpy を追加
import fugashi # fugashi を追加

class JapaneseTokenizer:
    """
    fugashi (MeCab) を使った日本語トークナイザ。
    名詞・動詞・形容詞のみを抽出し、ストップワードを除去する。
    """
    STOP_WORDS = {
        'する', 'ある', 'いる', 'なる', 'れる', 'られる',
        'この', 'その', 'あの', 'これ', 'それ', 'あれ',
        'こと', 'もの', 'ため', 'よう', 'など', 'また',
    }

    def __init__(self, use_pos_filter: bool = True):
        self.tagger = fugashi.Tagger()
        self.use_pos_filter = use_pos_filter

    def tokenize(self, text: str) -> List[str]:
        tokens = []
        for word in self.tagger(text):
            surface = word.surface
            # 修正: word.feature.split(',')[0] の代わりに word.pos を使用
            pos = word.pos
            if self.use_pos_filter and pos not in ('名詞', '動詞', '形容詞'):
                continue
            if surface in self.STOP_WORDS or len(surface) < 2:
                continue
            tokens.append(surface)
        return tokens


class SimpleTokenizer:
    """英数字・日本語兼用のシンプルな空白/文字境界トークナイザ（fugashi 不要）。"""

    def tokenize(self, text: str) -> List[str]:
        # 英数字はそのまま、日本語は 1 文字ずつ
        text = text.lower()
        tokens = re.findall(r'[a-z0-9]+|[぀-\u9fff]', text)
        return [t for t in tokens if len(t) >= 1]


class BM25:
    """
    BM25 (Okapi BM25) のフルスクラッチ実装。

    Parameters
    ----------
    k1 : float
        単語頻度の飽和パラメータ。大きいほど TF の影響が線形に近づく。
    b  : float
        文書長の正規化パラメータ。0 で正規化なし、1 で完全正規化。
    epsilon : float
        IDF が負になる場合の下限値（floor）。
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75, epsilon: float = 0.25):
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon

        # 構築後にセットされる内部状態
        self.corpus_size: int = 0
        self.avgdl: float = 0.0
        self.doc_freqs: List[Counter] = []   # 各文書の単語頻度
        self.doc_lengths: List[int] = []     # 各文書のトークン数
        self.df: Dict[str, int] = {}         # 各単語の DF (含む文書数)
        self.idf: Dict[str, float] = {}      # 各単語の IDF
        self.tokenizer = None

    # ------------------------------------------------------------------
    # 構築
    # ------------------------------------------------------------------

    def fit(self, corpus: List[str], tokenizer=None) -> 'BM25':
        """
        コーパス（文書リスト）からインデックスを構築する。

        Parameters
        ----------
        corpus     : 文書文字列のリスト
        tokenizer  : tokenize(text) -> List[str] メソッドを持つオブジェクト
        """
        self.tokenizer = tokenizer or SimpleTokenizer()
        tokenized = [self.tokenizer.tokenize(doc) for doc in corpus]
        return self._fit_tokenized(tokenized)

    def _fit_tokenized(self, tokenized_corpus: List[List[str]]) -> 'BM25':
        self.corpus_size = len(tokenized_corpus)
        self.doc_freqs = []
        self.doc_lengths = []
        self.df = defaultdict(int)

        total_len = 0
        for tokens in tokenized_corpus:
            freq = Counter(tokens)
            self.doc_freqs.append(freq)
            self.doc_lengths.append(len(tokens))
            total_len += len(tokens)
            for word in freq:
                self.df[word] += 1

        self.avgdl = total_len / self.corpus_size if self.corpus_size > 0 else 1.0
        self._compute_idf()
        return self

    def _compute_idf(self):
        """
        Robertson-Sparck Jones の IDF 式:
            IDF(q) = log((N - df(q) + 0.5) / (df(q) + 0.5) + 1)
        """
        N = self.corpus_size
        idf_sum = 0.0
        negative_idfs = []
        for word, freq in self.df.items():
            idf = math.log((N - freq + 0.5) / (freq + 0.5) + 1)
            self.idf[word] = idf
            idf_sum += idf
            if idf < 0:
                negative_idfs.append(word)

        # 負の IDF を持つ語（半数以上の文書に登場する語）は epsilon で floor
        avg_idf = idf_sum / len(self.idf) if self.idf else 1.0
        eps = self.epsilon * avg_idf
        for word in negative_idfs:
            self.idf[word] = eps

    # ------------------------------------------------------------------
    # スコアリング
    # ------------------------------------------------------------------

    def _score_single(self, query_tokens: List[str], doc_idx: int) -> float:
        """1 文書に対するスコアを計算する。"""
        score = 0.0
        dl = self.doc_lengths[doc_idx]
        freq_map = self.doc_freqs[doc_idx]
        norm = 1 - self.b + self.b * dl / self.avgdl

        for token in query_tokens:
            if token not in self.idf:
                continue
            tf = freq_map.get(token, 0)
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * norm
            score += self.idf[token] * numerator / denominator

        return score

    def get_scores(self, query: str) -> np.ndarray:
        """全文書に対するスコア配列を返す。"""
        query_tokens = self.tokenizer.tokenize(query)
        scores = np.array([
            self._score_single(query_tokens, i)
            for i in range(self.corpus_size)
        ])
        return scores

    def search(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5,
    ) -> List[Tuple[float, str]]:
        """
        クエリに対して上位 top_k 件の (スコア, 文書) を返す。
        """
        scores = self.get_scores(query)
        ranked_idx = np.argsort(scores)[::-1][:top_k]
        return [(scores[i], documents[i]) for i in ranked_idx]

    # ------------------------------------------------------------------
    # ユーティリティ
    # ------------------------------------------------------------------

    def term_score_breakdown(
        self, query: str, doc_idx: int
    ) -> Dict[str, float]:
        """クエリ語ごとのスコア寄与を返す（デバッグ用）。"""
        query_tokens = self.tokenizer.tokenize(query)
        dl = self.doc_lengths[doc_idx]
        freq_map = self.doc_freqs[doc_idx]
        norm = 1 - self.b + self.b * dl / self.avgdl
        breakdown = {}
        for token in query_tokens:
            if token not in self.idf:
                breakdown[token] = 0.0
                continue
            tf = freq_map.get(token, 0)
            num = tf * (self.k1 + 1)
            den = tf + self.k1 * norm
            breakdown[token] = self.idf[token] * num / den
        return breakdown

    @property
    def stats(self) -> Dict:
        return {
            '文書数': self.corpus_size,
            '語彙数': len(self.df),
            '平均文書長': round(self.avgdl, 1),
            'k1': self.k1,
            'b': self.b,
        }

def pretty_search(bm25: BM25, query: str, documents: List[str], top_k: int = 5):
    print(f'\n🔍 クエリ: 「{query}」')
    print('-' * 60)
    results = bm25.search(query, documents, top_k=top_k)
    for rank, (score, doc) in enumerate(results, 1):
        print(f'  {rank}位 [{score:.4f}] {doc}')
