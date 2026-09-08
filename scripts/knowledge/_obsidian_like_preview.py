"""本地 Obsidian-like 预览：把 pages/*.md 渲染成 HTML，提供：
- frontmatter 折叠表格
- [[wikilink]] 解析（含 alias）和点击跳转
- 反向链接段折叠
- mermaid 渲染
- 简易页面索引侧栏

启动后浏览器自动打开 http://127.0.0.1:8765
"""
import http.server
import socketserver
import urllib.parse
import re
import json
import sys
import io
import webbrowser
import os
import argparse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PROJ = Path(__file__).resolve().parents[2]
KM = Path(os.environ.get("UIAUTOTEST_KNOWLEDGE_DIR", PROJ / "knowledge/web"))
if not KM.is_absolute():
    KM = PROJ / KM
PAGES = KM / "pages"
DRAFT = KM / "draft"

PORT = 8765

FRONTMATTER_PATTERN = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)
LINK_PATTERN = re.compile(r'\[\[([^\]]+?)\]\]')


def parse_frontmatter(content: str):
    m = FRONTMATTER_PATTERN.match(content)
    if not m:
        return {}, content
    body = m.group(1)
    fm = {}
    cur = None
    for line in body.split('\n'):
        s = line.rstrip()
        if not s:
            continue
        if line.startswith('  - ') and cur:
            fm.setdefault(cur, [])
            if isinstance(fm[cur], list):
                fm[cur].append(line[4:].strip().strip('"\''))
            continue
        if ':' in s and not s.startswith(' '):
            k, _, v = s.partition(':')
            cur = k.strip()
            v = v.strip()
            if v == '':
                fm[cur] = []
            elif v.startswith('[') and v.endswith(']'):
                fm[cur] = [x.strip().strip('"\'') for x in v[1:-1].split(',') if x.strip()]
            else:
                fm[cur] = v.strip('"\'')
    return fm, content[m.end():]


def build_alias_map():
    idx = {}
    for d in (PAGES, DRAFT):
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            idx[f.stem] = f
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue
            fm, _ = parse_frontmatter(content)
            pid = fm.get("page_id")
            if isinstance(pid, str):
                idx.setdefault(pid, f)
            for a in fm.get("aliases", []) or []:
                idx.setdefault(a, f)
    return idx


def md_to_html(md_text: str, alias_map: dict) -> str:
    """简易 markdown -> html，支持 wikilink、表格、code、mermaid"""
    import markdown as md_lib

    # wikilink 替换
    def wl(m):
        target = m.group(1)
        # 别名形式 [[target|display]]
        if '|' in target:
            t, disp = target.split('|', 1)
        else:
            t, disp = target, target
        f = alias_map.get(t)
        if f:
            href = f"/page/{f.parent.name}/{f.stem}"
            return f'<a class="wl" href="{href}">{disp}</a>'
        else:
            return f'<a class="wl broken" href="#" title="未找到目标">{disp} ⚠</a>'

    md_text = LINK_PATTERN.sub(wl, md_text)

    # mermaid 代码块 -> div
    def mermaid_replace(m):
        code = m.group(1)
        return f'<div class="mermaid">{code}</div>'
    md_text = re.sub(r'```mermaid\n(.*?)```', mermaid_replace, md_text, flags=re.DOTALL)

    html = md_lib.markdown(md_text, extensions=['tables', 'fenced_code'])
    return html


def render_frontmatter(fm: dict) -> str:
    if not fm:
        return ""
    rows = []
    for k, v in fm.items():
        if isinstance(v, list):
            display = ", ".join(v) if v else "—"
        else:
            display = v
        rows.append(f"<tr><td><b>{k}</b></td><td>{display}</td></tr>")
    return f"""<details open class="frontmatter"><summary>📋 frontmatter</summary>
<table>{''.join(rows)}</table></details>"""


def render_page(rel_dir: str, stem: str, alias_map: dict) -> str:
    f = (KM / rel_dir / f"{stem}.md")
    if not f.exists():
        return f"<h1>404</h1><p>{f}</p>"
    content = f.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    # 切出反向引用段
    bl_start = "<!-- backlinks:start -->"
    bl_end = "<!-- backlinks:end -->"
    backlinks_html = ""
    if bl_start in body and bl_end in body:
        i, j = body.index(bl_start), body.index(bl_end) + len(bl_end)
        bl_block = body[i:j].replace(bl_start, "").replace(bl_end, "")
        backlinks_html = md_to_html(bl_block, alias_map)
        body = body[:body.rindex("## 反向引用")] if "## 反向引用" in body else body[:i]

    fm_html = render_frontmatter(fm)
    body_html = md_to_html(body, alias_map)

    return f"""
<div class="page">
  {fm_html}
  {body_html}
  <details class="backlinks"><summary>🔙 反向引用</summary>{backlinks_html}</details>
</div>
"""


PAGE_TPL = """<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  body {{ margin: 0; font-family: -apple-system, "Microsoft YaHei", sans-serif; background: #1e1e1e; color: #ddd; }}
  .layout {{ display: flex; min-height: 100vh; }}
  .sidebar {{ width: 280px; background: #252525; padding: 12px; overflow-y: auto; height: 100vh; box-sizing: border-box; }}
  .sidebar h3 {{ color: #aaa; font-size: 12px; text-transform: uppercase; margin: 14px 0 6px; }}
  .sidebar a {{ display: block; color: #88c; padding: 4px 8px; text-decoration: none; border-radius: 3px; font-size: 13px; }}
  .sidebar a:hover {{ background: #333; }}
  .sidebar a.draft {{ color: #c89; }}
  .main {{ flex: 1; padding: 28px 56px; max-width: 900px; }}
  h1 {{ color: #4ec9b0; border-bottom: 1px solid #444; padding-bottom: 8px; }}
  h2 {{ color: #569cd6; margin-top: 28px; }}
  h3 {{ color: #9cdcfe; }}
  table {{ border-collapse: collapse; margin: 12px 0; width: 100%; }}
  td, th {{ border: 1px solid #444; padding: 6px 10px; }}
  th {{ background: #2d2d2d; }}
  code {{ background: #2d2d2d; padding: 1px 5px; border-radius: 3px; color: #ce9178; }}
  pre {{ background: #181818; padding: 12px; border-radius: 4px; overflow-x: auto; border: 1px solid #333; }}
  pre code {{ background: transparent; }}
  a.wl {{ color: #4fc3f7; text-decoration: none; padding: 1px 4px; border-radius: 3px; background: rgba(79,195,247,0.1); }}
  a.wl:hover {{ background: rgba(79,195,247,0.25); }}
  a.wl.broken {{ color: #f48771; background: rgba(244,135,113,0.15); }}
  details.frontmatter, details.backlinks {{ margin: 12px 0; padding: 8px 12px; background: #252525; border-left: 3px solid #569cd6; border-radius: 4px; }}
  details.frontmatter summary {{ cursor: pointer; color: #569cd6; font-weight: bold; }}
  details.backlinks summary {{ cursor: pointer; color: #b5cea8; font-weight: bold; }}
  blockquote {{ border-left: 3px solid #666; padding: 4px 12px; color: #aaa; margin: 12px 0; }}
  .mermaid {{ background: #fff; padding: 14px; border-radius: 4px; }}
</style>
</head><body>
<div class="layout">
  <div class="sidebar">
    <h3>📚 pages ({n_pages})</h3>{nav_pages}
    <h3>📝 draft ({n_drafts})</h3>{nav_drafts}
  </div>
  <div class="main">
    {body}
  </div>
</div>
<script>mermaid.initialize({{startOnLoad: true, theme: 'default'}});</script>
</body></html>
"""


def render_index(alias_map):
    # 统计
    total_pages = len(list(PAGES.glob("*.md")))
    total_drafts = len(list(DRAFT.glob("*.md")))
    total_aliases = len(alias_map)

    # 按 frontmatter status 分组
    by_status = {}
    for f in PAGES.glob("*.md"):
        fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
        st = fm.get("status", "—")
        by_status.setdefault(st, []).append(f.stem)

    rows = ""
    for st, names in by_status.items():
        rows += f"<tr><td><b>{st}</b></td><td>{len(names)}</td></tr>"

    return f"""
<h1>TidiTree 知识库 — 本地 Obsidian-like 视图</h1>
<p>这是用 markdown 渲染器模拟 Obsidian 阅读视图，支持 wikilink 跳转、frontmatter 折叠、mermaid 图表。</p>

<h2>📊 统计</h2>
<table>
<tr><th>指标</th><th>值</th></tr>
<tr><td>pages 实体</td><td>{total_pages}</td></tr>
<tr><td>draft 草稿</td><td>{total_drafts}</td></tr>
<tr><td>alias 索引（page_id + 文件 stem + 别名）</td><td>{total_aliases}</td></tr>
{rows}
</table>

<h2>🚀 推荐入口</h2>
<ul>
<li>主页：<a class="wl" href="/page/pages/消息列表页">消息列表页</a></li>
<li>聊天：<a class="wl" href="/page/pages/聊天页面(P2P-群聊)">聊天页面(P2P-群聊)</a></li>
<li>群设置：<a class="wl" href="/page/pages/群设置页">群设置页</a></li>
<li>导航编辑：<a class="wl" href="/page/pages/导航栏编辑模式">导航栏编辑模式</a></li>
<li>图谱：<a class="wl" href="/graph">graph_view.md</a></li>
</ul>

<h2>🔗 alias 抽样测试</h2>
<p>以下 wikilink 全应跳到中文实体：</p>
<ul>
<li><a class="wl" href="/page/pages/消息列表页">[[message_page]]</a> → 消息列表页</li>
<li><a class="wl" href="/page/pages/聊天页面(P2P-群聊)">[[chat_page]]</a> → 聊天页面(P2P-群聊)</li>
<li><a class="wl" href="/page/pages/聊天页面(P2P-群聊)">[[聊天页]]</a>（旧别名） → 聊天页面(P2P-群聊)</li>
<li><a class="wl" href="/page/pages/搜索页面">[[search_page]]</a> → 搜索页面</li>
</ul>
"""


def build_nav():
    rows_pages = []
    for f in sorted(PAGES.glob("*.md")):
        rows_pages.append(f'<a href="/page/pages/{f.stem}">{f.stem}</a>')
    rows_drafts = []
    for f in sorted(DRAFT.glob("*.md")):
        if f.name == ".gitkeep":
            continue
        rows_drafts.append(f'<a class="draft" href="/page/draft/{f.stem}">{f.stem}</a>')
    return ("\n".join(rows_pages), "\n".join(rows_drafts),
            len(rows_pages), len(rows_drafts))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.alias_map = build_alias_map()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        path = urllib.parse.unquote(self.path)
        nav_pages, nav_drafts, n_pages, n_drafts = build_nav()

        if path in ("/", "/index"):
            body = render_index(self.alias_map)
            title = "TidiTree 知识库"
        elif path == "/graph":
            f = KM / "graph_view.md"
            content = f.read_text(encoding="utf-8")
            body = md_to_html(content, self.alias_map)
            title = "graph_view"
        elif path.startswith("/page/"):
            parts = path[len("/page/"):].split("/")
            if len(parts) >= 2:
                rel_dir, stem = parts[0], "/".join(parts[1:])
                body = render_page(rel_dir, stem, self.alias_map)
                title = stem
            else:
                body = "<h1>bad path</h1>"
                title = "404"
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"not found")
            return

        html = PAGE_TPL.format(title=title, body=body, nav_pages=nav_pages,
                               nav_drafts=nav_drafts, n_pages=n_pages, n_drafts=n_drafts)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, *args):
        pass  # 静音


def main():
    global KM, PAGES, DRAFT, PORT
    parser = argparse.ArgumentParser(description="知识库本地预览")
    parser.add_argument("--knowledge-dir", type=str, help="知识库目录（默认 Web 知识库）")
    parser.add_argument("--port", type=int, default=PORT, help="本地预览端口")
    args = parser.parse_args()
    if args.knowledge_dir:
        KM = Path(args.knowledge_dir)
        if not KM.is_absolute():
            KM = PROJ / KM
        PAGES = KM / "pages"
        DRAFT = KM / "draft"
    PORT = args.port
    print(f"[obsidian-like] 启动 http://127.0.0.1:{PORT}")
    print(f"[obsidian-like] 知识库根: {KM}")
    try:
        webbrowser.open(f"http://127.0.0.1:{PORT}")
    except Exception:
        pass
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
