> 已归档（2026-09-16）：2026-06 的 v5 编排融合设计，大部分已落地（见文内状态行），剩余项见 docs/待办与缺口清单.md。

# 编排融合设计：吸纳 ui-ai-v5 优势

**日期**：2026-06-12  
**状态**：大部分已落地（2026-09-07 核对）  
**范围**：编排层 + 支撑脚本（不改测试框架本身）

> **落地情况**：
> - ✅ Phase 1（fix-batch 增强）：`fix-batch.md` 已含 Phase 0.5 共性根因分析和基线回归验证
> - ✅ Phase 2（子 Agent 架构改造）：element/codegen/verify 已改为 `Agent()` 一次性子 Agent，explorer/spec-keeper 保持长驻
> - ✅ Phase 3 部分：G1–G5 派发门禁、批次空间认知注入、阶段0确认令牌均已进 orchestrator/agent 蓝图
> - ❌ Phase 3 缺口：`docs/runtime_experience.md` 未创建，经验沉淀尚无落盘文件
>
> 原始设计保留如下，供追溯决策依据。

---

## 背景

当前 UIAutotest 采用 Agent Teams 多 Agent 协作模式，aw-explorer / aw-element / aw-codegen / aw-verify 均为长驻 Agent，通过 SendMessage 双向通信。

ui-ai-v5 工程的实践暴露了长驻 Agent 的三个核心问题：

1. **上下文污染**：aw-codegen / aw-verify 在多任务后累积了大量无关历史（pytest 输出、截图描述），影响后续代码生成质量
2. **fix-batch 效率低**：同一 AW 方法导致多个用例失败时，被当作独立任务逐个修，实际只需修一次方法本身
3. **知识注入过宽**：向子 Agent 传入的知识库上下文缺乏精确过滤，无关内容增加干扰

本方案在保留 Agent Teams 整体架构和双层知识库（Graph + Embedding MCP）的前提下，针对性地吸纳 v5 的三项优势。

---

## 设计原则

- **不破坏现有功能**：每个 Phase 独立可验证，不影响前一 Phase 正常运作
- **双层知识库完整保留**：knowledge_graph MCP + vector_kb MCP 是核心基础设施，所有改动在其上叠加，不替换
- **最小化改动范围**：只改编排层（`.claude/agents/`、`.claude/commands/`、orchestrator prompt），不改 `utils/`、`tests/`、`image/` 等业务代码

---

## 一、架构改动：混合 Agent 生命周期

### 决策

| Agent | 现在 | 改后 | 原因 |
|---|---|---|---|
| aw-explorer | 长驻 SendMessage | **保持长驻** | 探索是积累性的，跨页面上下文有价值 |
| aw-element | 长驻 SendMessage | **改为子 Agent** | 截图任务无状态，每次独立 |
| aw-codegen | 长驻 SendMessage | **改为子 Agent** | 代码生成必须上下文干净，历史是噪音 |
| aw-verify | 长驻 SendMessage | **改为子 Agent** | pytest 输出不应污染下一次执行 |
| spec-keeper | 长驻 SendMessage | **不参与编排主流程** | 仅在 openspec 提案流程时独立使用，与日常测试流程无关 |

### 实现方式

`.claude/agents/` 下的定义文件**不删除**，其系统提示直接被 Agent() 调用复用。orchestrator 的调用方式从 SendMessage 改为 Agent()：

```python
# 改前（长驻，SendMessage，上下文累积）
SendMessage(to="aw-codegen", message="任务：...")

# 改后（子 Agent，每次干净上下文）
Agent(
    subagent_type="aw-codegen",   # 复用 .claude/agents/aw-codegen.md 的系统提示
    prompt="""
    [自包含的任务描述]
    ## 批次空间认知
    {本批次涉及页面的 KB 查询结果}
    ## 已知经验
    {从 experience.md 过滤的相关条目}
    ## 任务
    {具体用例/AW 描述}
    完成标准：{...}
    """,
)
```

### orchestrator 对应改动

- 移除 `SendMessage(to="aw-codegen/aw-verify/aw-element", ...)` 调用
- 改用 `Agent(subagent_type=..., prompt=...)` spawn 临时子实例
- 子 Agent 返回结果后，orchestrator 负责更新 experience.md 和 case_status.md
- aw-explorer / spec-keeper 保持原有 SendMessage 方式不变

---

## 二、fix-batch 增强：共性根因分析

### 现有问题

fix-batch 当前把每个失败用例当独立任务处理。当 5 个用例共同依赖同一个 AW 方法失败时，会跑 5 次修复，但只需修一次方法本身。

### 新增 Phase 0.5：共性分析

在分派修复任务之前插入分析步骤：

```
Phase 0：读 pytest 失败输出 / 本地 HTML 日志
Phase 0.5：共性根因分析（新增）
  ├─ 从每个失败 traceback 提取最后调用的 AW 方法
  │   示例：utils/aw/aw_base.py 中的基础操作方法
  ├─ 按方法分组：
  │   click_session_box → test_A, test_B, test_C（3个）← 疑似共性
  │   tap_group_settings → test_D（1个）← 独立
  ├─ 二次验证（防误归类）：以下 2 项一致才确认为共性
  │   - 异常消息核心内容相同（同一个 image/元素名）
  │   - 失败栈帧行号相近（±3行）
  ├─ 交叉比对：同方法有 PASS 用例 → 方法没问题，看调用差异
  │             全部 FAIL → 方法本身有 bug，直接修方法
  └─ 输出优先级队列：共性问题排前，独立问题排后

Phase 1：按优先级逐个处理（共性问题修一次，独立问题逐个修）
Phase 2：（共性修复后重跑 pytest）剩余失败重新分析，不沿用上轮结论
```

### AW 方法基线回归验证

当 aw-verify 修改了 `utils/aw/aw_base.py` 中的方法时，额外触发：

```bash
# 1. 暂存修改
git stash

# 2. 修复前跑依赖该方法的其他用例，记录基线
pytest tests/ -k "相关用例" -v --tb=line > /tmp/baseline.txt

# 3. 恢复修改
git stash pop

# 4. 修复后跑同组用例
pytest tests/ -k "相关用例" -v --tb=line > /tmp/after_fix.txt

# 5. 对比
# baseline PASS → after FAIL = 真实回归，revert
# baseline FAIL → after PASS = 附带修好，保留
```

判定：搞坏的用例数 > 修好的用例数 → `git checkout -- .`，本次修复放弃，记录后交人工。

---

## 三、上下文注入优化

### 3.1 批次空间认知注入

orchestrator 在 spawn codegen/verify 子 Agent 前，先用 MCP 查询本批次涉及的页面，只注入相关知识片段：

```python
# orchestrator 执行（复用现有 MCP 工具）
related = mcp__knowledge_graph__get_related_pages("group_settings_page")
similar = mcp__vector_kb__find_similar_tests("群设置功能用例")

# 注入 Agent prompt 的 "批次空间认知" 段
# 全量知识库不进子 Agent
```

不涉及的页面的 KB 内容一律不传入。

### 3.2 经验沉淀进知识库

不单独维护 experience.md 文件，改为写入 `docs/runtime_experience.md`，纳入现有 Embedding 层统一管理。

每次子 Agent 执行完成，orchestrator 将新发现的方法/限制追加写入该文件：

```markdown
## 已验证方法
| 方法 | 页面 | 备注 |
|------|------|------|
| click_session_box(name) | 会话列表页 | ✓ 可用 |

## 已知限制
| 场景 | 描述 |
|------|------|
| 平台开关控件 | 优先使用图片或 OCR 定位，不写死坐标 |
```

spawn 子 Agent 前，orchestrator 通过语义检索找相关经验，注入 prompt：

```python
# 语义检索比关键词匹配更准确
experience = mcp__vector_kb__semantic_search(
    query="当前任务描述",
    source_type="docs"
)
# 只注入相关条目，不注入全量
```

文件随版本迭代定期人工审查，过期条目直接删除，embedding 增量更新。

### 3.3 子 Agent 启动确认令牌

所有子 Agent（aw-codegen/aw-verify/aw-element）的 prompt 末尾加入强制确认要求：

```
⛔ 在输出以下确认语之前，禁止执行任何操作：
"阶段0完成：已读 CLAUDE.md / AW复用指南 / 元素常量"
```

orchestrator 检查子 Agent 返回内容是否包含该确认语。若无，视为启动异常，重新 spawn（最多 1 次重试）。

---

## 四、前置门禁：用例自检表

orchestrator 生成用例描述后、spawn codegen 子 Agent 前，过以下自检表。任意一项 ❌ 则阻断，补全后重新检查：

| # | 检查项 | 验证方式 | 不过后果 |
|---|---|---|---|
| G1 | 涉及的页面已在知识库中 | `mcp__knowledge_graph__list_pages()` | ❌ 先派 aw-explorer |
| G2 | 涉及的元素图片已注册 | grep `image/image_name_mapping.py` | ❌ 先派 aw-element |
| G3 | 有 setup 造数 → test 方法末尾有对应清理调用（如 `dissolve_group()`、`recall_message()`） | 检查 test 方法末尾 | ❌ 补充清理调用 |
| G4 | teardown 最后能回到消息首页 | 检查 teardown 描述末尾 | ❌ 补充回首页步骤 |
| G5 | 同功能参数变体是否已合并 parametrize | 检查是否多个相似用例 | ⚠️ 提示合并，不阻断 |

---

## 分阶段落地计划

### Phase 1：fix-batch 增强（2–3天）
- 修改 `.claude/commands/fix-batch.md`，加入 Phase 0.5 共性分析
- 加入 AW 方法基线回归验证逻辑
- **验证方式**：跑一批已知失败用例，确认共性问题被正确归类并优先修复

### Phase 2：子 Agent 架构改造（3–5天）
- 修改 `aw-orchestrator.md`，将 aw-codegen/aw-verify/aw-element 的调用从 SendMessage 改为 Agent()
- 在 orchestrator prompt 中加入批次空间认知注入逻辑
- **验证方式**：跑一个完整的 convert-cases 流程，确认用例生成质量不低于改前

### Phase 3：经验沉淀 + 自检表（1–2天）
- 创建 `docs/runtime_experience.md`，纳入 embedding pipeline
- 在 orchestrator 中加入经验语义检索注入和子 Agent 启动确认令牌检查
- 在 orchestrator 中加入 G1–G5 自检表逻辑
- **验证方式**：观察连续多次 codegen 任务后，子 Agent 收到的 prompt 是否保持精简且包含有效经验

---

## 不改动的内容

- `utils/aw/aw_base.py` — AWBase 设备交互层不变
- `utils/aw/aw_base.py` — 基础 AW 方法保持兼容
- `utils/user.py` — TTUser 基础 AW 入口
- `tests/` — 所有现有测试用例不变
- `image/` / `image_ai/` — 元素图片流转机制不变
- `explorer_output/knowledge/` — 双层知识库结构完整保留
- `.mcp.json` — MCP Server 注册不变
- `mcp_servers/` — knowledge_graph / vector_kb MCP 实现不变
- `scripts/knowledge/` — 知识库维护脚本不变
