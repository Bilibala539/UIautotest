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
import io
import re
import os
from pathlib import Path

PROJ_ROOT = Path(__file__).parent.parent.parent
KNOWLEDGE_DIR = Path(os.environ.get("UIAUTOTEST_KNOWLEDGE_DIR", PROJ_ROOT / "knowledge/web"))
if not KNOWLEDGE_DIR.is_absolute():
    KNOWLEDGE_DIR = PROJ_ROOT / KNOWLEDGE_DIR
CHROMA_DIR = Path(os.environ.get("UIAUTOTEST_CHROMA_DIR", PROJ_ROOT / ".chroma_db"))
if not CHROMA_DIR.is_absolute():
    CHROMA_DIR = PROJ_ROOT / CHROMA_DIR

# Windows 上强制 stdin/stdout 为 UTF-8（MCP 协议用 JSON UTF-8 通信）
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='')
sys.stderr.reconfigure(encoding='utf-8')


def get_collection():
    """获取 ChromaDB collection"""
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embed_fn = SentenceTransformerEmbeddingFunction(
        model_name=os.environ.get("UIAUTOTEST_EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
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
    """
    为写新用例/AW提供综合上下文（向量搜索 + 图谱关系串联）

    流程:
    1. 向量搜索找到语义相关的 pages/tests/docs
    2. 对命中的 knowledge_pages，读取图谱数据丰富关系信息:
       - backlinks: 谁引用了该页面
       - navigation: 从消息列表页到该页面的路径
       - linked_pages: 该页面引用了哪些其他页面
    3. 组装返回综合上下文
    """
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
                "content_preview": doc[:300],
                "similarity": round(1 - dist, 3),
            })

    # 串联图谱层：对命中的 knowledge_pages 丰富关系信息
    enriched_pages = []
    seen_page_ids = set()
    for item in grouped["knowledge_pages"]:
        page_id = Path(item["source_file"]).stem
        if page_id in seen_page_ids:
            continue
        seen_page_ids.add(page_id)

        graph_info = _enrich_with_graph(page_id)
        enriched_pages.append({
            "page_id": page_id,
            "source_file": item["source_file"],
            "similarity": item["similarity"],
            "content_preview": item["content_preview"],
            **graph_info,
        })

    return {
        "feature": feature_description,
        "related_pages": enriched_pages,
        "similar_tests": grouped["test_cases"],
        "docs": grouped["docs"],
        "recommendation": _generate_recommendation(grouped),
    }


def _enrich_with_graph(page_id: str) -> dict:
    """
    读取图谱层数据文件，为指定页面丰富关系信息。
    直接读文件（不走 MCP 跨进程调用），因为共享同一个数据目录。
    """
    knowledge_dir = KNOWLEDGE_DIR
    app_map_path = knowledge_dir / "app_map.json"
    backlinks_path = knowledge_dir / "backlinks.json"
    pages_dir = knowledge_dir / "pages"

    result = {
        "backlinks": [],
        "linked_pages": [],
        "navigation_from_message_page": None,
    }

    # 读取 backlinks
    try:
        bl_data = json.loads(backlinks_path.read_text(encoding="utf-8-sig"))
        backlinks = bl_data.get("backlinks", {}).get(page_id, [])
        result["backlinks"] = [b["source_id"] for b in backlinks]
    except Exception:
        pass

    # 读取页面中的 [[links]]
    page_file = pages_dir / f"{page_id}.md"
    if not page_file.exists():
        for f in pages_dir.glob("*.md"):
            if f.stem == page_id:
                page_file = f
                break
    if page_file.exists():
        try:
            content = page_file.read_text(encoding="utf-8")
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            result["linked_pages"] = list(set(links))
        except Exception:
            pass

    # 查找从 message_page 到该页面的导航路径（BFS）
    try:
        app_map = json.loads(app_map_path.read_text(encoding="utf-8-sig"))
        transitions = app_map.get("transitions", [])
        path = _bfs_path(transitions, "message_page", page_id)
        if path:
            result["navigation_from_message_page"] = path
    except Exception:
        pass

    return result


def _bfs_path(transitions: list, start: str, end: str) -> list:
    """BFS 找最短导航路径"""
    from collections import deque

    adj = {}
    for t in transitions:
        if t.get("type") == "back":
            continue
        src = t["from"]
        dst = t["to"]
        adj.setdefault(src, []).append({"to": dst, "via": t.get("via", "")})

    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        node, path = queue.popleft()
        if node == end:
            return path
        for edge in adj.get(node, []):
            nxt = edge["to"]
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))

    return None


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
        "description": "为写新用例或AW方法提供综合上下文（向量搜索+图谱关系串联）。返回: related_pages(含backlinks/导航路径/关联页面) + similar_tests + docs",
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
