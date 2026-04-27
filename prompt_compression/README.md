# Prompt Compression (MCP + FastAPI)

## Overview
本プロジェクトは、複数のプロンプト圧縮手法（compressor）を比較・評価し、最適な圧縮結果を用いてLLM推論を行うパイプラインを提供するものである。  
同一のコアロジックを、**MCPサーバー**および**FastAPI**の両インターフェースから利用可能とする構成になっている。

---

## Architecture

[MCP Client]        [HTTP Client]
      │                    │
      ▼                    ▼
   MCP Server         FastAPI Server
           \          /
            ▼        ▼
             smart_llm
                 │
 ┌───────────────┼───────────────┐
 ▼               ▼               ▼
compressors   evaluator       cache
                                  │
                                  ▼
                                Redis

---

## Features

- 複数compressorの並列実行
- 評価（ROUGE + embedding）
- セマンティックキャッシュ
- MCP + FastAPI デュアルインターフェース

---

## Requirements

- Python 3.10+
- Redis（外部サービス）

---

## ⚠️ Redisについて（重要）

Redisは**外部サービスとして起動する必要がある**。  
コード内で起動はしない。

### ローカル

```bash
redis-server
