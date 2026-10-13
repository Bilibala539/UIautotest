# UIAutotest 多项目自动化测试项目约定

> 这份文件是所有 AI 助手（我本人 + `.claude/agents/` 下所有子 agent）每次开工前的第一份必读。
> 变更请慎重，因为它影响整个团队的行为。
>
> 铁律：所有输出一律中文（包括系统提示）。

## 项目一句话

基于 **pytest** 的多项目 UI 自动化测试框架（双维度架构：基础 AW 按端分，业务 AW 按项目分）。

**当前项目**：
| 项目 | 端 | 用户类 | 业务类 | 知识库 |
|---|---|---|---|---|
| TidiTree | Web | `TTUser` | `TidiTreeBusiness` | `knowledge/web/` |
| Swan（音乐 App） | Flutter (Android) | `SwanUser` | `SwanBusiness` | `knowledge/swan/` |
| 智能音箱显示屏系统（名称待定） | Android | `AndroidUser` | `AndroidBusiness` | `knowledge/android/` |

架构细则见 `docs/aw-architecture.html`、`.claude/rules/aw_architecture.mdc`；各项目 agent 编排见 `docs/agents/<project>/`。

## 关键路径速查

| 路径 | 用途 |
|---|---|
| `conftest.py` | pytest 全局 fixture |
| `utils/aw/aw_base.py` | AWBase —— 公共引擎（OCR/截图/图像匹配），设备交互唯一入口 |
| `utils/aw/base/` | 基础 AW 按端分：`web_base.py` / `android_base.py` / `flutter_base.py` |
| `utils/aw/business/` | 业务 AW 按项目分：`tiditree.py` / `swan.py` / `android.py` + `common.py`（跨项目 Mixin） |
| `utils/user.py` | `User` 基类 + `TTUser` / `SwanUser` / `AndroidUser`（`__getattr__` 代理业务方法） |
| `tests/` | pytest 用例 |
| `image/web/`、`image/android/`、`image/flutter/` | **正式**元素图片（跑通后才进；flutter=Swan 端 62 张已转正） |
| `image_ai/web/`、`image_ai/android/`、`image_ai/flutter/` | **暂存**元素图片（新截的） |
| `image/image_name_mapping.py` | 平台图片路径与转正工具 |
| `knowledge/web/` | TidiTree Web 知识库（app_map.json + pages/*.md + digest/） |
| `knowledge/swan/` | Swan（Flutter）独立知识库（与 Web/Android 页面、索引和向量库隔离） |
| `knowledge/android/` | 智能音箱显示屏系统（Android）独立知识库 |
| `knowledge/web/digest/` 等 | 功能摘要 + 跨页面流程 + 关联索引 |
| `knowledge/*/draft/` | 知识草稿区（explorer 写入，验证后转正到 pages/） |
| `knowledge/*/backlinks.json` | 反向链接索引（自动生成） |
| `.mcp.json` | MCP Server 注册（web/swan/android 各自的 knowledge_graph* + vector_kb*） |
| `mcp_servers/knowledge_graph/` | 图谱查询 MCP（导航路径/反向链接/页面搜索） |
| `mcp_servers/vector_kb/` | 语义检索 MCP（embedding 相似度搜索） |
| `.chroma_db/` 等 | 向量数据库持久化存储（web/swan/android 各自独立目录） |
| `scripts/knowledge/` | 知识库维护脚本（backlinks/embedding/promote/auto_update） |
| `docs/UI元素截取与裁剪规范.md` | 元素截图规范 |
| `docs/agents/swan/AW方法指南.md` | Swan 已有 AW 方法查询入口（写新用例/AW 前必查，防重复创建） |
| `docs/待办与缺口清单.md` | **当前权威 plan**：已拍板决定 + 文档/环境缺口，开工前必读 |
| `docs/runtime_experience.md` | 运行时经验知识库（子 Agent 执行经验沉淀，供语义检索注入） |
| `run_parallel.py` | 并行测试运行器入口 |
| `.claude/rules/` | 流程与架构规则（ai_workflow / aw_architecture）；编码规范已并入本文件 |

## 硬性规则（任何 agent 都必须遵守）

### 1. 设备交互必须走 AWBase

**严禁**绕过 AWBase 直接操作浏览器。如果 AWBase 没封装某个操作，先在 AWBase 或平台驱动中加方法，再调用。

### 2. 定位策略：图像模板 > OCR 文本，不用 key，禁止 tap 坐标

元素定位一律用 `click_image`（首选）或 `click_text`（次选）；坐标会因分辨率、窗口位置变化而失效。
**accessibility key 只用于探索辅助**（explorer 导航指引、认识元素、截图取元素参考），`click_accessibility`/`wait_accessibility`/`accessibility_exists` 仅限 explorer 探索与调试。
自动化用例运行时的点击/长按/断言一律图片定位，禁止 key。

### 3. 浏览器截图坐标

截图、元素库、测试运行三者的 viewport 尺寸必须一致；默认 1440×900，可通过环境变量调整。

### 4. 图片流转：暂存 → 正式

- 新截元素先进对应平台的 `image_ai/<platform>/`，用 `image_path(..., draft=True)` 登记
- 测试通过后由 aw-verify 调用 `promote_image(...)` 转正到 `image/<platform>/`

### 5. 基础操作优先

业务方法按 TidiTree 页面单独设计；基础操作统一使用 `user.aw.click_text`、`user.aw.click_image`、`user.aw.text_exists`、`user.aw.input_text`。

### 6. 断言优先级

图片断言 > OCR 文字断言。尽量使用截图图像识别，尽量不用 OCR。**禁止"只断言没异常"**。禁止 `try/except` 让失败测试看起来通过。

### 7. 失败归因顺序

`image_exists` / `click_image` 失败时：**先查图片质量，再查代码逻辑**。不要在图片有问题的情况下反复改代码。

### 8. 一用例一文件一 test 方法（铁律）

每个用例 .py 文件**有且仅有一个 `test_` 方法**；不同测试场景、不同数据变体各自独立成文件，**值写死在用例里**。**严禁使用 `@pytest.mark.parametrize`**（2026-10-13 拍板：参数装饰器=一个文件跑多条，等价于一文件多用例）。适用本工程全部平台（web/android/flutter）。例外仅限 `tests/flutter/test_case_driver.py`（平台 YAML 用例执行载体）。用例间共用的前置/清理编排沉到业务层（`utils/aw/business/`，如 `swan_regression.py`）。

### 9. 框架层改动须用户决策

以下属于框架层：`utils/aw/driver/`、`conftest.py`、`run_parallel.py`

修用例/写用例过程中发现框架层有问题时：
- **不要自己改** — 报告给用户，说明问题现象和初步判断
- **由用户决定**是否改、怎么改
- "加 fallback"、"加自动探测"、"加环境适配"都算框架层改动

### 10. 禁止"图片匹配失败→坐标回退"模式

当 `click_image` / `image_exists` 失败时，**禁止**加 `tap(x, y)` 作为 fallback。
正确做法：先查图片质量（规则7），重截图或调阈值。坐标回退是伪修复，换环境必坏。

## 平台开发进度恢复(新会话/新窗口必读)

接手 Swan 测试平台相关工作前,先读这两份拿到全貌,再接着干:
1. `docs/agent团队名册.md` —— 团队角色、硬性纪律、交接记录(最新进度看这里)
2. `docs/测试套件管理计划.md` —— 总体里程碑 M1-M6 与当前所处阶段

硬性纪律速记:凭据只在 .167 /opt/uiautotest/.env.local;模块 agent 不部署不提交 git(主会话统一做);运行面(.167/.176)绝不 kill 全部进程,只杀指定 PID。

## 用例域纪律(一库两服务,2026-10-13 起)

工作站(:8090,`/opt/app`)与测试平台(:8080)**共库**:唯一数据源 `/opt/uiautotest/output/dashboard.sqlite3` 的 `case_defs` 表,两边展示与增删改查打同一张表(方案与遗留待办:`docs/用例域整合计划.md`)。

- **文字用例(text)**:工作站创作/维护,编号沿用工作站 `launch-NEG-001` 式(不重编号);正文 `structured` 列(机器读原始报文)+ `content` 列(人读渲染),人审状态在 `review_meta` 列。**新文字用例请勿手写 YAML/文件,直接在工作站或平台 API 建**
- **自动化用例(auto)**:case_id = `aw-<py文件主干>`(去 `test_` 前缀,中文保留,如 `aw-冷启动落页`);由 `scripts/sync_cases.py` 扫描 `tests/flutter/test_*.py` 文件头标记入库。**改挂接关系 = 改文件头标记再重跑 sync,勿直改库**
- **py 文件头标记格式**(`sync_cases.py --annotate` 可补写;pytest 上报按 CASE-ID 聚合,parametrize 变体同文件共享一个编号):
  ```
  # CASE-ID: aw-冷启动落页
  # LINKED-CASE: REG-015,REG-016
  ```
- **旧 76 条 REG-xxx** 保留作挂接锚点(D1 默认);docstring"回归用例 N"锚点已迁移到文件头 LINKED-CASE 标记,新用例一律用标记行

## 团队分工

本项目在 `.claude/agents/` 下定义了长期团队角色。主会话作为 **orchestrator** 对接用户；遇到具体任务派给对应 agent：

| 任务特征 | 派给谁 | 调用方式 |
|---|---|---|
| 摸清某个页面怎么走 / 知识库缺页面 | `aw-explorer` | SendMessage（长驻，探索需要积累上下文） |
| 截 UI 元素并注册常量 | `aw-element` | Agent()（子 Agent，每次干净上下文） |
| 编写业务层 / 用户方法 / pytest 用例 | `aw-codegen` | Agent()（子 Agent，每次干净上下文） |
| 跑 pytest / 诊断失败 / 图片转正 | `aw-verify` | Agent()（子 Agent，每次干净上下文） |

**调用方式说明**：`aw-codegen / aw-verify / aw-element` 通过 `Agent(subagent_type=...)` 每次新建实例执行，上下文干净、互不干扰。`aw-explorer` 通过 `SendMessage` 与长驻实例通信，支持多轮对话。（spec-keeper 已于 2026-10-12 随 openspec 流程移除而删除）orchestrator spawn 子 Agent 前须通过 G1-G5 派发门禁（见 `aw-orchestrator.md`），并通过 MCP 查询精确注入批次空间认知。

要一键拉起整个团队：`/bootstrap-team`。

## 并行测试执行

checklist 下 138 个用例可用 `run_parallel.py` 并行跑，缩短到约 1/3 耗时。

浏览器测试可通过 pytest-xdist 并行运行，每个 worker 使用独立浏览器会话。

账号配置通过环境变量注入：
```
TT_USERA_USERNAME / TT_USERA_PASSWORD
```
用例无需改动，仍写 `self.users("userA")`，框架按 INSTANCE_ID 自动映射。

**用法**：
```bash
python run_parallel.py                    # 3 实例全量
python run_parallel.py -n 2 -t 5          # 2 实例跑 5 个文件（验证用）
```

**串行模式不受影响**：不设 `INSTANCE_ID` 时 `_device_index` 默认 0，`_user_key_map` 为空，行为不变。

## 知识库系统（双层架构）

知识库采用 **Graph + Embedding** 双层架构，通过 MCP Server 暴露给所有 agent：

### Graph 层（knowledge_graph MCP）
- **数据源**：`knowledge/<project>/`（web/swan/android，Obsidian vault 格式，互相隔离）
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

- ❌ 绕过 AWBase 直接操作浏览器
- ❌ `tap(x, y)` 坐标点击
- ❌ accessibility key 做运行时定位/断言（定位用图像模板 > OCR 文本，不用 key）
- ❌ 截图与浏览器 viewport 尺寸不一致
- ❌ 截入动态元素（角标/时间/头像/在线状态）
- ❌ 新元素直接进 `image/<platform>/`（必须先进入对应的 `image_ai/<platform>/`）
- ❌ `try/except` 吞掉测试失败
- ❌ 只断言"没异常"
- ❌ 一个 py 文件里多个 test 方法（一用例一文件一 test 方法，规则 8 铁律）
- ❌ `@pytest.mark.parametrize`（参数装饰器禁用——变体各自独立成文件，规则 8 铁律）
- ❌ 修用例时自行改框架层（`conftest.py`/`run_parallel.py`/`driver/*`）— 须用户决策
- ❌ `click_image` 失败后加 `tap(x,y)` 坐标回退（必须修图片）

## 运行时经验（踩坑积累，所有 agent 必知）

| 场景 | 正确做法 |
|------|----------|
| 自动化登录账号 | **只用测试账号 13555555555**（OTP 白名单内，验证码接口可自动取码）；**18946151218 是一次性演示账号，禁止任何自动化登录/登出**（白名单不含，退出不可逆）——`.env.local` 的 `SWAN_PHONE` 必须指向 135 号（2026-10-12 曾配错为 189 致 agent 误用，用户手动救场） |
| **真机任务独占** | 同一台 adb 设备上**任何时刻只跑一个真机任务**（pytest 会话/agent 探索/补截图互斥）——并行必互相切 App 导致假失败（2026-10-12 实测：登录四件套与平台主页探索并行，设备被切进 QQ 音乐 5 条全废）。编排真机任务前先确认无其他 agent 占用设备 |
| 浏览器文本定位 | 优先使用 `click_text`（OCR），需要稳定定位时再补充 Web 元素选择器 |
| Python 多行命令 | 走 PowerShell 执行；避免 CodeMaker Hub 路径校验报错 |
| OCR `click_text` 偏上 | 筛选器标签/弹窗选项/底部栏按钮加 `dy=8~12`；列表条目无需加 |
| 图片匹配失败排查 | 灰度标准差>5、均值 5-250、无角标/阴影 → 图没问题再查代码 |

## 编码补充规则（原 .claude/rules/rules.mdc 并入，编码规范以本文件为唯一载体）

### 异常处理
- 默认让异常抛出；用 `if` / `assert` 做状态检查，不用异常控制流
- 仅允许 try-catch 的场景：ADB 外部命令、teardown 清理、资源释放
- 禁止：catch-all 吞异常、静默 `except: pass`、用 try-catch 掩盖测试失败

### 日志
- `logger = logging.getLogger(__name__)`；格式 `logger.info(f"✅ {operation} 成功")` / `logger.error(f"❌ {operation} 失败")`

### 过时 API（已不存在，不要参考）
~~ImageRecognition~~、~~OCRRecognition~~、~~MuMuActions~~、~~aw_find_by_image~~、~~aw_find_by_ocr~~、~~LOGIN_LOCATORS~~

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
