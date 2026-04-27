from .tfidf import TFIDFCompressor
from .selective import SelectiveContextCompressor
from .llmlingua import LLMLinguaCompressor
from .long_llmlingua import LongLLMLinguaCompressor
from .attention import AttentionPruningCompressor

# 追加（新規3手法）
from .lightweight import (
    TextRankCompressor,
    BM25Compressor,
    EmbeddingTopKCompressor,
)

REGISTRY = {
    'tfidf': TFIDFCompressor,
    'selective': SelectiveContextCompressor,
    'llmlingua': LLMLinguaCompressor,
    'longlingua': LongLLMLinguaCompressor,
    'attention': AttentionPruningCompressor,

    # 追加分
    'textrank': TextRankCompressor,
    'bm25': BM25Compressor,
    'embedding_topk': EmbeddingTopKCompressor,
}

_instances = {}

def get_compressor(name):
    if name not in REGISTRY:
        raise ValueError(name)
    if name not in _instances:
        _instances[name] = REGISTRY[name]()
    return _instances[name]
