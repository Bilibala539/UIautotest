# docs/ 文档索引

> 每个文档一行：路径 + 一句话主题。新文档落位后请同步更新本索引。
> 目录约定：项目级计划/规范/名册放 docs/ 根；各项目 agent 蓝图放 `docs/agents/<project>/`；对话纪要放 `docs/conversations/`；过时文档移 `docs/archive/`（文件头注明归档原因）。根目录只保留 README.md 与 CLAUDE.md。

## 项目计划与规范（docs/ 根）

| 路径 | 主题 |
|---|---|
| `待办与缺口清单.md` | **当前权威 plan**：已拍板决定 + 文档/环境缺口，开工前必读 |
| `平台建设计划.md` | Swan 测试平台建设进度计划（P1-P5，平台服务常驻 .166） |
| `测试套件管理计划.md` | 打包-流水线-套件总体计划 v2（Jenkins 执行层） |
| `平台UI设计规范.md` | dashboard 单页应用的唯一视觉与交互依据 |
| `agent团队名册.md` | Swan 平台 Agent 团队角色名册，会话恢复入口 |
| `编排流程详细设计.md` | 多 Agent 编排体系（人读版；机器可读实现见 `.claude/agents/`） |
| `UI元素截取与裁剪规范.md` | 元素截图/裁剪规范（`image_exists`/`click_image` 用图质量） |
| `runtime_experience.md` | 运行时经验知识库（子 Agent 踩坑沉淀，供语义检索注入） |
| `SETUP.md` | agent teams 配置包跨机器安装指南 |
| `ShowUI-Windows部署指南.md` | ShowUI-2B 多模态 UI 定位环境 Windows 部署（独立 venv） |

非 md 资产：`aw-architecture.html`（架构细则）。

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
| `测试用例文件规范.md` | 用例文件强制规范（一用例一文件、固定 setup/teardown） |

### docs/agents/web/（TidiTree Web 项目，未适配参考）

| 路径 | 主题 |
|---|---|
| `README.md` | 启用说明（参照 swan/ 模式适配后使用） |
| `aw-orchestrator.md` / `aw-explorer.md` / `aw-element.md` / `aw-codegen.md` / `aw-verify.md` | 各角色蓝图旧版，未适配三平台现状 |

## 对话纪要（docs/conversations/）

| 路径 | 主题 |
|---|---|
| `README.md` | 纪要归档约定（命名、脱敏要求） |
| `2026-09-08-aw双维度重构与验证码平台.md` | 2026-09-08 工作对话纪要 |

## 已归档（docs/archive/）

| 路径 | 主题 |
|---|---|
| `功能地图-v1.md` | Swan App 功能地图 v1（已被 `knowledge/swan/系统认知/功能地图.md` v2 取代） |
| `swan_kb_session_handoff.md` | Swan 知识库 v1 会话交接（v1 已建成，交接完成） |
| `2026-06-12-v5-orchestration-fusion-design.md` | v5 编排融合设计（大部分已落地） |
