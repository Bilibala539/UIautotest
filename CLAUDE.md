# UIAutotest 项目约定

> 这份文件是所有 AI 助手（我本人 + `.claude/agents/` 下所有子 agent）每次开工前的第一份必读。
> 变更请慎重，因为它影响整个团队的行为。

## 项目一句话

基于 **pytest + MuMu 模拟器 + ADB** 的安卓 UI 自动化测试框架，针对网易 **POPO** App。图像识别（OpenCV 模板匹配）+ OCR（PaddleOCR）定位。

## 关键路径速查

| 路径 | 用途 |
|---|---|
| `conftest.py` | pytest 全局 fixture |
| `utils/aw/aw_base.py` | AWBase —— 设备交互唯一入口 |
| `utils/aw/business/mumu.py` | 业务 AW 方法层 |
| `utils/user.py` | PPUser —— 暴露给测试用例的便捷方法 |
| `tests/` | pytest 用例 |
| `image/` | **正式**元素图片（跑通后才进） |
| `image_ai/` | **暂存**元素图片（新截的） |
| `image/image_name_mapping.py` | 所有图片常量 |
| `explorer_output/knowledge/` | App 知识库（app_map.json + pages/*.md + digest/） |
| `explorer_output/knowledge/digest/` | 功能摘要 + 跨页面流程 + 关联索引 |
| `explorer_output/knowledge/draft/` | 知识草稿区（explorer 写入，验证后转正到 pages/） |
| `explorer_output/knowledge/backlinks.json` | 反向链接索引（自动生成） |
| `.mcp.json` | MCP Server 注册（knowledge_graph + vector_kb） |
| `mcp_servers/knowledge_graph/` | 图谱查询 MCP（导航路径/反向链接/页面搜索） |
| `mcp_servers/vector_kb/` | 语义检索 MCP（embedding 相似度搜索） |
| `.chroma_db/` | 向量数据库持久化存储 |
| `scripts/knowledge/` | 知识库维护脚本（backlinks/embedding/promote/auto_update） |
| `docs/AW方法总结与复用指南.md` | 已封装业务 AW 清单 —— 写新代码前必查 |
| `docs/UI元素截取与裁剪规范.md` | 元素截图规范 |
| `docs/并行测试执行指南.md` | 多 MuMu 实例并行跑测试 —— 换机器必读 |
| `run_parallel.py` | 并行测试运行器入口 |
| `.codemaker/rules/` | 项目硬性规则（ai_workflow / aw_architecture / rules） |
| `.codemaker/skills/` | 4 把 aw-* skill 原始定义 |
| `openspec/changes/` | 开放提案 |
| `openspec/specs/` | 已归档的能力规范 |

## 硬性规则（任何 agent 都必须遵守）

### 1. 设备交互必须走 AWBase

**严禁**直接 ADB shell、Playwright、浏览器实例、或任何非 AWBase 的工具操作设备。如果 AWBase 没封装某个操作，先在 AWBase 加方法，再调用。

### 2. 禁止 tap 坐标

元素定位一律用 `click_image` 或 `click_text`。坐标会因分辨率、窗口位置变化而失效。

### 3. 分辨率统一 540×960

截图、元素库、测试运行三者的窗口大小必须一致。

### 4. 图片流转：暂存 → 正式

- 新截元素先进 `image_ai/`，`image_name_mapping.py` 里用 `test_path` 常量
- 测试通过后由 aw-verify 转正：文件 `image_ai/ → image/`，mapping 里 `test_path → path`

### 5. 复用优先

写新 AW / 用例前必须先读 `docs/AW方法总结与复用指南.md`。常用便捷方法：
- `user.send_message(recipient, message, isback=False)` —— 进会话发消息
- `user.search(tab, text, isclose=False)` —— 搜索
- `user.open_sidebar()` / `user.open_settings()` —— 打开侧边栏/设置

### 6. 断言优先级

图片断言 > OCR 文字断言。尽量使用截图图像识别，尽量不用 OCR。**禁止"只断言没异常"**。禁止 `try/except` 让失败测试看起来通过。

### 7. 失败归因顺序

`image_exists` / `click_image` 失败时：**先查图片质量，再查代码逻辑**。不要在图片有问题的情况下反复改代码。

### 8. 测试合并

同功能不同参数合并成一个 py 文件用 `@pytest.mark.parametrize`；不要一条文字用例对应一个 py 文件。

## 团队分工

本项目在 `.claude/agents/` 下定义了长期团队角色。主会话作为 **orchestrator** 对接用户；遇到具体任务派给对应 agent：

| 任务特征 | 派给谁 |
|---|---|
| 摸清某个页面怎么走 / 知识库缺页面 | `aw-explorer` |
| 截 UI 元素并注册常量 | `aw-element` |
| 写业务 AW / PPUser 方法 / pytest 用例 | `aw-codegen` |
| 跑 pytest / 诊断失败 / 图片转正 | `aw-verify` |
| openspec 提案 / spec / tasks 维护 | `spec-keeper` |

要一键拉起整个团队：`/bootstrap-team`。

## openspec 流程

涉及新能力或大改动：
1. 走 `openspec-propose`（或 `spec-keeper` agent）生成 change
2. 实现时用 `openspec-apply-change` 推进
3. 完成后 `openspec-archive-change` 归档

当前开放 change：`openspec/changes/agent-team/`（把 4 个 skill 封装成 Python Agent 类的状态机工程化落地）。

## 并行测试执行

checklist 下 138 个用例可用 `run_parallel.py` 并行跑，缩短到约 1/3 耗时。

**机制**：预启动 N 个 MuMu 实例 → 测试文件均匀分片 → N 个独立 pytest 进程各管一个实例（`INSTANCE_ID` 绑定端口 + 账号）。

**账号自动映射**（避免同一账号多设备登录互踢）：
```
INSTANCE_ID=0 → userA (grp.popoqa67)   端口 16384
INSTANCE_ID=1 → userB (grp.popoqa73)   端口 16416
INSTANCE_ID=2 → userC (grp.popoqa74)   端口 16448
INSTANCE_ID=3 → userD (grp.popoqa75)   端口 16480
```
用例无需改动，仍写 `self.users("userA")`，框架按 INSTANCE_ID 自动映射。

**用法**：
```bash
python run_parallel.py                    # 3 实例全量
python run_parallel.py -n 2 -t 5          # 2 实例跑 5 个文件（验证用）
```

**串行模式不受影响**：不设 `INSTANCE_ID` 时 `_device_index` 默认 0，`_user_key_map` 为空，行为不变。

详细原理、换机器检查清单、故障排查见 `docs/并行测试执行指南.md`。

## 知识库系统（双层架构）

知识库采用 **Graph + Embedding** 双层架构，通过 MCP Server 暴露给所有 agent：

### Graph 层（knowledge_graph MCP）
- **数据源**：`explorer_output/knowledge/`（Obsidian vault 格式）
- **能力**：页面搜索、读取页面文档、反向链接查询、BFS 导航路径、关联页面
- **[[双向链接]]**：pages/*.md 中用 `[[page_id]]` 声明关联，`backlinks_generator.py` 自动生成反向引用

### Embedding 层（vector_kb MCP）
- **数据源**：pages/*.md + tests/*.py + docs/*.md → ChromaDB 向量索引
- **能力**：语义搜索、找相似测试用例、综合上下文推荐
- **模型**：paraphrase-multilingual-MiniLM-L12-v2（支持中文）

### 知识更新流程
```
explorer 探索新页面 → 写入 draft/*.md
                       ↓
promote_knowledge.py 验证（结构完整性 + 链接有效性）
                       ↓
验证通过 → 移入 pages/ + 更新 app_map.json
                       ↓
git commit → post-commit hook → auto_update.py
                       ↓
           backlinks 重建 + embedding 增量更新
```

### Agent 使用方式
- 写新用例前：`find_related_context("功能描述")` → 获取页面文档+相似用例+规范
- 找导航路径：`get_navigation_path("起点page_id", "终点page_id")`
- 查谁引用了某页面：`get_backlinks("page_id")`
- 模糊搜索：`semantic_search("自然语言描述")`

### 维护脚本
```bash
python scripts/knowledge/backlinks_generator.py    # 重建反向链接
python scripts/knowledge/embedding_pipeline.py     # 全量重建向量索引
python scripts/knowledge/embedding_pipeline.py --incremental  # 增量更新
python scripts/knowledge/promote_knowledge.py      # 验证并转正草稿
python scripts/knowledge/auto_update.py --force    # 强制全量更新
```

## 禁止事项速查

- ❌ 直接 ADB shell / 绕过 AWBase
- ❌ `tap(x, y)` 坐标点击
- ❌ 截图时窗口不是 540×960
- ❌ 截入动态元素（角标/时间/头像/在线状态）
- ❌ 新元素直接进 `image/`（必须先 `image_ai/`）
- ❌ 不读 AW 复用指南就开始写代码
- ❌ `try/except` 吞掉测试失败
- ❌ 只断言"没异常"
- ❌ 一条用例一个 py 文件（应合并）
- ❌ 不走 openspec 流程直接做大改动

## 运行时经验（踩坑积累，所有 agent 必知）

| 场景 | 正确做法 |
|------|----------|
| MuMu 开关控件点击 | 点 x=450-480, y=555；不要用模板匹配图片 |
| 管理标签页：删除自定义标签页 | 点右侧三点按钮（x≈510）→ 底部弹窗 → 选删除；左侧 icon 只是切换展示/隐藏，不是删除 |
| Python 多行命令 | 走 PowerShell 执行；避免 CodeMaker Hub 路径校验报错 |

<!-- codemap:start -->
## Codemap MCP

**Always use codemap tools for code exploration before falling back to Grep/Read.**

### Tools Quick Reference

| Tool | Use case |
|------|----------|
| `search_code` | Fuzzy keyword or concept search (FTS + vector). For exact name lookup, use find_symbol. |
| `find_symbol` | Exact/prefix/suffix name lookup. Use when you know the symbol name. |
| `get_symbol_detail` | Get a symbol's location, signature, docs, and body. |
| `get_call_chain` | Trace upstream callers and/or downstream callees. |
| `get_type_hierarchy` | Class/interface parent and child hierarchy. |
| `get_dependencies` | Find all symbols that reference a given symbol. |
| `get_graph_stats` | Graph statistics: file/symbol/edge counts. |
| `flame_profile_calls` | Runtime flame profile caller/callee (non-lite mode only). |
| `search_knowledge` | Business rules and architecture docs from codeindex. |
| `query_cypher` | Count/aggregate structural queries: "how many functions in X?", "which class has most methods?", duplicate names, cross-cutting analysis. |

**Name resolution:** Pass `symbol_name` — simple name (`parse_config`) or qualified (`ClassName.method`). No module prefix needed.

**Symbol ID:** `filepath:kind:scopedName` (e.g. `player.py:method:Player.attack`, `models.py:class:Outer.Inner`)

### Slash commands
- `/codemap-exploring` — Explore unfamiliar code
- `/codemap-debugging` — Debug via call chains
- `/codemap-impact-analysis` — Impact analysis before changes

### Rules

- **After `get_symbol_detail`: edit immediately.** Do NOT re-Read the same file.
- **Use `search_code` first**, not broad `find_symbol` prefix queries.
- **Use batch queries:** `search_code({matches: ["A", "B"]})`, `find_symbol({symbol_name: ["X", "Y"]})`.
- **For obvious single-file bugs: skip codemap.** Error → Read → Edit.
- **Counting or aggregation questions** (how many, which has most, rank by): use `query_cypher`, NOT read/grep.

<!-- codemap:end -->
