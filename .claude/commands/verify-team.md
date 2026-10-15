---
description: 装配自检 — 对每个 agent 做 smoke test，验证蓝图、知识库、规则、文档都到位
---

## 任务

验证本工程的 5 人 AI 团队装配是否完整。每个 agent 读自己蓝图里的"强制前置阅读"清单并汇报就绪。

### 前提

团队已通过 `/bootstrap-team` 启动，或者准备调用 `Agent` 工具派出 subagent。

### 流程

#### 1. 检查蓝图文件存在

用 `Glob`：`E:\UIAutotest\docs\agents\swan\aw-*.md`

预期存在：
- aw-orchestrator.md
- aw-explorer.md
- aw-element.md
- aw-codegen.md
- aw-verify.md

缺任何一个 → 报错给用户，提示工程未完整 clone。（spec-keeper 已于
2026-10-12 随 openspec 流程移除而删除）

#### 2. 检查项目约定文件存在

用 `Read` 依次读：
- `E:\UIAutotest\CLAUDE.md`
- `E:\UIAutotest\.claude\README.md`

缺失 → 报错，提示补文件。

#### 3. 对每个 agent 做 smoke test

并行派 4 个 subagent（orchestrator 不用派，它就是当前主会话）。每个 prompt 模板：

```
你是 uiautotest-team 的 <role-name>，本次是 smoke test。
**不要执行任何实际业务**（不连模拟器、不改代码、不改知识库）。

步骤：
1. Read 你的蓝图 `E:\UIAutotest\docs\agents\swan\<role-name>.md`
2. 按蓝图里"强制前置阅读"清单逐个 Read，每个汇报 OK / 不存在
3. Glob 蓝图里提到的子目录（如 explorer 需要 glob pages/*.md 和 digest/features/*.md），报数量
4. 用 ≤150 字回答：
   - 我是谁（职责一句话）
   - 前置阅读是否全部到位（列出不存在的）
   - 职责边界：会做什么 / 不会做什么
   - 产出形态（给 orchestrator 的交付是什么样子）

不做任何实际任务。
```

并行派 4 个 agent（用 `Agent` 工具，`subagent_type=general-purpose`——stub 已于 2026-10-15 清退，角色定义 = 蓝图首读；`run_in_background=true` 让它们并行）：

> 备注：stub 已于 2026-10-15 清退，角色定义统一为 general-purpose + 蓝图首读。若会话不在 `E:\UIAutotest` 目录启动，`subagent_type` 对应的蓝图不会被加载。在 prompt 开头贴入蓝图 Markdown 全文或改为"以下是你的蓝图内容"并把蓝图 Markdown 粘贴进去。

#### 4. 汇总报告

等 4 个 agent 全部返回（或一个一个串行也行），按下表给用户一份检查表：

| Agent | 蓝图可读 | 前置阅读全到位 | 职责自述清晰 | 整体 |
|---|---|---|---|---|
| aw-explorer | ✅/❌ | ✅/❌（缺失列表） | ✅/❌ | PASS/FAIL |
| … | … | … | … | … |

最后给一句话总结：
- 全 PASS → "团队装配完整，可以开始使用"
- 有 FAIL → 指出缺失项，给出具体修复建议

#### 5. 清理（可选）

如果本次 smoke test 是通过 `TeamCreate` 临时拉的队（而不是在已有的 `uiautotest-team` 里），可以 `TeamDelete` 清理。如果是在真实团队里做的自检，保留。

### 预期耗时

5~10 分钟（5 个 agent 并行，各读 10 来个文件）。

### 禁止

- ❌ 真的执行业务任务（探索、截图、写代码、跑测试）
- ❌ 修改任何文件
- ❌ 为了"通过"而隐瞒 agent 的错误反馈
