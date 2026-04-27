from .tfidf import TFIDFCompressor
from .selective import SelectiveContextCompressor
from .llmlingua import LLMLinguaCompressor
from .long_llmlingua import LongLLMLinguaCompressor
from .attention import AttentionPruningCompressor

REGISTRY = {
 'tfidf': TFIDFCompressor,
 'selective': SelectiveContextCompressor,
 'llmlingua': LLMLinguaCompressor,
 'longlingua': LongLLMLinguaCompressor,
 'attention': AttentionPruningCompressor,
}

_instances={}
def get_compressor(name):
    if name not in REGISTRY:
        raise ValueError(name)
    if name not in _instances:
        _instances[name]=REGISTRY[name]()
    return _instances[name]
