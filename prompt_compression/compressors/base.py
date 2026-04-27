from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import time
from prompt_compression.utils.models import token_len

@dataclass
class CompressionResult:
    original: str
    compressed: str
    method: str
    original_tokens: int
    compressed_tokens: int
    latency_ms: float
    ratio: float = field(init=False)

    def __post_init__(self):
        self.ratio = 1 - (self.compressed_tokens / max(self.original_tokens, 1))

class BaseCompressor(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def _compress(self, text: str, ratio: float) -> str: ...

    def compress(self, text: str, ratio: float = 0.5) -> CompressionResult:
        original_tokens = token_len(text)
        start = time.time()
        compressed = self._compress(text, ratio)
        latency_ms = (time.time() - start) * 1000
        return CompressionResult(
            original=text,
            compressed=compressed,
            method=self.name,
            original_tokens=original_tokens,
            compressed_tokens=token_len(compressed),
            latency_ms=latency_ms,
        )
