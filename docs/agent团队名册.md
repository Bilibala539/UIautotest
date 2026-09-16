# Swan 平台 Agent 团队名册

> 用途:会话重启(/resume)或新会话时,主会话(调度者)读本文件即可恢复团队全貌。
> 角色定义文件在 `C:\Users\menglz.SWANSPEAKERS\.claude\agents\`;开发任务进度详见 `docs/测试套件管理计划.md`(总体计划 v2)。

## 协作模式

主会话 = 调度者:接收用户任务 → 派给对应模块 agent → 验收(diff 审查+冒烟)→ 统一提交 git → 部署 .166 → 向用户汇报。
模块 agent:只改自己模块,不部署、不提交 git,自测用临时端口+临时 db。

## 团队成员

| 代号 | 职责 | 状态 | 备注 |
|---|---|---|---|
| 调度者(主会话) | 任务接收/分配/汇总/验收/提交/部署/播报 | 常驻 | 巡检 cron 每 23 分钟(会话内) |
| 用例管理 agent | case_defs CRUD、用例管理页、sync_cases.py | 待命(可唤醒) | 修复过列宽拖拽×2、列重叠;单列宽度=可见列宽之和的方案已验证 |
| **jenkins打包模块开发** | .166 构建环境(JDK17/Android/Flutter)+ scripts/build_swan_apk.py | ✅ 环境与脚本已交付(a690bc5);在修 register_apk.py 缺 apk_id 的 bug | 构建环境:C:\build-env\+env.ps1(JDK17 Temurin/Android SDK 34+36/Flutter 3.47.4 南京大学镜像,flutter doctor 通过);**阻塞:auto_tester 权限未生效,真打包未验**;注意 .166 的 python 是 WindowsApps 占位符,远程跑脚本用 py -3 |
| **平台侧流水线开发** | pipeline_configs + 调度器 + 流水线页面 | ✅ 已交付(1118a66+aff7db7,已部署) | 已完成:套件→case_filter 聚合、web 平台支持、门禁按平台裁剪、rc3 补 run 收尾(执行会话/流水线状态一致) |
| **平台侧用例模块开发** | 测试套件管理 M4 + 用例页 6 条优化 + 规范对齐 | ✅ 已交付部署(34fcedd+aff7db7,2026-09-16) | 套件 CRUD/成员管理/modules/优先级徽章/编辑抽屉/**批量导入+CSV 模板下载**(aff7db7);未尽:批量操作条、toast 组件、账号体系 |
| **平台侧产品设计师** | 全网检索同类测试平台交互与 UI,产出 docs/平台UI设计规范.md;所有开发 agent 页面开发以规范为唯一依据 | 设计中(2026-09-16) | 只设计不改代码;规范落地后按 P0/P1 建议清单驱动各页签改造 |

## 关键约定(全团队硬性纪律)

1. 凭据(auto_tester 密码/禅道账密)只存 .166 `E:/uiautotest/.env.local`,不进 git/代码/文档
2. agent 不部署(不 ssh .166 杀进程/不动计划任务)、不提交 git——主会话统一做
3. .166 上绝不 kill 全部 pythonw,只杀指定 PID
4. 提单(禅道)必须人工确认;企微机器人外发先征得用户同意
5. 冒烟:临时端口 180xx + 临时 db,测完删;JS 改动 node --check + `$()` 引用交叉核对
6. 部署节奏:commit → push → .166 pull → 杀 8080 指定 PID → schtasks /run TestHistoryDashboard(首次拉起常失败,跑两次并验证 8080 监听)

## 交接记录

- 2026-09-16 平台侧流水线开发交付:commit 1118a66(服务已重启生效,`/api/pipeline-configs` 200;PipelineScheduler 计划任务 Running,日志 logs/pipeline_scheduler.log)。未尽:套件下拉未填充(等 M4)、include_build 只存配置未接执行层、调度器停机跨分钟不补跑
- 2026-09-16 待办:① 催项目 Owner 把 auto_tester 加进 swan-audio(Reporter,直接成员)② 用户提供仓库准确 Clone 地址 ③ 权限通后 jenkins打包模块开发 联调真打包,随后 M3 Jenkins 接入(.166:8082)
