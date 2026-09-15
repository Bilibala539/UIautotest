# BUG 报告：SWAN-BUG-20260904-004

- 任务：`SWAN-20260904-005-search-execution`
- 分类：`broken`（运行时 ANR 候选，未形成 L2 业务断言）
- 模块：`com.swan.network` 启动 / `MainActivity`
- 基线：App `dev@4d1ed7b1d727f12906d6ac9fa9ed195966e464b3`
- 现象：首次启动探针出现系统对话框 `Swan Audio isn't responding`；随后 hierarchy 复核进入登录页，暂未稳定复现。
- 证据：`F:\SwanApp-Toolchain\results\SWAN-20260904-005-search-execution\evidence\maestro-hierarchy.txt`、`anr-recheck.png`、`anr-recheck-hierarchy.txt`
- 结论：记录为间歇性 ANR 候选；不计入搜索 L2 失败，不得在未重复复现前提单。
- 后续：独立 ANR/性能任务复现，确认主线程堆栈后再决定提单。

## 证据增强（2026-09-10，SWAN-20260910-001-feature-boundary）

- B 线探索两日内 4 次 ANR，**触发点扩展**：不止启动时序——文本输入（片 1 A-1，dropbox ErrorId 7101afa5）与登录点击（SWAN-BUG-20260910-002，ErrorId 57f0fd98）均可触发 "Swan Audio isn't responding"。
- **放大器确认**：scrcpy 镜像挂载期间 media.swcodec 常驻 ~50% CPU，4 次 ANR 均发生在挂载期间；交互期停录屏/不挂 scrcpy 后显著缓解。据此宪法可见性规则修订为 v1.3（默认不挂 scrcpy）。
- 结论修正：P-003 嫌疑链路由"启动时序"扩展为"输入/焦点事件链路 + 编码负载放大"，出现次数升为 2（候选）。
