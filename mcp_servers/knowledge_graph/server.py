"""
Knowledge Graph MCP Server

为 Claude Code agents 提供知识库图谱查询能力：
- search_pages: 按关键词搜索页面
- get_page: 读取指定页面文档
- get_backlinks: 查询谁引用了指定页面
- get_navigation_path: 查询两个页面之间的导航路径
- get_related_pages: 获取与指定页面相关的所有页面
- list_pages: 列出所有已知页面

启动: python mcp_servers/knowledge_graph/server.py
协议: MCP (stdin/stdout JSON-RPC)
"""

import json
import re
import sys
import io
from pathlib import Path
from collections import deque

# Windows 上强制 stdin/stdout 为 UTF-8（MCP 协议用 JSON UTF-8 通信）
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='')

KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "explorer_output" / "knowledge"
PAGES_DIR = KNOWLEDGE_DIR / "pages"
APP_MAP_PATH = KNOWLEDGE_DIR / "app_map.json"
BACKLINKS_PATH = KNOWLEDGE_DIR / "backlinks.json"


def load_app_map():
    if APP_MAP_PATH.exists():
        return json.loads(APP_MAP_PATH.read_text(encoding="utf-8-sig"))
    return {"pages": {}, "transitions": []}


def load_backlinks():
    if BACKLINKS_PATH.exists():
        return json.loads(BACKLINKS_PATH.read_text(encoding="utf-8-sig"))
    return {"backlinks": {}, "forward_index": {}}


def search_pages(query: str) -> list:
    """搜索页面：在页面名称、内容中匹配关键词"""
    results = []
    query_lower = query.lower()

    for md_file in PAGES_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        name = md_file.stem

        score = 0
        if query_lower in name.lower():
            score += 10
        if query_lower in content.lower():
            score += content.lower().count(query_lower)

        if score > 0:
            # 提取第一行作为标题
            first_line = content.split('\n')[0].lstrip('# ')
            results.append({
                "page_id": name,
                "title": first_line,
                "score": score,
                "file": str(md_file.relative_to(KNOWLEDGE_DIR)),
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10]


def get_page(page_id: str) -> dict:
    """获取页面完整内容"""
    filepath = PAGES_DIR / f"{page_id}.md"
    if not filepath.exists():
        # 尝试中文名
        for f in PAGES_DIR.glob("*.md"):
            if f.stem == page_id:
                filepath = f
                break
        else:
            return {"error": f"页面不存在: {page_id}"}

    content = filepath.read_text(encoding="utf-8")
    app_map = load_app_map()
    page_info = app_map.get("pages", {}).get(page_id, {})

    return {
        "page_id": page_id,
        "content": content,
        "metadata": page_info,
    }


def get_backlinks(page_id: str) -> dict:
    """查询谁引用了指定页面"""
    bl_data = load_backlinks()
    backlinks = bl_data.get("backlinks", {}).get(page_id, [])
    return {
        "page_id": page_id,
        "referenced_by": backlinks,
        "count": len(backlinks),
    }


def get_navigation_path(from_page: str, to_page: str) -> dict:
    """使用 BFS 查找两个页面之间的最短导航路径"""
    app_map = load_app_map()
    transitions = app_map.get("transitions", [])

    # 构建邻接表
    graph = {}
    for t in transitions:
        src = t["from"]
        if src not in graph:
            graph[src] = []
        graph[src].append({
            "to": t["to"],
            "via": t.get("via", ""),
            "action": t.get("action", {}),
            "type": t.get("type", ""),
        })

    # BFS
    queue = deque([(from_page, [from_page])])
    visited = {from_page}

    while queue:
        current, path = queue.popleft()
        if current == to_page:
            # 构建步骤描述
            steps = []
            for i in range(len(path) - 1):
                src = path[i]
                dst = path[i + 1]
                for edge in graph.get(src, []):
                    if edge["to"] == dst:
                        steps.append({
                            "from": src,
                            "to": dst,
                            "via": edge["via"],
                            "action": edge["action"],
                        })
                        break
            return {
                "found": True,
                "from": from_page,
                "to": to_page,
                "path": path,
                "steps": steps,
                "hops": len(path) - 1,
            }

        for edge in graph.get(current, []):
            if edge["to"] not in visited and edge.get("type") != "back":
                visited.add(edge["to"])
                queue.append((edge["to"], path + [edge["to"]]))

    return {
        "found": False,
        "from": from_page,
        "to": to_page,
        "message": f"未找到从 {from_page} 到 {to_page} 的路径",
    }


def get_related_pages(page_id: str) -> dict:
    """获取与指定页面相关的所有页面（正向链接 + 反向链接 + 导航邻居）"""
    app_map = load_app_map()
    bl_data = load_backlinks()

    related = {
        "navigates_to": [],
        "navigates_from": [],
        "links_to": [],
        "linked_by": [],
    }

    # 从 transitions 提取导航关系
    for t in app_map.get("transitions", []):
        if t["from"] == page_id:
            related["navigates_to"].append({"page": t["to"], "via": t.get("via", "")})
        if t["to"] == page_id:
            related["navigates_from"].append({"page": t["from"], "via": t.get("via", "")})

    # 从 forward_index 提取正向链接
    for source, targets in bl_data.get("forward_index", {}).items():
        source_id = Path(source).stem
        if source_id == page_id:
            related["links_to"] = targets

    # 从 backlinks 提取反向链接
    backlinks = bl_data.get("backlinks", {}).get(page_id, [])
    related["linked_by"] = [b["source_id"] for b in backlinks]

    return {"page_id": page_id, "related": related}


def list_pages() -> list:
    """列出所有已知页面"""
    app_map = load_app_map()
    pages = []
    for pid, info in app_map.get("pages", {}).items():
        pages.append({
            "page_id": pid,
            "name": info.get("name", pid),
            "type": info.get("type", "unknown"),
            "has_detail": info.get("detail") is not None,
        })
    return pages


# === MCP Protocol Handler ===

TOOLS = [
    {
        "name": "search_pages",
        "description": "按关键词搜索知识库页面（页面名称和内容）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_page",
        "description": "获取指定页面的完整文档内容和元信息",
        "inputSchema": {
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "页面ID（如 message_page, group_settings）"}
            },
            "required": ["page_id"],
        },
    },
    {
        "name": "get_backlinks",
        "description": "查询哪些页面引用了指定页面（反向链接）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "目标页面ID"}
            },
            "required": ["page_id"],
        },
    },
    {
        "name": "get_navigation_path",
        "description": "查询从页面A到页面B的最短导航路径（BFS）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "from_page": {"type": "string", "description": "起始页面ID"},
                "to_page": {"type": "string", "description": "目标页面ID"},
            },
            "required": ["from_page", "to_page"],
        },
    },
    {
        "name": "get_related_pages",
        "description": "获取与指定页面相关的所有页面（导航邻居+链接关系）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "页面ID"}
            },
            "required": ["page_id"],
        },
    },
    {
        "name": "list_pages",
        "description": "列出知识库中所有已知页面",
        "inputSchema": {
            "type": "object",
            "properties": {},
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
                    "name": "knowledge-graph",
                    "version": "1.0.0",
                },
            },
        }

    elif method == "notifications/initialized":
        return None  # no response for notifications

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
            if tool_name == "search_pages":
                result = search_pages(arguments["query"])
            elif tool_name == "get_page":
                result = get_page(arguments["page_id"])
            elif tool_name == "get_backlinks":
                result = get_backlinks(arguments["page_id"])
            elif tool_name == "get_navigation_path":
                result = get_navigation_path(arguments["from_page"], arguments["to_page"])
            elif tool_name == "get_related_pages":
                result = get_related_pages(arguments["page_id"])
            elif tool_name == "list_pages":
                result = list_pages()
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
    sys.stderr.write("Knowledge Graph MCP Server started\n")
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
