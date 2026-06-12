# 编排融合实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 ui-ai-v5 的三项编排优势融合进 UIAutotest：aw-codegen/verify/element 改为子 Agent、fix-batch 加入共性根因分析、上下文注入改为精确过滤。

**Architecture:** 混合生命周期模式——aw-explorer/spec-keeper 保持长驻 SendMessage，aw-codegen/aw-verify/aw-element 改为通过 Agent() 每次干净上下文 spawn；orchestrator 在 spawn 前做 G1-G5 自检和 MCP 精准知识注入；fix-batch 新增 Phase 0.5 共性聚类，修公共 AW 方法时做基线回归对比。

**Tech Stack:** Claude Code Agent 系统（`.claude/agents/`）、Agent() 工具、SendMessage 工具、knowledge_graph MCP、vector_kb MCP

---

## 文件变更清单

| 文件 | 操作 | 改动内容 |
|---|---|---|
| `.claude/commands/fix-batch.md` | 修改 | 插入 Phase 0.5（共性分析）+ AW 方法基线回归验证 |
| `.claude/agents/aw-orchestrator.md` | 修改 | codegen/verify/element 调用改 Agent()，加 G1-G5 自检，加批次空间认知注入 |
| `.claude/agents/aw-codegen.md` | 修改 | 移除 SendMessage，加阶段0确认令牌，进度汇报改为文本输出 |
| `.claude/agents/aw-verify.md` | 修改 | 移除 SendMessage，加阶段0确认令牌，进度汇报改为文本输出 |
| `.claude/agents/aw-element.md` | 修改 | 移除 SendMessage，加阶段0确认令牌，进度汇报改为文本输出 |
| `docs/runtime_experience.md` | 新建 | 运行时经验知识库文件，纳入 embedding pipeline |

---

## Phase 1：fix-batch 增强

### Task 1：fix-batch.md — 插入 Phase 0.5 共性根因分析

**Files:**
- Modify: `.claude/commands/fix-batch.md`

- [ ] **Step 1：在 fix-batch.md 的「Phase 0」和「Phase 1」之间插入以下内容**

在 `## Phase 1: 逐个修复` 标题之前插入：

```markdown
---

## Phase 0.5: 共性根因分析（orchestrator 自行完成，不派 agent）

> **目的**：修之前先找共性，同一 AW 方法导致多个失败时一次修好全部，不逐个修。

### Step 1：提取 AW 方法

从每个失败用例的 traceback 中提取最后调用的 `utils/aw/business/mumu.py` 方法：

```
示例 traceback：
  tests/checklist/test_session_box.py:42 in test_open_session_box
  utils/aw/business/mumu.py:885 in click_session_box    ← 提取这行
```

### Step 2：按方法分组

```
click_session_box → test_open_session_box, test_close_session_box, test_batch_session（3个）← 疑似共性
enter_group_settings → test_group_name, test_group_announcement（2个）← 疑似共性
tap_send_btn → test_send_image（1个）← 独立，不是共性
```

### Step 3：二次验证（防误归类）

方法名相同 ≠ 同一根因。以下 **2 项均一致** 才确认为共性：

| 验证项 | 比对方式 | 一致判定 |
|--------|---------|---------|
| 异常消息核心内容 | 提取 error message 中的元素名/图片名/OCR文字 | 指向同一个元素或图片 |
| 失败栈帧行号 | mumu.py 内部失败的行号 | 同一行或 ±3 行以内 |

### Step 4：交叉比对通过用例

对每个疑似共性方法，检查是否有 PASS 用例也调用了它：

```bash
grep -rl "click_session_box" E:/UIAutotest/tests/
```

| 比对结果 | 修复方向 |
|---------|---------|
| 有 PASS 用例调用同方法且成功 | 方法本身没问题，对比成功 vs 失败用例的调用差异（参数/前置页面/传入值） |
| 所有调用该方法的用例全部失败 | 方法本身有 bug，直接修方法 |
| 没有 PASS 用例调用该方法 | 走通用诊断（Step 1） |

### Step 5：输出修复优先级队列

在原有 C1-C6 聚类基础上，共性问题排最前：

```markdown
## 修复计划（含共性分析结果）

| 优先级 | 类型 | 根因 | 影响用例数 | 修复方向 |
|--------|------|------|-----------|---------|
| P0-共性 | 共性 AW 方法 | click_session_box 元素定位失败 | 3 | 直接修方法 |
| P1-共性 | 共性 AW 方法 | enter_group_settings 匹配逻辑 | 2 | 对比成功用例调用差异 |
| P2-独立 | C4-操作逻辑 | test_send_image 各自不同 | 1 | 逐个分析 |
```

**每轮 fix（aw-verify 修复后重跑 pytest）后，重新执行 Phase 0.5**——剩余失败的共性模式可能变了，不能沿用上轮分析结论。
```

- [ ] **Step 2：验证插入位置正确**

```bash
grep -n "Phase 0.5\|Phase 1\|Phase 2" E:/UIAutotest/.claude/commands/fix-batch.md
```

期望输出中 `Phase 0.5` 行号在 `Phase 1` 之前。

- [ ] **Step 3：Commit**

```bash
git add .claude/commands/fix-batch.md
git commit -m "feat: fix-batch 加入 Phase 0.5 共性根因分析"
```

---

### Task 2：fix-batch.md — 加入 AW 方法基线回归验证

**Files:**
- Modify: `.claude/commands/fix-batch.md`

- [ ] **Step 1：在 Phase 1 的「验证与推进」部分，「通过」分支后插入基线回归验证逻辑**

找到以下内容：

```markdown
- **通过** → `git commit -m "fix: [用例名] [根因简述]"`
  - 然后检查同组其他用例（附带修复检查）
```

替换为：

```markdown
- **通过** → 先检查是否修改了公共 AW 方法，再决定是否做基线回归：

  **如果本轮 aw-verify 修改了 `utils/aw/business/mumu.py`**，在 commit 前执行基线回归：

  ```bash
  # 1. 找出依赖被修改方法的测试文件
  CHANGED_METHOD=$(git diff HEAD utils/aw/business/mumu.py | grep "^+def \|^-def " | awk '{print $2}' | tr -d '(:')
  AFFECTED=$(grep -rl "$CHANGED_METHOD" E:/UIAutotest/tests/ 2>/dev/null | grep "\.py$")

  # 2. 若有受影响文件，暂存修改，跑基线
  git stash
  for f in $AFFECTED; do
    pytest "$f" -v --tb=line 2>&1 | grep -E "PASSED|FAILED" >> /tmp/uiat_baseline.txt
  done

  # 3. 恢复修改，跑修复后版本
  git stash pop
  for f in $AFFECTED; do
    pytest "$f" -v --tb=line 2>&1 | grep -E "PASSED|FAILED" >> /tmp/uiat_after.txt
  done
  ```

  对比结果：
  | 变化 | 含义 | 动作 |
  |------|------|------|
  | baseline PASS → after FAIL | 真实回归 | `git checkout -- .`，本次修复放弃，记录后交人工 |
  | baseline FAIL → after PASS | 附带修好 | 保留，一并 commit |
  | 搞坏数 > 修好数 | 净负回归 | `git checkout -- .`，放弃，交人工 |
  | 无真实回归 | 安全 | 继续 commit |

  **如果未修改 mumu.py**，直接 commit：

  ```bash
  git commit -m "fix: [用例名] [根因简述]"
  ```
```

- [ ] **Step 2：验证修改**

```bash
grep -n "基线回归\|uiat_baseline\|净负回归" E:/UIAutotest/.claude/commands/fix-batch.md
```

期望：3 行匹配。

- [ ] **Step 3：Commit**

```bash
git add .claude/commands/fix-batch.md
git commit -m "feat: fix-batch 加入 AW 方法基线回归验证"
```

---

## Phase 2：子 Agent 架构改造

### Task 3：aw-codegen.md — 移除 SendMessage，加确认令牌

**Files:**
- Modify: `.claude/agents/aw-codegen.md`

- [ ] **Step 1：tools 列表中移除 SendMessage**

找到：
```yaml
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - SendMessage
  - TaskUpdate
```

替换为：
```yaml
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - TaskUpdate
```

- [ ] **Step 2：「必读（每次开工）」后加阶段0确认令牌要求**

找到：
```markdown
### 必读（每次开工）
- `CLAUDE.md` —— 项目规约 + 运行时经验（含坐标规律、禁止事项）
```

替换为：
```markdown
### 必读（每次开工）
- `CLAUDE.md` —— 项目规约 + 运行时经验（含坐标规律、禁止事项）

> ⛔ **阶段0确认令牌**：读完 CLAUDE.md 和 `docs/AW方法总结与复用指南.md` 后，必须输出以下确认语（一字不改），之后才能执行任何写文件操作：
> ```
> 阶段0完成：已读 CLAUDE.md / AW复用指南 / 元素常量
> ```
```

- [ ] **Step 3：将「📡 中间进度汇报」改为文本输出说明**

找到：
```markdown
## 📡 中间进度汇报（关键节点必须主动发）
```

将该 section 标题和表格内容替换为：
```markdown
## 📡 中间进度输出（关键节点必须输出到正文）

> 作为子 Agent 运行时无法 SendMessage，进度通过正文输出体现。

| 节点 | 输出内容 |
|------|----------|
| 自检通过后 | `[进度] 自检通过（无功能重复），开始写代码` |
| 主要 AW 方法写完后 | `[进度] AW 方法已写入 mumu.py，开始写 pytest 用例` |
| 自检发现问题 | `[自检失败] <原因>` |
| 遇到无法继续的障碍 | `[阻塞] <描述>` |
```

- [ ] **Step 4：验证**

```bash
grep -n "SendMessage\|阶段0完成\|子 Agent" E:/UIAutotest/.claude/agents/aw-codegen.md
```

期望：`SendMessage` 只在「禁止事项」说明中出现（若有）；`阶段0完成` 出现 1 次；`子 Agent` 出现 1 次。

- [ ] **Step 5：Commit**

```bash
git add .claude/agents/aw-codegen.md
git commit -m "feat: aw-codegen 改为子 Agent 模式，加阶段0确认令牌"
```

---

### Task 4：aw-verify.md — 移除 SendMessage，加确认令牌

**Files:**
- Modify: `.claude/agents/aw-verify.md`

- [ ] **Step 1：tools 列表中移除 SendMessage**

找到：
```yaml
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - SendMessage
  - TaskUpdate
  - Skill
```

替换为：
```yaml
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - TaskUpdate
  - Skill
```

- [ ] **Step 2：「必读（每次开工）」后加确认令牌要求**

找到：
```markdown
### 必读（每次开工）
- `CLAUDE.md` —— 项目规约 + 运行时经验
- `conftest.py` —— fixture 和 device 初始化
- `pytest.ini` —— 测试配置
```

替换为：
```markdown
### 必读（每次开工）
- `CLAUDE.md` —— 项目规约 + 运行时经验
- `conftest.py` —— fixture 和 device 初始化
- `pytest.ini` —— 测试配置

> ⛔ **阶段0确认令牌**：读完以上三个文件后，必须输出以下确认语（一字不改），之后才能执行任何 pytest 命令：
> ```
> 阶段0完成：已读 CLAUDE.md / conftest / pytest.ini
> ```
```

- [ ] **Step 3：将「📡 中间进度汇报」改为文本输出说明**

找到：
```markdown
## 📡 中间进度汇报（关键节点必须主动发）
```

将该 section 标题替换为：
```markdown
## 📡 中间进度输出（关键节点必须输出到正文）

> 作为子 Agent 运行时无法 SendMessage，进度通过正文输出体现。
```

- [ ] **Step 4：验证**

```bash
grep -n "SendMessage\|阶段0完成\|子 Agent" E:/UIAutotest/.claude/agents/aw-verify.md
```

期望：`SendMessage` 在 tools 列表中不再出现；`阶段0完成` 出现 1 次。

- [ ] **Step 5：Commit**

```bash
git add .claude/agents/aw-verify.md
git commit -m "feat: aw-verify 改为子 Agent 模式，加阶段0确认令牌"
```

---

### Task 5：aw-element.md — 移除 SendMessage，加确认令牌

**Files:**
- Modify: `.claude/agents/aw-element.md`

- [ ] **Step 1：tools 列表中移除 SendMessage**

找到：
```yaml
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - SendMessage
  - TaskUpdate
```

替换为：
```yaml
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - TaskUpdate
```

- [ ] **Step 2：「必读（每次开工）」后加确认令牌要求**

找到：
```markdown
### 必读（每次开工）
- `CLAUDE.md` —— 项目规约 + 运行时经验（含截图规范要点）
- `image/image_name_mapping.py` —— 已有常量命名，避免撞名
```

替换为：
```markdown
### 必读（每次开工）
- `CLAUDE.md` —— 项目规约 + 运行时经验（含截图规范要点）
- `image/image_name_mapping.py` —— 已有常量命名，避免撞名

> ⛔ **阶段0确认令牌**：读完以上两个文件后，必须输出以下确认语（一字不改），之后才能截图或写文件：
> ```
> 阶段0完成：已读 CLAUDE.md / AW复用指南 / 元素常量
> ```
```

- [ ] **Step 3：将「📡 中间进度汇报」改为文本输出说明**

找到：
```markdown
## 📡 中间进度汇报（关键节点必须主动发）
```

将该 section 标题替换为：
```markdown
## 📡 中间进度输出（关键节点必须输出到正文）

> 作为子 Agent 运行时无法 SendMessage，进度通过正文输出体现。
```

- [ ] **Step 4：验证**

```bash
grep -n "SendMessage\|阶段0完成" E:/UIAutotest/.claude/agents/aw-element.md
```

期望：`SendMessage` 在 tools 列表中不再出现；`阶段0完成` 出现 1 次。

- [ ] **Step 5：Commit**

```bash
git add .claude/agents/aw-element.md
git commit -m "feat: aw-element 改为子 Agent 模式，加阶段0确认令牌"
```

---

### Task 6：aw-orchestrator.md — 工作流模板改为 Agent() 调用

**Files:**
- Modify: `.claude/agents/aw-orchestrator.md`

- [ ] **Step 1：更新「工作流模板」section**

找到：
```markdown
## 工作流模板

```
收到需求
  ├─ TaskCreate 建总任务
  ├─ 判断流程切入点（从哪一阶段开始）
  ├─ for each 阶段:
  │    SendMessage 派下游 agent
  │    等完成 / 检查产物
  │    TaskUpdate 标记完成
  ├─ 全部完成后汇总为 Markdown 交付
  └─ 异常时给用户清晰的诊断，不要静默重试超过 3 次
```
```

替换为：
```markdown
## 工作流模板

```
收到需求
  ├─ TaskCreate 建总任务
  ├─ 判断流程切入点（从哪一阶段开始）
  ├─ for each 阶段:
  │    if agent in [aw-explorer, spec-keeper]:
  │      SendMessage 派长驻 agent（可双向通信，支持中途问答）
  │    else [aw-codegen, aw-verify, aw-element]:
  │      → G1-G5 自检（见下方「派发前门禁」）
  │      → MCP 批次空间认知查询（见下方「知识注入」）
  │      → Agent(subagent_type=..., prompt=自包含任务描述)
  │      → 检查返回内容是否含「阶段0完成」确认语
  │        ├─ 有 → 读取 [完成]/[失败] 结果
  │        └─ 无 → 重新 spawn（最多 1 次重试）
  │    TaskUpdate 标记完成
  ├─ 全部完成后汇总为 Markdown 交付
  └─ 异常时给用户清晰的诊断，不要静默重试超过 3 次
```

---

## 派发前门禁（spawn aw-codegen 前必须通过）

spawn aw-codegen 子 Agent 之前，orchestrator 逐项检查：

| # | 检查项 | 验证方式 | 不过后果 |
|---|--------|---------|---------|
| G1 | 涉及的页面已在知识库中 | `mcp__knowledge_graph__list_pages()` 结果中有目标 page_id | ❌ 先派 aw-explorer |
| G2 | 涉及的元素图片已注册 | `grep "目标元素关键词" E:/UIAutotest/image/image_name_mapping.py` | ❌ 先派 aw-element |
| G3 | test 方法末尾有对应清理调用 | 确认任务描述中有清理步骤（如 `dissolve_group()`、`recall_message()`） | ❌ 补充后再 spawn |
| G4 | 清理后能回到消息首页 | 确认任务描述末尾有回首页操作 | ❌ 补充后再 spawn |
| G5 | 同功能参数变体是否合并 parametrize | 检查是否多个相似用例描述 | ⚠️ 提示合并，不阻断 |

---

## 知识注入（spawn aw-codegen/aw-verify/aw-element 前执行）

```python
# orchestrator 在构建子 Agent prompt 前执行
related_pages  = mcp__knowledge_graph__get_related_pages("目标 page_id")
nav_path       = mcp__knowledge_graph__get_navigation_path("消息列表页", "目标页面")
similar_tests  = mcp__vector_kb__find_similar_tests("当前用例功能描述")
experience     = mcp__vector_kb__semantic_search(
                     query="当前用例功能描述",
                     source_type="docs"      # 检索 docs/runtime_experience.md
                 )

# 只注入与当前任务相关的片段，全量知识库不进子 Agent
```

子 Agent prompt 结构模板：

```
你是 UIAutotest 的[角色]。以下信息自包含，无需额外加载其他上下文。

## 批次空间认知
{related_pages 查询结果}
{nav_path 查询结果}

## 相似用例参考
{similar_tests 查询结果}

## 已知经验
{experience 查询结果}

## 任务
{具体任务描述}

完成标准：{具体标准}

⛔ 在输出「阶段0完成：已读 CLAUDE.md / ...」确认语之前，禁止执行任何写文件或 pytest 操作。
```
```

- [ ] **Step 2：验证关键内容存在**

```bash
grep -n "G1\|G2\|G3\|G4\|G5\|批次空间认知\|阶段0完成\|subagent_type\|派发前门禁" E:/UIAutotest/.claude/agents/aw-orchestrator.md | head -20
```

期望：G1-G5 均存在，`批次空间认知`、`阶段0完成`、`派发前门禁` 各出现 ≥1 次。

- [ ] **Step 3：Commit**

```bash
git add .claude/agents/aw-orchestrator.md
git commit -m "feat: orchestrator 改用 Agent() spawn 子实例，加 G1-G5 门禁和知识注入"
```

---

## Phase 3：经验沉淀进知识库

### Task 7：创建 docs/runtime_experience.md

**Files:**
- Create: `docs/runtime_experience.md`

- [ ] **Step 1：创建文件，写入初始结构和现有已知经验**

内容来源于 CLAUDE.md 的「运行时经验」表，迁移为独立文件：

```markdown
# 运行时经验

> 此文件由 orchestrator 在每次子 Agent 完成后追加新发现。
> 通过 `mcp__vector_kb__semantic_search(query, source_type="docs")` 检索。
> 定期人工审查，过期条目直接删除。

## 已验证操作

| 场景 | 正确做法 | 禁止做法 |
|------|---------|---------|
| MuMu 开关控件点击 | 点 x=450-480, y=555 | 图片匹配开关图标 |
| 管理标签页：删除自定义标签页 | 点右侧三点按钮（x≈510）→ 底部弹窗 → 选删除 | 点左侧 icon（只是切换显示/隐藏） |

## 已验证 AW 方法

| 方法 | 页面 | 备注 |
|------|------|------|
| user.send_message(recipient, message) | 会话列表 → 聊天页 | isback=False 时停在会话内 |
| user.search(tab, text) | 搜索页 | isclose=False 时保持搜索页打开 |

## 已知限制

| 场景 | 描述 |
|------|------|
| Python 多行命令 | 走 PowerShell 执行；避免 CodeMaker Hub 路径校验报错 |
| OCR click_text 偏移 | 点击筛选标签/弹窗选项/底部栏按钮时，加 dy=8~12 偏移 |
```

- [ ] **Step 2：验证文件结构**

```bash
grep -n "^## " E:/UIAutotest/docs/runtime_experience.md
```

期望输出：
```
3:## 已验证操作
10:## 已验证 AW 方法
17:## 已知限制
```

- [ ] **Step 3：触发 embedding 增量更新，让文件进入向量索引**

```bash
cd E:/UIAutotest && python scripts/knowledge/embedding_pipeline.py --incremental
```

期望输出包含 `runtime_experience.md` 被处理的日志。

- [ ] **Step 4：验证可以被语义检索到**

```bash
cd E:/UIAutotest && python -c "
import sys
sys.path.insert(0, '.')
from mcp_servers.vector_kb.server import semantic_search
results = semantic_search('MuMu开关控件', source_type='docs', n_results=3)
for r in results:
    print(r['source'], r['content'][:80])
"
```

期望：输出中包含来自 `runtime_experience.md` 的内容。

- [ ] **Step 5：在 aw-orchestrator.md 中追加「经验沉淀」说明**

在 orchestrator 的「验证与推进」流程描述后，追加：

```markdown
## 子 Agent 完成后的经验沉淀

每次 aw-codegen/aw-verify/aw-element 返回 `[完成]` 后，orchestrator 检查返回内容中是否有 `NEW_EXPERIENCE` 或新发现的方法/限制，若有则追加到 `docs/runtime_experience.md`：

```bash
# 追加格式示例（orchestrator 直接 Edit 写入）
# docs/runtime_experience.md 的「已验证 AW 方法」或「已知限制」section 末尾追加一行
```

追加完成后，下次 embedding 增量更新（由 git post-commit hook 触发，或手动执行）会自动将新条目纳入向量索引。
```

- [ ] **Step 6：Commit**

```bash
git add docs/runtime_experience.md .claude/agents/aw-orchestrator.md
git commit -m "feat: 创建 runtime_experience.md 并纳入向量知识库，orchestrator 加经验沉淀流程"
```

---

## 验证整体改动

- [ ] **整体冒烟验证**：手动触发一次 convert-cases 流程，观察：
  1. orchestrator 在 spawn codegen 前是否执行了 G1-G5 检查
  2. codegen 子 Agent 返回内容中是否包含「阶段0完成」确认语
  3. orchestrator 是否使用了 Agent() 而不是 SendMessage 来调用 codegen

- [ ] **fix-batch 验证**：对已知存在共性失败的用例运行 fix-batch，观察：
  1. Phase 0.5 是否正确输出了共性分析结果
  2. 共性方法被修复后，同组其他用例是否被附带识别为修复

- [ ] **知识检索验证**：

```bash
cd E:/UIAutotest && python scripts/knowledge/embedding_pipeline.py --incremental
```

确认 `runtime_experience.md` 在索引中。
