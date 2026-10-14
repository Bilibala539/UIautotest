# docs/ 文档索引

> 每个文档一行：路径 + 一句话主题。新文档落位后请同步更新本索引。
> 目录约定：项目级计划/规范放 docs/ 根；各项目 agent 蓝图放 `docs/agents/<project>/`；对话纪要放 `docs/conversations/`；过时文档直接删除（git 历史即归档，不再设 archive/ 目录）。根目录只保留 README.md 与 CLAUDE.md。

## 项目计划与规范（docs/ 根）

| 路径 | 主题 |
|---|---|
| `待办与缺口清单.md` | **当前权威 plan**：未闭环缺口 + 已拍板去向表，开工前必读 |
| `AW补全计划.md` | **Swan AW 层补全计划**（范围：仅 flutter/Swan）：批次表/阻塞清单/编排方式/验收口径，每批完成更新 |
| `Swan回归用例AW实现方案.md` | 76 条 P0 回归用例的 AW 实现清单（AW补全计划 W1 批次按其用例号派生） |
| `UI元素截取与裁剪规范.md` | 元素截图/裁剪规范（`image_exists`/`click_image` 用图质量） |
| `runtime_experience.md` | 运行时经验知识库（子 Agent 踩坑沉淀，供语义检索注入） |
| `ShowUI-Windows部署指南.md` | ShowUI-2B 多模态 UI 定位环境 Windows 部署（独立 venv） |

非 md 资产：`aw-architecture.html`（架构细则）。
平台侧文档（平台建设计划/平台UI设计规范/agent团队名册/agent模块档案/分离准备 等）已于 2026-10-13 随平台分离迁至 **swan-map-station** 仓 `docs/`，本仓不再保留副本。

## 各项目 agent 蓝图（docs/agents/）

范式：每个项目一个子目录，`.claude/agents/<role>.md` 为会话入口，本目录为对应项目蓝图。

### docs/agents/swan/（Swan Flutter 项目，现行）

| 路径 | 主题 |
|---|---|
| `aw-orchestrator.md` | 总协调蓝图（派发门禁 G1-G5、经验沉淀流程） |
| `aw-explorer.md` | App 探索蓝图（页面考古、知识库写入） |
| `aw-element.md` | 元素截图与注册蓝图 |
| `aw-codegen.md` | 业务 AW 与用例编码蓝图 |
| `aw-verify.md` | 验证蓝图（跑 pytest、诊断失败、图片转正） |
| `端到端工作流.md` | 端到端写用例工作流（Phase 1-5：知识库→探索→截取→生成→验证转正；自 `.claude/rules/ai_workflow.mdc` 并入） |
| `AW方法指南.md` | **已有 AW 方法唯一查询入口**（34 业务方法+回归 mixin+基础操作速查；写新用例/AW 前必查，防重复创建） |
| `AW方法编写规范.md` | **AW 方法写法强制规范**（签名/docstring 六要素/定位/断言收尾/幂等短路/自检清单） |
| `测试用例文件规范.md` | 用例文件强制规范（一用例一文件一 test 方法、固定 setup/teardown） |

## 对话纪要（docs/conversations/）

| 路径 | 主题 |
|---|---|
| `README.md` | 纪要归档约定（命名、脱敏要求） |
| `2026-09-08-aw双维度重构与验证码平台.md` | 2026-09-08 工作对话纪要 |
