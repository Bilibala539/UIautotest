# .claude/ 目录导航（UIAutotest）

> 本文件是 `.claude/` 的目录页：每个东西是什么、入口在哪、去哪读全文。
> 项目硬性规则在根目录 `CLAUDE.md`（所有 agent 必读的第一份文件）；本文不重复规则，只指路。
> （2026-10-14 重写：原 6-agent/MuMu/openspec 时代的接入指南已过时删除，历史版本见 git）

## 目录结构

```
.claude\
├── README.md                # ← 本文（目录导航）
├── agents\                  # 5 个 Swan aw 角色的会话入口（stub）
│   ├── aw-orchestrator.md   #   总协调——正文指向 docs/agents/swan/aw-orchestrator.md
│   ├── aw-explorer.md       #   App 探索
│   ├── aw-element.md        #   元素截图与常量注册
│   ├── aw-codegen.md        #   业务 AW 与用例编码
│   └── aw-verify.md         #   跑 pytest / 诊断失败 / 图片转正
├── commands\
│   ├── bootstrap-team.md    # 一键拉起 aw 团队
│   ├── verify-team.md       # 团队装配自检
│   ├── fix-batch.md         # 批量失败用例修复编排（Swan 口径，2026-10-14 改写）
│   └── clean.md             # 清理
├── skills\
│   └── agent-run\           # 常驻 agent 运行技能
└── rules\                   # （已清空 2026-10-14）
                             #   原 ai_workflow.mdc → docs/agents/swan/端到端工作流.md
                             #   原 aw_architecture.mdc → docs/aw-architecture.html
                             #   原 rules.mdc → CLAUDE.md「编码补充规则」节
```

## stub → 蓝图 两级结构（本目录的核心设计）

`.claude/agents/<role>.md` 是**30 行以内的 stub**：写触发条件、上下文加载清单、职责红线，
详细操作规程全部指向 `docs/agents/swan/` 下的对应蓝图（800 行级，单独演进）。

这样分工的原因：
- Claude Code 每次派 agent 只注入 stub——上下文轻
- 蓝图在仓库里随代码走版本，改动有 diff 可审
- 换机器/新会话，行为由「stub + 蓝图 + CLAUDE.md」三者共同决定，一致可复现

**改规则去哪改**：操作步骤/规范 → 改 `docs/agents/swan/` 蓝图；硬性铁律 → 改根目录 `CLAUDE.md`；触发/加载清单 → 改 stub。

## 派活路由（详见 CLAUDE.md「团队分工」）

| 任务特征 | 派给谁 | 对应蓝图 |
|---|---|---|
| 摸页面 / 知识库缺页面 | aw-explorer | `docs/agents/swan/aw-explorer.md` |
| 截 UI 元素 / 注册图片常量 | aw-element | `docs/agents/swan/aw-element.md` |
| 写业务 AW / pytest 用例 | aw-codegen | `docs/agents/swan/aw-codegen.md` |
| 跑测试 / 诊断失败 / 图片转正 | aw-verify | `docs/agents/swan/aw-verify.md` |
| 批量修复失败用例 | 主会话走 `/fix-batch` | `.claude/commands/fix-batch.md` |

写新用例的端到端步骤（Phase 1-5）：`docs/agents/swan/端到端工作流.md`。
架构（双维度：基础按端 / 业务按项目）：`docs/aw-architecture.html`。

## AI 助手在本目录工作时的三条约定

1. **先读 `CLAUDE.md`**（硬性规则 + 关键路径速查），再按任务读对应蓝图全文
2. **派 agent 用角色名**（`subagent_type="aw-codegen"` 等），不要用 general-purpose——stub 里的加载清单才会生效
3. **改蓝图/stub 前先看 git log**——这两个目录都是版本化的，改动可追溯

## 与平台侧的边界（2026-10-13 起）

测试平台（Swan 平台/工作站）代码与模块 agent 定义已剥离至 **swan-map-station** 仓
（本地 `E:\swan-map-station`），分离方案见平台仓 `docs/测试平台分离准备.md`。
本仓 `.claude/` 只管自动化测试框架侧（aw 五角色）；平台相关工作去平台仓做。
