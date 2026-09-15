# Swan 知识库 INDEX(唯一入口,agent 与人开工先读本文件)

> 2026-09-15 由 `E:\swan-qa-share`(F:\SwanApp-Toolchain 知识库快照,基线 App dev@4d1ed7b / core dev@402853ab)与本地元素层知识库合并而成。
> 维护规则:任何子库有新增/状态变化,对应行必须更新。恢复状态第一入口:本文件 + `reports/session-state.md`。
> 原始快照留底于 `E:\swan-qa-share\`,只读不改;反馈给源头机器时以本目录为准。

## 目录地图

| 子库 | 路径 | 内容 |
|---|---|---|
| 页面/元素层(本地) | `pages/` `digest/` `app_map.json` `backlinks.json` | 43 页元素知识、链路摘要;**人读入口:`digest/中文索引.md`** |
| 系统认知(并入) | `系统认知/` | 功能地图(18 域/123+ 功能点)、模块卡片 login/search/app/core、接口清单、架构总览 |
| 用例库(并入) | `cases/` | login 47 条 L2 双通道(cases/login/)+ 模块17搜索 14 条(cases/fullregression 下 SWAN-20260911 为全回归用例) |
| BUG 库(并入) | `bugs/` | 6 份 BUG 报告 + 模式库 P-001~P-004 + flaky 登记表 |
| 报告/过程(并入) | `reports/` | 轮次报告、周期汇报、session-state.md(全程会话日志) |
| 治理登记(并入) | `registries/` | 仓库注册表、device-pool.md(设备池)、业务要求映射表、05f 审计日志、credentials-registry.md |
| 可执行测试(本地) | `E:\UIAutotest\tests\flutter\` | pytest 脚本,由 cases/ YAML 经 convert-cases 流水线翻译而来 |
| 业务封装(本地) | `E:\UIAutotest\utils\aw\business\swan.py` | SwanBusiness,用例步骤的用户意图级方法 |

## 模块清单

| 模块 | 卡片 | 用例状态 | 最近轮次 | 基线 | 最后更新 |
|---|---|---|---|---|---|
| login | 系统认知/模块卡片-login.md | L2 47(正14+逆33);执行单元 41,PARTIAL 🟢2/🔴1/🟡18/⏳19(源机暂停) | SWAN-20260907-005 | dev@4d1ed7b/core@402853ab | 2026-09-07 |
| module-17-search | 系统认知/模块卡片-search.md | L2 14(正6+逆8,未执行) | SWAN-20260904-003 | dev@4d1ed7b | 2026-09-04 |
| HiVi-Network-FlutterApp | 系统认知/模块卡片-app.md | 无用例(L1/L2 绿) | SWAN-20260904-001 | dev@4d1ed7b | 2026-09-04 |
| hivi_network_flutter_core | 系统认知/模块卡片-core.md | 无用例(仓库自带测试过) | SWAN-20260904-001/002 | dev@402853ab | 2026-09-04 |
| 功能地图 | 系统认知/功能地图.md | v2-draft:125 路由全枚举、104 未考古条目裁决、4 未确认全裁决 | SWAN-20260910-001 | dev@4d1ed7b/core@402853a | 2026-09-10 |

## 本机接手状态(2026-09-15,UIAutotest 侧)

- **已完成**:五域知识迁入;INDEX.md 合并入口;模块卡片-login 元素层校注;设备池本地化(荣耀 JDY-AN00 在线/OPPO c0614b6a 未连/AVD 未启用);审计日志、session-state 已由本侧续写。
- **已完成**:login 正向 14 条逐条评级(cases/login/TRANSLATION-NOTES.md),5 条翻译落地 `tests/flutter/test_swan_login_positive.py`,SwanBusiness 新增 3 个业务方法;数据映射统一走 .env.local。
- **进行中**:真机执行 5 条待跑;逆向 33 条、搜索/全回归翻译待铺开;看板接活数据、反馈包回传源机待做。
- **本机差异**:真机荣耀 JDY-AN00(Android 14,720×1612)在线;验证码走 otp-gateway(.166:18080)自动取码;账号在 `.env.local`。
- **总览页**(给同事):`E:\UIAutotest\docs\Swan测试工程总览.html`。

## 检索

- 语义检索:Chroma 向量库(`.chroma_db/`),MCP:knowledge_graph_swan / vector_kb_swan。
- 查坑:先看对应模块卡片 + 页面文件"坑"节;报新 BUG 前先查 `bugs/` 查重;负向用例设计先查 `bugs/模式库.md`。
