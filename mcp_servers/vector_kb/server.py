"""
Vector KB MCP Server

为 Claude Code agents 提供语义检索能力：
- semantic_search: 自然语言搜索知识库
- find_similar_tests: 找到与描述相似的测试用例
- find_related_context: 为写新用例/AW提供相关上下文

启动: python mcp_servers/vector_kb/server.py
协议: MCP (stdin/stdout JSON-RPC)
"""

import json
import sys
from pathlib import Path

PROJ_ROOT = Path(__file__).parent.parent.parent
CHROMA_DIR = PROJ_ROOT / ".chroma_db"

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def get_collection():
    """获取 ChromaDB collection"""
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embed_fn = SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
    return client.get_collection(
        name="knowledge_base",
        embedding_function=embed_fn,
    )


def semantic_search(query: str, n_results: int = 5, source_type: str = None) -> dict:
    """语义搜索知识库"""
    collection = get_collection()

    where_filter = None
    if source_type:
        where_filter = {"source_type": source_type}

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter,
    )

    items = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        items.append({
            "content": doc[:500],
            "source_file": meta["source_file"],
            "source_type": meta["source_type"],
            "similarity": round(1 - dist, 3),
            "chunk_info": f"{meta['chunk_index']+1}/{meta['total_chunks']}",
        })

    return {
        "query": query,
        "results": items,
        "total": len(items),
    }


def find_similar_tests(description: str, n_results: int = 5) -> dict:
    """找到与描述相似的已有测试用例"""
    collection = get_collection()

    results = collection.query(
        query_texts=[description],
        n_results=n_results,
        where={"source_type": "test_cases"},
    )

    items = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        items.append({
            "test_file": meta["source_file"],
            "content_preview": doc[:300],
            "similarity": round(1 - dist, 3),
        })

    return {
        "description": description,
        "similar_tests": items,
    }


def find_related_context(feature_description: str, n_results: int = 8) -> dict:
    """为写新用例/AW提供综合上下文（跨所有来源类型搜索）"""
    collection = get_collection()

    results = collection.query(
        query_texts=[feature_description],
        n_results=n_results,
    )

    # 按来源类型分组
    grouped = {
        "knowledge_pages": [],
        "knowledge_digest": [],
        "test_cases": [],
        "docs": [],
    }

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        source_type = meta["source_type"]
        if source_type in grouped:
            grouped[source_type].append({
                "source_file": meta["source_file"],
                "content_preview": doc[:200],
                "similarity": round(1 - dist, 3),
            })

    return {
        "feature": feature_description,
        "context": grouped,
        "recommendation": _generate_recommendation(grouped),
    }


def _generate_recommendation(grouped: dict) -> str:
    """基于搜索结果生成建议"""
    rec = []
    if grouped["knowledge_pages"]:
        rec.append(f"相关页面文档: {grouped['knowledge_pages'][0]['source_file']}")
    if grouped["test_cases"]:
        rec.append(f"参考用例: {grouped['test_cases'][0]['source_file']}")
    if grouped["docs"]:
        rec.append(f"相关文档: {grouped['docs'][0]['source_file']}")
    return " | ".join(rec) if rec else "未找到强相关上下文"


# === MCP Protocol Handler ===

TOOLS = [
    {
        "name": "semantic_search",
        "description": "语义搜索知识库（页面文档+测试用例+开发文档），返回最相关的内容片段",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "自然语言查询（如'会话分组功能'、'群设置页导航'）"},
                "n_results": {"type": "integer", "description": "返回结果数（默认5）", "default": 5},
                "source_type": {
                    "type": "string",
                    "description": "限定来源类型: knowledge_pages/knowledge_digest/test_cases/docs",
                    "enum": ["knowledge_pages", "knowledge_digest", "test_cases", "docs"],
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "find_similar_tests",
        "description": "根据功能描述找到相似的已有测试用例，用于参考和避免重复",
        "inputSchema": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "要实现的测试功能描述"},
                "n_results": {"type": "integer", "description": "返回结果数（默认5）", "default": 5},
            },
            "required": ["description"],
        },
    },
    {
        "name": "find_related_context",
        "description": "为写新用例或AW方法提供综合上下文（页面文档+相似用例+开发规范）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "feature_description": {"type": "string", "description": "要实现的功能/用例描述"},
                "n_results": {"type": "integer", "description": "每类来源返回数（默认8）", "default": 8},
            },
            "required": ["feature_description"],
        },
    },
]


def handle_request(request: dict) -> dict:
    """处理 MCP JSON-RPC 请求"""
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "vector-kb",
                    "version": "1.0.0",
                },
            },
        }

    elif method == "notifications/initialized":
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS},
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "semantic_search":
                result = semantic_search(
                    arguments["query"],
                    arguments.get("n_results", 5),
                    arguments.get("source_type"),
                )
            elif tool_name == "find_similar_tests":
                result = find_similar_tests(
                    arguments["description"],
                    arguments.get("n_results", 5),
                )
            elif tool_name == "find_related_context":
                result = find_related_context(
                    arguments["feature_description"],
                    arguments.get("n_results", 8),
                )
            else:
                result = {"error": f"未知工具: {tool_name}"}

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
                },
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"错误: {str(e)}"}],
                    "isError": True,
                },
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main():
    """MCP stdio transport main loop"""
    sys.stderr.write("Vector KB MCP Server started\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = handle_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            sys.stderr.write(f"Invalid JSON: {line}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    main()
