from mcp.server.fastmcp import FastMCP
from prompt_compression.pipeline.smart_llm import smart_llm

mcp = FastMCP("prompt-compression")

@mcp.tool()
def compress_and_answer(prompt: str, ratio: float = 0.3) -> str:
    result = smart_llm(prompt, compression_ratio=ratio)
    return result["response"]

if __name__ == "__main__":
    mcp.run()
