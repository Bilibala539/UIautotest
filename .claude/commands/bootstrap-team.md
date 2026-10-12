---
description: 一键把 UIAutotest 5 人长期团队拉起来（orchestrator + explorer + element + codegen + verify）
---

## 任务

按以下步骤，把 `uiautotest-team` 团队实例化到当前会话。

### 1. 清理同名旧队

先 `TeamList`（如果 team 名 `uiautotest-team` 已存在）或直接尝试 `TeamCreate`。如果旧队还在但上一次会话已断（teammate 全成 ghost），用 `TeamDelete` 清掉再重建。

### 2. 建队

调用 `TeamCreate`：
- `team_name`: `uiautotest-team`
- `agent_type`: `aw-orchestrator`
- `description`: `UIAutotest 长期团队：App 探索、元素截图、AW/用例生成、验证`

### 3. 派 4 个下游 teammate

团队实例建好后，通过 `Agent` 工具按下表依次派出 4 个 teammate。每个 teammate 启动时给它：
- `team_name`: `uiautotest-team`
- `name`: 对应 agent 名
- `subagent_type`: 对应 agent 名（即 `.claude/agents/<name>.md` 的 name）
- 初始任务：读 `CLAUDE.md`，再读自己蓝图里"必读"一栏的文件，读完后以以下格式向 orchestrator 汇报：
  ```
  [就绪]
  职责：<一句话>
  已读文件：<列表>
  待命
  ```

| name | subagent_type | 职责一句话 |
|---|---|---|
| explorer | aw-explorer | App 探索、更新知识库 |
| element | aw-element | UI 元素截图、注册常量 |
| codegen | aw-codegen | 业务 AW、PPUser 便捷方法、pytest 用例 |
| verify | aw-verify | 跑测试、诊断失败、图片转正 |

说明：orchestrator 就是当前的主会话（team lead），不用再派。（spec-keeper 已于
2026-10-12 随 openspec 流程移除而删除）

### 4. 发令牌

4 个 teammate 全部回报就绪后，作为 orchestrator 发送一条群发消息（每个 teammate 各发一次），内容：

> 团队就位。后续我会用标准任务格式派活。收到任务后：
> 1. 按自己蓝图的"上下文加载"规则加载相关知识（CLAUDE.md 必读，其余按需）
> 2. 每完成一个关键节点主动发"[进度]"消息，不要等到最后才汇报
> 3. 完工后用"[完成]"或"[失败]"格式向我回报
> 4. 发现超出职责范围的事，不要擅自做，回告我重新分派

### 5. 报告给用户

完成后给用户发一份简报：
- 已创建团队 `uiautotest-team`
- 5 个 teammate 名单 + 各自的 agentId
- 接下来怎么用（举 2-3 个例子，比如 "帮我探索 XX 页面"、"帮我为 YY 功能生成 pytest"、"帮我把 image_ai/ 里某批图片转正"）
- 会话结束时要不要 `TeamDelete`（建议：保留，下次 `/bootstrap-team` 会幂等处理）

## 幂等性

如果用户在同一会话里多次调用 `/bootstrap-team`：
- 已有 teammate 不要重复派
- 缺失的才补
- 报告里显式说明"已存在 X 人 / 本次新派 Y 人"
