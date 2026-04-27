from prompt_compression.compressors.textrank import textrank_compress
from prompt_compression.compressors.bm25 import bm25_like_compress
from prompt_compression.compressors.embedding_topk import embedding_topk_compress


class CompressionResult:
    def __init__(self, method, compressed):
        self.method = method
        self.compressed = compressed


class TextRankCompressor:
    def compress(self, text, ratio):
        return CompressionResult(
            method="textrank",
            compressed=textrank_compress(text, ratio)
        )


class BM25Compressor:
    def compress(self, text, ratio):
        return CompressionResult(
            method="bm25",
            compressed=bm25_like_compress(text, ratio)
        )


class EmbeddingTopKCompressor:
    def compress(self, text, ratio):
        return CompressionResult(
            method="embedding_topk",
            compressed=embedding_topk_compress(text, ratio)
        )
