# .claude/ 目录导航（UIAutotest）

> 本文件是 `.claude/` 的目录页：每个东西是什么、入口在哪、去哪读全文。
> 项目硬性规则在根目录 `CLAUDE.md`（所有 agent 必读的第一份文件）；本文不重复规则，只指路。
> （2026-10-14 重写：原 6-agent/MuMu/openspec 时代的接入指南已过时删除，历史版本见 git）

## 目录结构

```
.claude\
├── README.md                # ← 本文（目录导航）
└── commands\
    ├── bootstrap-team.md    # 一键拉起 aw 团队（general-purpose + 蓝图首读）
    ├── verify-team.md       # 团队装配自检
    ├── fix-batch.md         # 批量失败用例修复编排（Swan 口径，2026-10-14 改写）
    └── clean.md             # 清理
```

## 角色规程唯一权威 = docs/agents/swan/（本目录不再存 agent 定义）

五个长期角色的操作规程全部在 `docs/agents/swan/aw-<role>.md`（按项目分目录，单独演进）。
`.claude/agents/` 的 30 行 stub 已于 2026-10-15 清退——stub 与蓝图长期只差一句转发，单一权威消歧义。

- **拉起**：`Agent(subagent_type="general-purpose", name="aw-<role>")`，prompt 首行 = 先读对应蓝图 + CLAUDE.md（分工表见 CLAUDE.md「团队分工」）
- **恢复原生定义**（需要 frontmatter 级工具/模型控制时）：按蓝图新建 30 行 stub 放回本目录——name/description + tools/model +「⛔ 强制第一步读 docs/agents/swan/aw-<role>.md」，规程不复制

> 目录演进：rules\ 已于 10-14 清退（ai_workflow→docs/agents/swan/端到端工作流.md；aw_architecture→docs/aw-architecture.html；rules.mdc→CLAUDE.md「编码补充规则」）；skills\agent-run 已迁平台仓（28c9f4d）；agents\ stub 于 10-15 清退——本目录现只剩 commands\。

**改规则去哪改**：操作步骤/规范 → 改 `docs/agents/swan/` 蓝图；硬性铁律 → 改根目录 `CLAUDE.md`。


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
