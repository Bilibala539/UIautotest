# agent-team 编排架构详细设计

> 本文档描述的是**当前实际运行**的 Claude Code Agent Teams 架构。
> 旧版文档（Python 状态机 `python -m agent_team` 命令行工具）已废弃，由此文档完整替换。
> 所有 Agent 定义在 `.claude/agents/` 目录下，由 Claude Code 原生 multi-agent 能力驱动。

---

## 一、架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        用 户（人）                               │
└─────────────────────────────┬───────────────────────────────────┘
                              │ 对话 / 指令
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   aw-orchestrator（主会话，永久）                  │
│  职责：意图理解 / 工作流选择 / 派发前门禁 / Git 存档点 / 经验沉淀    │
└──────┬────────────┬──────────────────┬───────────────┬──────────┘
       │ SendMessage│ SendMessage      │ Agent()       │ Agent()
       ▼            ▼                  ▼               ▼
┌────────────┐ ┌─────────────┐ ┌───────────────┐ ┌──────────────┐
│aw-explorer │ │ spec-keeper │ │  aw-element   │ │  aw-codegen  │
│（长驻）    │ │（长驻）     │ │ （子 Agent）  │ │ （子 Agent） │
└────────────┘ └─────────────┘ └───────────────┘ └──────────────┘
                                                        │
                                              生成代码后
                                                        ▼
                                              ┌──────────────┐
                                              │  aw-verify   │
                                              │ （子 Agent） │
                                              └──────────────┘
```

**双层知识库（所有 Agent 共享）**

```
┌───────────────────────────────────────────────────────┐
│  Graph 层（knowledge_graph MCP）                       │
│  app_map.json + pages/*.md                            │
│  能力：页面搜索 / 导航路径 / 反向链接                   │
├───────────────────────────────────────────────────────┤
│  Embedding 层（vector_kb MCP）                         │
│  pages/*.md + tests/*.py + docs/*.md → ChromaDB       │
│  能力：语义搜索 / 相似用例推荐 / 综合上下文注入          │
└───────────────────────────────────────────────────────┘
```

---

## 二、Agent 角色与生命周期

### 2.1 生命周期对照表

| Agent | 文件 | 生命周期 | 调用方式 | 设计原因 |
|---|---|---|---|---|
| aw-orchestrator | `.claude/agents/aw-orchestrator.md` | 主会话（永久） | 用户直接对话 | 需要持有全局状态、历史上下文 |
| aw-explorer | `.claude/agents/aw-explorer.md` | 长驻 | `SendMessage` | 探索需要跨页面积累上下文，不能每次重置 |
| aw-element | `.claude/agents/aw-element.md` | 子 Agent | `Agent()` | 截图操作无状态，每次任务独立执行 |
| aw-codegen | `.claude/agents/aw-codegen.md` | 子 Agent | `Agent()` | 代码生成需要干净上下文，避免前次代码污染 |
| aw-verify | `.claude/agents/aw-verify.md` | 子 Agent | `Agent()` | pytest 输出量大，不应污染后续对话 |
| spec-keeper | `.claude/agents/spec-keeper.md` | 长驻 | `SendMessage` | 仅在走 openspec 流程时启用，需保留提案历史 |

### 2.2 长驻 vs 子 Agent 的选择原则

**长驻 Agent（SendMessage）**：适合需要"记住"跨轮次信息的角色。explorer 在探索第二个页面时需要知道第一个页面探索了什么；spec-keeper 在归档提案时需要知道整个提案生命周期。

**子 Agent（Agent() spawn）**：适合无状态的一次性任务。截图只需要目标页面路径；代码生成只需要当次任务描述 + 注入的知识片段；验证只需要测试文件路径。每次 spawn 拿到干净上下文，不受前次执行结果干扰。

---

## 三、三种工作流模式

### 3.1 convert-cases（文字用例 → 自动化脚本）

这是最常用的主流程：将人工编写的文字测试用例自动转化为可运行的 pytest 脚本。

```
用户提供文字用例
        │
        ▼
orchestrator 解析意图，执行派发前门禁 G1-G5
        │
        ├── G1 未过 → SendMessage aw-explorer 探索目标页面
        │               └── 更新知识库后回到门禁重新检查
        │
        ├── G2 未过 → Agent() spawn aw-element 截取缺失元素
        │               └── 注册常量后回到门禁重新检查
        │
        ▼（所有门禁通过）
orchestrator 执行 Git checkpoint（pre-codegen）
        │
        ▼
Agent() spawn aw-codegen（注入批次空间认知）
        │   输出：AW 方法 + PPUser 代理 + pytest 用例文件
        ▼
Agent() spawn aw-verify
        │
        ├── 通过 → 图片转正 image_ai/ → image/
        │          Git commit "feat: [功能]"
        │          orchestrator 提取经验 → runtime_experience.md
        │
        └── 失败 → 按根因路由
                    ├── 图片问题  → 重新 spawn aw-element → 再次 verify
                    ├── 代码问题  → 重新 spawn aw-codegen → 再次 verify
                    └── 3 次失败 → git reset --hard HEAD，报告用户
```

**步骤细节**：

| 步骤 | 执行者 | 可跳过条件 |
|---|---|---|
| Step 1：解析结构化步骤 | spec-keeper（可选） | 文字用例已足够清晰时，orchestrator 直接处理 |
| Step 2：确认页面路径 | aw-explorer | 目标页面已在知识库（G1 通过）|
| Step 3：截取 UI 元素 | aw-element | 所需图片常量已注册（G2 通过）|
| Step 4：生成代码 | aw-codegen（子 Agent）| 不可跳过 |
| Step 5：验证 | aw-verify（子 Agent）| 不可跳过 |

---

### 3.2 enrich-kb（丰富知识库）

专门用于补充、更新、维护 App 知识库，不产出测试代码。

```
用户指令：探索某页面 / 更新某功能文档 / 知识库巡检
        │
        ▼
orchestrator 路由到以下子模式之一：

  new-page    → SendMessage aw-explorer 探索新页面
               └── 写入 draft/*.md → promote_knowledge.py 验证 → 进 pages/

  update-page → SendMessage aw-explorer 重新探索已有页面
               └── 更新 pages/*.md，触发 embedding 增量更新

  add-feature → SendMessage aw-explorer 针对特定功能点补充文档
               └── 补充现有页面的功能描述

  audit-kb    → aw-verify 执行知识库健康度检查
               └── 检查孤立页面、失效链接、过期截图描述
```

该模式不涉及 aw-codegen，只用 explorer + verify 两个角色。

---

### 3.3 fix-batch（批量修复失败用例）

专门处理 CI/本地跑出来的一批失败用例，按失败聚类批量修复。

```
Phase 0：读取失败日志
  │  从 session.json / pytest output 提取所有失败用例
  │  提取每条失败的 traceback、AW 方法调用栈
  │
  ▼
Phase 0.5：共性根因分析
  │  从 traceback 提取 AW 方法名 → 按方法分组
  │  同一 AW 方法 ≥2 个用例失败 → 疑似共性故障
  │  二次验证：比对异常消息 + 栈帧行号（±3 行）
  │  交叉比对 PASS 用例，排除测试数据差异误判
  │  输出优先级队列：共性故障组优先，单点故障后处理
  │
  ▼
Phase 1：按优先级逐组修复（对每个故障组循环）
  │
  ├── aw-verify spawn → 诊断具体失败原因
  │       │
  │       ├── 图片质量问题    → spawn aw-element 重新截图
  │       ├── AW 逻辑问题    → spawn aw-codegen 修复 AW 方法
  │       ├── 用例代码问题   → spawn aw-codegen 修复用例
  │       └── 环境/设备问题  → 人工介入，跳过本组
  │
  ├── aw-verify spawn → 重新跑修复后的用例验证（最多 3 轮）
  │       ├── 通过 → 标记修复，进行 Git commit
  │       └── 失败 → 继续下一轮修复迭代
  │
  └──（所有组处理完毕）
  │
  ▼
Phase 2：汇总报告
  修复成功 N 条，跳过 M 条，仍失败 K 条
  输出每条失败的根因分类和建议
```

**共性分析的价值**：一个 AW 方法被修复后，所有依赖它的用例可以一次性全部修复，而不是逐条排查相同的错误。

**AW 方法基线回归验证**（修改 `mumu.py` 时触发）：

```
git stash
  → 跑受影响用例，记录基线通过数
git stash pop
  → 跑修复后版本，记录新通过数
如果"搞坏数 > 修好数" → git revert 修改，报告用户
```

---

## 四、派发前门禁 G1-G5

在 orchestrator 向 aw-codegen spawn 子 Agent 之前，必须逐项通过以下门禁检查。这些检查防止 codegen 拿到不完整的上下文，避免产出无法运行的代码。

| # | 检查项 | 验证方式 | 不通过时的处置 |
|---|---|---|---|
| G1 | 目标页面已在知识库中 | `knowledge_graph.search_pages(页面名)` 有结果 | 先派 aw-explorer 探索页面，完成后重新检查 |
| G2 | 目标 UI 元素图片已注册常量 | `image_name_mapping.py` 中存在对应常量 | 先派 aw-element 截取元素，完成后重新检查 |
| G3 | test 方法末尾有清理调用 | 检查用例文字描述中包含还原步骤 | 在任务描述中补充清理步骤后再 spawn |
| G4 | 清理后能回到消息首页 | 评估清理路径的可达性 | 补充清理步骤后再 spawn |
| G5 | 同功能变体是否应合并 parametrize | 检查是否存在仅参数不同的同类用例 | 提示合并建议，**不阻断**派发（开发者自决）|

**为什么要有门禁**：子 Agent 的上下文是独立的，它在 spawn 时"看不到"主会话的历史。如果元素图片未注册，codegen 生成的代码引用了不存在的常量，verify 必然失败，造成不必要的重试往返。门禁将问题前置，减少无效轮次。

---

## 五、批次空间认知注入

子 Agent（aw-codegen、aw-element、aw-verify）在 spawn 时，orchestrator 会构建一个包含相关知识片段的 prompt，而不是把全量知识库塞进去。

### 5.1 Prompt 结构

```
┌─────────────────────────────────────────────────────────┐
│ 批次空间认知（MCP 查询结果）                              │
│                                                         │
│  ① get_related_pages("目标页面")                        │
│     → 目标页面文档 + 邻接页面 + 反向引用该页面的其他页面  │
│                                                         │
│  ② get_navigation_path("消息首页", "目标页面")           │
│     → 从起点到目标页的 BFS 最短路径（操作步骤）           │
│                                                         │
│  ③ find_similar_tests("用例描述")                       │
│     → 已有的相似测试用例（避免重复，提供代码参考）        │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ 已知经验（语义检索）                                      │
│                                                         │
│  ④ semantic_search("用例描述", source_type="docs")       │
│     → docs/runtime_experience.md 中的相关踩坑记录        │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ 任务描述                                                  │
│  具体用例文字 / AW 方法需求 / 截图目标                    │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ 完成标准                                                  │
│  子 Agent 输出确认令牌 + 预期产出格式                     │
└─────────────────────────────────────────────────────────┘
```

### 5.2 子 Agent 确认令牌

子 Agent 必须在读完规定文件（CLAUDE.md、AW复用指南、元素常量）后输出：

```
阶段0完成：已读 CLAUDE.md / AW复用指南 / 元素常量
```

orchestrator 在接收到子 Agent 的回复后，验证令牌是否存在。若缺失，说明子 Agent 跳过了必读步骤，orchestrator 将重新 spawn 一次（最多重试 1 次）。

**设计原因**：子 Agent 每次 spawn 都是全新上下文，没有强制机制保证它读了规定文件。令牌是一个轻量级的契约，让 orchestrator 可以机械地验证前置条件。

### 5.3 知识注入而非全量推送

全量知识库可能包含数十个页面文档和数百个测试用例，全部推入子 Agent 会：
- 消耗大量 token，增加延迟和成本
- 无关信息干扰生成质量

通过 MCP 查询精准注入相关片段，子 Agent 拿到的是"恰好需要的"上下文。

---

## 六、fix-batch 失败修复流程详解

### 6.1 Phase 0.5 共性分析算法

```
输入：N 条失败用例的 traceback

Step 1：提取 AW 方法调用
  解析每条 traceback，提取 utils/aw/business/mumu.py 中的方法名
  每条失败 → [method_A, method_B, ...]

Step 2：频率分组
  统计每个 AW 方法被多少条失败涉及
  ≥ 2 条涉及同一方法 → 候选共性故障

Step 3：二次验证（排除误判）
  对候选组：比对异常消息相似度 + 栈帧行号（±3 行内）
  若行号和异常一致 → 确认为共性故障
  若行号不同但异常相同 → 可能是同类逻辑问题，标记为"疑似"

Step 4：交叉比对 PASS 用例
  PASS 用例如果也调用了相同 AW 方法 → 说明方法本身没问题
  → 降级为单点故障（数据/环境差异）

Step 5：输出优先级队列
  [共性故障组1（影响 5 个用例）,
   共性故障组2（影响 3 个用例）,
   单点故障1, 单点故障2, ...]
```

### 6.2 修复路由规则

```
失败原因                          路由到
──────────────────────────────────────────────────
image_exists / click_image 失败   → aw-element 重新截图
ImportError / AttributeError      → aw-codegen 修复代码
AssertionError（业务逻辑失败）    → aw-codegen 修复用例
ADB 连接错误 / 设备超时           → 人工介入（跳过）
无法识别的错误                    → aw-codegen（默认）
```

### 6.3 修复轮次控制

每个故障组最多执行 3 轮修复迭代：

```
轮次1：按初始根因路由修复 → verify
轮次2：根据 verify 输出调整策略 → 再次修复 → verify
轮次3：最后一次尝试 → verify
失败：标记为"需人工介入"，记录诊断报告，跳过本组
```

---

## 七、知识库双层架构与更新机制

### 7.1 两层能力对比

| 维度 | Graph 层 | Embedding 层 |
|---|---|---|
| MCP Server | `knowledge_graph` | `vector_kb` |
| 数据源 | `explorer_output/knowledge/` | pages/ + tests/ + docs/ |
| 存储格式 | Markdown + JSON 索引 | ChromaDB 向量数据库 |
| 查询方式 | 精确匹配 / BFS 图遍历 | 语义相似度搜索 |
| 适用场景 | 导航路径、页面结构、反向链接 | 相似用例、概念检索、综合上下文 |
| 更新触发 | git post-commit hook | git post-commit hook（增量）|

### 7.2 知识更新流程

```
aw-explorer 探索新页面
        │
        ▼ 写入
explorer_output/knowledge/draft/*.md （草稿区）
        │
        ▼ 执行
python scripts/knowledge/promote_knowledge.py
  ├── 验证：结构完整性（必须包含规定字段）
  ├── 验证：[[双向链接]] 有效性（引用的 page_id 必须存在）
  └── 验证通过 → 移入 pages/ + 更新 app_map.json
        │
        ▼ git commit
post-commit hook 触发 auto_update.py
        │
        ├── backlinks_generator.py  → 重建反向链接索引
        └── embedding_pipeline.py --incremental → 增量更新向量索引
```

### 7.3 手动维护脚本

```bash
# 重建反向链接（pages/ 中链接关系变更后）
python scripts/knowledge/backlinks_generator.py

# 全量重建向量索引（首次初始化或索引损坏时）
python scripts/knowledge/embedding_pipeline.py

# 增量更新向量索引（日常 git commit 后自动触发，也可手动）
python scripts/knowledge/embedding_pipeline.py --incremental

# 验证并转正草稿
python scripts/knowledge/promote_knowledge.py

# 强制全量更新（反链 + embedding）
python scripts/knowledge/auto_update.py --force
```

### 7.4 Agent 查询惯例

| 查询目的 | 调用方式 |
|---|---|
| 写新用例前获取完整上下文 | `find_related_context("功能描述")` |
| 找从消息首页到目标页的操作路径 | `get_navigation_path("起点page_id", "目标page_id")` |
| 查找哪些页面引用了当前页 | `get_backlinks("page_id")` |
| 自然语言模糊搜索页面 | `semantic_search("描述")` |
| 找相似已有测试用例 | `find_similar_tests("用例描述")` |

---

## 八、Git 存档点协议

在 codegen/verify 流程中，orchestrator 维护严格的 Git 检查点，确保任何失败都可以安全回滚。

### 8.1 存档点时机

| 时机 | Git 操作 | Commit 消息格式 |
|---|---|---|
| spawn aw-codegen 前 | `git commit` | `checkpoint: pre-codegen [任务描述]` |
| aw-verify 全部通过后 | `git commit` | `feat: [功能描述]` |
| aw-verify 失败，需重试 | `git reset --hard HEAD` | （无 commit）|
| 连续 3 次验证失败 | `git reset --hard HEAD` | （无 commit，报告用户）|

### 8.2 存档点流程图

```
orchestrator 决定 spawn codegen
        │
        ▼
git commit "checkpoint: pre-codegen [任务]"
        │
        ▼
spawn aw-codegen → 产出代码文件
        │
        ▼
spawn aw-verify
        │
        ├── 第1轮 PASS → git commit "feat: [功能]" → 结束
        │
        ├── 第1轮 FAIL → 按根因路由修复
        │       ▼
        │   spawn aw-codegen/element（修复）
        │       ▼
        │   spawn aw-verify（第2轮）
        │       ├── PASS → git commit "feat: [功能]" → 结束
        │       └── FAIL → 继续修复
        │               ▼
        │           spawn aw-codegen/element（再次修复）
        │               ▼
        │           spawn aw-verify（第3轮）
        │               ├── PASS → git commit "feat: [功能]" → 结束
        │               └── FAIL → git reset --hard HEAD
        │                         → 报告用户，人工介入
        └──────────────────────────────────────────────────
```

**为什么在 codegen 前打 checkpoint 而不是 verify 前**：codegen 可能修改 mumu.py、user.py 等共用文件。如果 verify 失败需要 reset，只 reset 到 codegen 前的状态是安全的——既能撤销本次产出，又不会影响之前已验证通过的内容。

---

## 九、经验沉淀机制

每次 aw-verify 通过后，orchestrator 将本次执行中发现的新经验追加到 `docs/runtime_experience.md`。

### 9.1 哪些内容值得沉淀

- 元素定位的特殊技巧（如某类开关不能用图片匹配，需要坐标范围）
- 特定页面的导航陷阱（如某页面有两个同名按钮，需要区分上下文）
- AW 方法的已知局限（如某操作在网络慢时需要增加等待）
- 元素图片的截取注意事项

### 9.2 经验如何被后续任务使用

```
runtime_experience.md
        │
        ▼（auto_update.py 增量更新）
ChromaDB 向量索引
        │
        ▼（批次空间认知注入）
semantic_search("用例描述", source_type="docs")
        │
        ▼
注入子 Agent 的 prompt，作为"已知经验"片段
```

经验沉淀形成正反馈：处理过的场景越多，后续类似场景的一次通过率越高。

---

## 十、与旧蓝图的对比说明

| 维度 | 旧蓝图（Python 状态机）| 当前架构（Claude Code Agent Teams）|
|---|---|---|
| 运行方式 | `python -m agent_team "任务"` | 主会话对话驱动 |
| Agent 通信 | 共享 TeamContext dataclass | SendMessage / Agent() spawn |
| 状态管理 | 代码对象持有 | 主会话上下文 + 知识库 |
| 重试控制 | Orchestrator while 循环 | orchestrator 手动判断后重新 spawn |
| 知识存储 | 内存 TeamContext | 双层知识库（Graph + Embedding）|
| 实现状态 | **未实现（蓝图）** | **已实现并实际运行** |

旧蓝图的 Python 状态机思路是可行的工程化方向，但当前 Claude Code 的 Agent Teams 原生能力已经满足实际需求，无需额外的 Python 框架层。如未来需要更高程度的自动化（如 CI 触发无人值守运行），可参考旧蓝图思路补充代码层。

---

## 附录 A：Agent 文件索引

| 文件 | 角色 | 生命周期 |
|---|---|---|
| `.claude/agents/aw-orchestrator.md` | 总编排、意图理解、门禁 | 主会话永久 |
| `.claude/agents/aw-explorer.md` | App 页面探索、知识库写入 | 长驻 |
| `.claude/agents/aw-element.md` | UI 元素截图、常量注册 | 子 Agent |
| `.claude/agents/aw-codegen.md` | AW 方法 + 用例代码生成 | 子 Agent |
| `.claude/agents/aw-verify.md` | pytest 执行、失败诊断、图片转正 | 子 Agent |
| `.claude/agents/spec-keeper.md` | openspec 提案管理 | 长驻 |

## 附录 B：相关文档索引

| 文件 | 内容 |
|---|---|
| `CLAUDE.md` | 项目约定总纲，所有 Agent 必读 |
| `docs/AW方法总结与复用指南.md` | 已封装 AW 方法清单，写代码前必查 |
| `docs/UI元素截取与裁剪规范.md` | 元素截图规范，aw-element 执行依据 |
| `docs/并行测试执行指南.md` | 多实例并行跑测试的机器配置指南 |
| `docs/runtime_experience.md` | 运行时踩坑经验积累（可能不存在则由首次沉淀创建）|
| `explorer_output/knowledge/pages/` | App 页面知识文档 |
| `explorer_output/knowledge/app_map.json` | 页面关系图谱索引 |
| `openspec/changes/agent-team/` | 旧工程化蓝图提案（已暂停，保留供参考）|
