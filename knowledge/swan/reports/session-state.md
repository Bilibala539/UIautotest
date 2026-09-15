# Session State

更新时间：2026-09-15（知识库迁入 UIAutotest,login 翻译试点完成）
状态来源：外置状态回写（TEST-SYNTHETIC）

> ## 🔄 活跃任务：UIAutotest 知识融合（2026-09-15 开工,UIAutotest 侧续写）
> **背景**：本知识库自 F:\SwanApp-Toolchain 快照(E:\swan-qa-share)迁入 E:\UIAutotest\knowledge\swan,与本地元素层知识库(43 页)合并;原始快照留底只读。**此后本文件由 UIAutotest 侧续写**,源机记录保留在下方历史块。
> - **已完成**：五域知识落位(系统认知/cases/bugs/reports/registries);INDEX.md 合并入口;模块卡片-login 增补本机元素层校注;设备池本地化(荣耀 JDY-AN00 在线,OPPO c0614b6a 未连)。
> - **login 翻译试点**：正向 14 条评级 9 全自动/3 受限/2 BLOCKED/1 禁止(评级表:cases/login/TRANSLATION-NOTES.md);5 条已翻译 → `tests/flutter/test_swan_login_positive.py`;SwanBusiness 新增 enter_sms_code_step / fill_sms_code / relaunch_app。
> - **数据映射裁决**：YAML 的 TEST-SYNTHETIC 账号池(13800000002 等)在测试环境未必预置,翻译件统一改走 .env.local 真实账号(users("swan"));抓包级断言(请求体/token 三处同步/请求计数)降级为 UI 态断言。
> - **下一步**：① 真机执行 5 条(荣耀或 OPPO 接入后,PLATFORM=flutter)②逆向 33 条翻译 ③搜索/全回归用例翻译 ④看板接活数据 ⑤反馈包回传源机。**版本核对跳过中(用户指示)**——大规模回归前需对齐 App 基线。
> - **总览页**：`E:\UIAutotest\docs\Swan测试工程总览.html`(给同事的融合说明,三色标注来源)。

> ## 🔄 活跃任务：SWAN-20260911-001-fullregression（2026-09-11 11:30 开工）
> **用户指令**：从 `C:\Users\swan\Desktop\Hivi-Network` 拉取新版代码，与本地已有代码隔离，自行打 APK 装模拟器，全量测试本版本。
> - **隔离部署完成**：快照（非 git，无 .git）→ `E:\SwanApp\repos\flutter\hivi-network-snapshot-20260911\`（App + Core 并排，满足 `../hivi_network_flutter_core` 相对路径依赖）；已有检出（App@4d1ed7b / Core@402853ab）零触碰。快照版本 5.3.0 build 32（IOS_BUILD 129 / OHOS 32，与旧快照不同，内容更新）。差异规模初估：App 623 文件 / Core 849 文件与基线不同。
> - **APK 已打包安装**：`flutter build apk --debug --flavor general` 459.6s 成功 → `E:\SwanApp\artifacts\app-general-debug-snapshot-20260911.apk`（221MB）→ adb install -r 至 emulator-5554（升级安装，userdata 保留）。**启动实测：登录态过时**（toast"登录状态过时"，回到登录页）——需重新登录。
> - **用户裁决（2026-09-11）**：验证码=**人工给码模式**（沿用上轮，号码 acct-swan-mobile）；执行到收码点停下，主对话向用户转发。
> - **并行三从已派发**：A 线 qa-archaeologist 差异考古（快照 vs dev@4d1ed7b，产 delta-analysis.md）+ 用例双从（正向/逆向，基于功能地图 v2 全量回归，互盲）。
> - **设备**：emulator-5554 已登记占用（00c 已回写 🟢）；开机预检：宿主可用内存 14.8G/31.7G 舒适档通过。
> - **任务卡**：`plans/011-fullregression/011-card-main.yaml`；结果目录 `results/SWAN-20260911-001-fullregression/`。

> ## ✅ 任务收口：SWAN-20260910-001-feature-boundary（2026-09-10 20:00，用户裁决"收口"）
> - **执行规模**：A 线代码解析（18 域，104 条裁决，地图 v2）+ B 线模拟器探索 9 片全绿（登录前 3 片 + 登录后 6 片，含一次播放越界规范止损 P-9-1）；证据 ~100 文件，states-matrix §1-33。
> - **收口动作已完成**：设备已释放（emu kill 存快照，00c 回写"⏸已关机"；**登录态保留 userdata，005 断点不受影响**）；功能地图 v2-draft → **v2 正式**（新增"探索边界标注"节 + 变更记录）；qa-reporter 轮次报告生成中（results/SWAN-20260910-001-feature-boundary/report.md，**报告复核通过前不外发、不提单**）。
> - **移交下一步（第二步·建站）**：数据原料=功能地图 v2 + states-matrix + 轮次报告 + explorer_output 快照；建站需求见下方"建站预留记录"。部署方式待与用户讨论。
> - **待裁决池（下一轮测试或报告定级时处理）**：软件升级点击、账号绑定管理、用户反馈新建表单、消费明细财务只读、F-2 服务端核对。
> - **005 登录轮断点不变**：登录态已在探索中重建（有效会话），恢复 005 时从 POS-002 断言补证起步，凭据见 05g。

> ## 🔄 （已收口）活跃任务：SWAN-20260910-001-feature-boundary（2026-09-10 开工）
> **用户两步走指令**：第一步=功能边界探索完成功能地图（无需深入测试，非致命 BUG 绕过）；第二步=本地建站→部署→测试结果同步更新（未开始）。
> - **并行双线已派发**：A 线 qa-archaeologist 代码解析（路由总表→20 模块核对→104 条未考古裁决），B 线 qa-executor 模拟器探索首片（登录前区域：预调→启动首屏→隐私同意→登录页采集）。
> - **任务卡**：`plans/010-feature-boundary/010-card-{archaeologist,executor}.yaml`；结果目录 `results/SWAN-20260910-001-feature-boundary/`。
> - **设备**：emulator-5554 已换绑本任务（005 登录轮保持暂停断点不变），00c 已回写；宿主机内存已升级 31.7G（可用 9.4G，舒适档通过）。
> - **基线核实**：App dev@4d1ed7b / Core dev@402853a，与功能地图 v1 记录一致。
> - **颗粒度升级（2026-09-10 用户指令，已推送执行从+固化任务卡 v2）**：页面状态矩阵——键入区四态（empty/filled/error/normal-focus）、组件联动显式记录、可点击区点击响应；证据命名 `<页面>__<功能区>__<状态>.png`；states-matrix.md 登记。分批按模块推进，每片 ≤3 单元。
> - **A 线完成（2026-09-10）**：qa-archaeologist 代码解析完毕，功能地图升级 **v2-draft**（412 行）。104 条未考古裁决：96 已考古-L1 / 4 保持未考古（AI 网关、AI 联动、Vision 数据层、固件升级——行为级深考古域）/ 4 边界修正；4 条发现-未确认全部转正；**新增 24 条功能点**；路由总表实测 125 条。**6 条疑似缺陷仅记 notes**：5 条死路由（/main、/main/home、/music_platform/vip、/vip/pay、/manage-one）、推送 Port 为 no-op 空实现（消息中心用例不可依赖真推送）、/search 与 /main/search 双路由同页。产物：`01-系统认知/功能地图.md` + `results/SWAN-20260910-001-feature-boundary/archaeologist/`。
> - **B 线片 1 完成（2026-09-10，3/3 🟢）**：登录页状态矩阵 27 张采证（键入区四态+联动组合）。三条联动已证实：①协议勾选同时控制下一步+第三方图标；②按钮启用只校验位数≥11 不校验号段，非法号段→行内红字（login_error_text，无 toast 不发码）；③密码模式眼睛图标无独立 resource-id（点 917,1043）。**绕过记录**：A-1"Swan Audio没有响应"ANR ×3（触发点=文本输入，dropbox ErrorId 7101afa5，是 P-003 候选 BUG 的证据增强；录屏编码是放大器，已改交互期停录屏）；O-5 微博按钮点击无响应待复核；O-3 键盘不渲染；O-6 input text 快连丢字符；T-1 device-speed-prep.ps1 PS5.1 BOM 解析失败（待修复）；O-4 归属地列表行零语义标签待终判。环境坑位已存 executor agent-memory。**片 2 已续派**（归属地测绘+密码模式矩阵+O-5/O-3 复核，免登录）。**片 3 需验证码**（人工中断点：优先 acct-swan-mobile 短信回读）。用户已知晓 scrcpy 镜像≠第二台虚拟机。
> - **B 线片 2 完成（2026-09-10，3/3 🟢，累计证据 ~70 文件）**。**缺陷候选（证据齐、未定级、未提单——提单属不可逆动作等用户确认）**：F-1 微博第三方登录点击即崩（UnsatisfiedLinkError libwind.so 缺失，UMShareAPI→微博 SDK loadLibrary，疑似 100% 复现，完整栈 crash-weibo-fatal-stack.txt；对照微信不崩仅行内报错）；F-2 密码框无前端长度校验（6 位即启用登录键，点击后主线程 ANR 循环 ErrorId 57f0fd98 只能 force-stop；**登录请求是否已发出未确认，是否需服务端核对待用户裁决**）。**O-4 终判更正**：归属地列表行有完整 content-desc 语义（片 1 系 grep 只查 text= 的疏漏，已撤销）；235 行国家清单+A-Z 索引条（无 X 段）；索引条点击穿透选行、拖拽才跳段（交互发现）。**隐私/使用政策两链接疑同一 URL**（network.hivi.com/privacy，Web 域待复核）。**规程修订（已采纳执行）**：scrcpy 实测是 ANR 放大器（media.swcodec ~50% CPU，本轮 4 次 ANR 均在挂载期间）——本任务默认不挂 scrcpy（宪法可见性规则的框架级修订待用户批准）；逐字符输入≥0.5s 间隔；ANR 预案=等待×1→force-stop 冷重启。**片 3 等验证码协调**（人工中断点，等用户选择：短信回读自动 / 人工给码）。
> - **BUG 库落档（2026-09-10 用户批准）**：F-1/F-2 已写入本地 BUG 库——`SWAN-BUG-20260910-001`（微博登录点击即崩，libwind.so 缺失）、`SWAN-BUG-20260910-002`（密码框无长度校验+点击 ANR，服务端核对留待定级阶段）；模式库新增 P-004（第三方 SDK 原生库缺失类）、P-003 次数升 2 并更新反哺动作；-004 候选报告补证据增强节。**宪法修订 v1.3 已入 CLAUDE.md**：scrcpy 默认不挂（ANR 放大器实证），仅 BUG 取证/用户要求时挂。两条 BUG 均未定级未提单（提单前须 qa-reporter 定级+主对话复核+用户确认）。
> - **片 3 已续派（2026-09-10，人工给码模式）**：用户裁决密码链路不可用（F-2 未走通）走短信；短信号已由用户会话内提供（**明文不入任何文件**，05g 别名 acct-swan-mobile 对应的新号），执行从流程=输入号码→发码→⏸收码点暂停→主对话向用户要码转发→登录→仅 AppShell 首屏测绘（后续 Tab 分片）。
> - **片 3 完成（2026-09-10，4/4 🟢，登录成功，零 ANR）**：短信链路全通（人工给码模式）；验证码页矩阵入库——**4 格输入非 6 格、第 4 位自动提交无提交按钮**、明文显示完整手机号（O-8 隐私观察留报告层裁决）、重发倒计时未捕获；O-7 发码后跳转反馈慢（t+3s 无反馈 t+60s 到位，自动化需轮询）。AppShell 首屏 9 功能区测绘完成（频道条/搜索栏/平台捷径×5（QQ网易酷狗已授权✓，Apple Music/Qobuz 灰置）/我喜欢 2317 首/歌单/小薇 AI 入口/最近播放/播放条/四 Tab）。**v1.3 规程实证：不挂 scrcpy 全程零 ANR**（对照片 1/2 挂载期 4 次）。登录后无权限弹窗。**片 4 已续派**（tab_me 测绘；退出登录入口只定位严禁点击——登录态是后续分片生命线）。片 5+ 候选池：四 Tab 各模块、小薇 AI 单独一片、播放功能涉音响实体需人工 checklist。
> - **片 4 完成（2026-09-10，3/3 🟢，登录态完好）**：tab_me 12 功能区+9 入口全落证；**危险区已定位未点**——注销账号 person_info_cancel_account_button 紧邻退出登入 person_info_logout_button（均在 person_info_page 末位，§18 已标禁区）；音质设置=底部弹层非跳页；设备管理子页有空态实证。新观察：O-9 扫一扫点击无稳定新页待复核；O-10 SWAN收藏子页 dump null-root（子页自动化只能坐标定位）；**O-11 版本标识落点=关于页"5.3.0 (build 32) debug-test"（建站版本标识需求可直接引用）**；O-12 关于页有协议第二入口可与片 2 同 URL 疑点对照。**片 5 已续派**（tab_platform：授权↔入口启用联动+三平台首屏；播放全程绕开涉音响实体）。**待用户裁决池**：新建歌单（写操作）、检查更新点击、充值消费记录只读边界、O-9 复核方式。
> - **片 5 完成（2026-09-10，3/3 🟢）**：tab_platform 6 功能区+6 平台行全测绘。**授权联动矩阵完整**：已授权行=灰底+−钮（取消授权=禁区）+行体点详情页；未授权行体无响应，引导仅由+钮触发且**样式因平台而异**（Spotify=底部下载引导弹层、Apple Music=居中红弹窗、Qobuz 被播放条遮挡未测）；**网易云金底+VIP 角标=会员等级视觉维度**（授权态之外的新维度）。三平台详情模板**非统一**（O-13：QQ音乐独有投放钮/网易独有播客项/酷狗独有歌手推荐）——自动化锚点须按平台分别维护。O-14 闭合：Spotify 入口=平台页音乐段第 4 行。惠币数值属敏感数据报告引用须脱敏。**片 6 已续派**（tab_device 最后一个主 Tab：空态样板+配网入口，不真配对）。待裁决池不变（新建歌单/检查更新/财务只读/O-9）。
> - **模拟器重启（2026-09-10 12:56，用户批准）**：宿主窗口显示异常（内容裁切放大、非设备端问题——adb screencap 全页正常、无障碍放大关闭；系 qemu 窗口缩放状态卡死，Ctrl+滚轮/工具栏缩放按钮均无效）。优雅关机（emu kill 存快照）→ Quick Boot 5 秒恢复。**重启后自检全绿**：前台 MainActivity、tab_me 在（登录态保持）、dump 正常、窗口 427x770 比例正常。执行从已通知并待命。**运维经验：qemu 窗口缩放卡死唯一可靠修法=优雅重启**（宿主侧无损，Quick Boot + userdata 登录态均保持）；已排除的路径（宿主 SendKeys 缩放/工具栏/滚轮/Extended Controls）勿再尝试。
> - **片 7 完成（2026-09-10，3/3 🟢）**：首页频道条**三重联动**实证（内容区+搜索栏 placeholder+背景色随频道切换；播放条/四 Tab 恒定；**频道状态跨 Tab 保持**——自动化操作前必须先确认当前频道）；可视音箱频道=功能不可用空态样板；O-9 闭环：扫一扫响应正常（相机权限弹窗→扫码页；模拟器"相机不可用"错误态=虚拟相机无视频流的**环境限制非缺陷**，真机预期正常）；小薇=**独立全屏 AI 聊天页**（头部+问候区+输入框+Swan 悬浮球）。**T-4 事件**：U1 通配清理波及 005 轮 /sdcard 录屏残留 15 个——逐一核对 F 盘归档全在，**无证据损失**，实际完成积压清理；教训已固化：共享设备存储禁用通配删除。**片 8 已续派**（person_info 深测绘——注销/退出双按钮禁区、帮助反馈 4 子项、关于升级+O-12 协议同源对照；检查更新严禁点击）。
> - **片 8 完成（2026-09-10，3/3 🟢）**：person_info 7 功能区全锚点（手机号只读态实证；头像/昵称/密码/绑定管理=4 写操作链路识别未点；**注销/退出双禁区零触碰**）。**O-12 实证闭合：全部 4 个协议入口同指 network.hivi.com/privacy（空白未部署；/terms 404 佐证使用政策无独立页）——候选问题移交报告层**。帮助反馈：使用说明 8 主题与 App 功能结构高度对应（O-21，可作功能地图交叉验证源）；常见问题有 EN 语言切换（O-20 i18n 维度新发现）；可适配音箱型号=远程内容加载慢（O-19）。软件升级行未入语义树+禁点维持（待裁决）。事件：双返回误退桌面 1 次无损恢复（教训：子页返回逐级 dump 验证）。**片 9 已续派**（搜索主链路+电台深一层+设置入口定位——补完功能边界最后 5 个未触模块中的 3 个；切服严禁操作）。执行从判断素材已饱和，片 9 后评估进地图更新+报告阶段。
> - **建站预留记录（用户 2026-09-10 指令：信息一次采全，缺失再跑一轮要问责）**：第二步建站必须覆盖 ①页面状态矩阵的交互化展现（状态切换器、联动关系可视化）②版本 update log 看板 + 版本标识 ③死路由/边界外条目要在站上有显式标注 ④A 线 6 条疑似缺陷 notes 进详情页 ⑤深考古域 4 条标记为"行为级待深挖"导航占位。
> - **已知待协调**：登录后区域探索需要验证码（人工中断点已预声明：优先 acct-swan-mobile 短信回读，失败向用户收集）。
> - **功能地图富化需求（第二步建站范围，用户已确认方向）**：版本 update log 看板 + 版本标识 + 历史版本回看；页面快照/功能区像素/交互/键入区/ICON 等探索富信息；前端 UI 升级（深色默认、三栏工作台、状态徽标）。部署方式待与用户讨论。

> ## ⏸ 005 登录轮断点（暂停中，未废弃——恢复时优先读本节）
> 1. **首片已派**（v1.1 分片）：新 executor 领 POS-002 + POS-004 + MERGE-02 三单元；它状态复核发现**上次登录实际已成功**（shared_prefs 真实 JWT userId=226、AppShell 已渲染用户数据），但 POS-002 关键断言无证据。
> 2. **主对话已裁决 A**：pm clear 完整重跑（授权销毁 userId=226 会话）→ 重过隐私同意（准备步）→ POS-002 全断言重跑（新收码点）。**pm clear 已执行**；强停时 App 画面疑为旧进程残影（"画面仍显示登录态首页"），明日开工先复核实际存储/窗口状态。
> 3. **设备已释放**：emu kill 收工，内存 0.9G→5.5G；00c 已回写关机（空闲）。明日开机 **Quick Boot 即可**（config 变更后冷启动已做过一次）。
> 4. **明日恢复序列**：开机预检（00c 硬规则：可用 ≥5G）→ 00c 登记占用 → Quick Boot 开机 → spawn 首片 executor（短信组收口 3 单元；号码明文 131****5234 届时会话内随片下发）→ 复核 App 实际状态 → 隐私同意准备步 → POS-002 收码点（用户回读）→ 片间 SendMessage 续派同一 executor → 全部 ⏳ 单元收口 → qa-reporter → 主对话复核三问 → 禅道提单检查点。
> 5. 风险备忘：宿主内存紧张时段（<5G 可用）不得开工；设备命令一律 30s 超时 + 弃片条款兜底。

> ## ⚡ 框架 v1.1 变更通知（登录会话恢复时必读）
> 用户已暂停登录轮做框架调整，以下规则**立即生效**，恢复执行时按新规则跑：
> 1. **分片执行**：executor 每次只领 ≤3 个执行单元，片间回报红绿灯，主对话循环续派（宪法"分片调度"）。
> 2. **设备命令强制超时**：adb/maestro/uiautomator 全部带 30s 超时，超时标 `BLOCKED(tool-timeout)` 转下一步，禁止干等。
> 3. **可见性**：UI 用例执行前确认模拟器有窗 + 开 scrcpy 镜像；每片开跑即分段录屏（180s）。
> 4. **人工中断点协议**：任务卡 `human_interruption_points` 预声明；执行中遇到即停下回报，主对话向用户收集后续派；人工输入尽量派发前收齐。
> 5. **Maestro 防 flaky 规范**已入 `02-L2功能.yaml` automation_guidance（text>id 选择器、轮询断言禁 sleep、retryTapIfNoChange）——新写/重写自动化步骤时遵循。
> 6. **分片升级 v1.2·恢复续跑**：同一批次内 spawn 首片后，后续片用 SendMessage 恢复同一 executor（上下文保留）；恢复时先重读 progress.md 对齐磁盘。progress.md 是事实源。
> 7. **提速预调**：每个执行会话首个 UI 用例前先跑 `E:\SwanApp\scripts\device-speed-prep.ps1`（关闭系统动画+保持唤醒）；模拟器开机默认 Quick Boot，仅配置变更后冷启动一次。
>
> 恢复登录轮时：按下方断点续跑，重派 executor 从 POS-002 起，**首片建议 = 短信组收口 3 单元**（收码优先用 acct-swan-mobile 短信回读，避免人工等待）。

## 2026-09-07 登录模块轮（SWAN-20260907-001~005）——用户暂停做框架调整，断点如下

- **进度**：001 考古完成（模块卡片-login.md）→ 002/003 双从用例完成（正向 14 + 逆向 33 含 NEG-TOKEN-003）→ 004 合并（40 执行单元 + 6 跨通道合并，产物 `results/SWAN-20260907-004-login-merged/`）→ 005 执行 PARTIAL：🟢2（POS-001、NEG-PRIV-002）/ 🔴1（NEG-PRIV-001 不同意不退出，suspected-defect）/ 🟡18（credential-required 4、tool 8、env 7）/ ⏳19。执行从已停，App 疑似掉桌面（恢复时先复核）。
- **用户三项裁决**：① 全量推进（前置缺失记 BLOCKED 不等齐）；② G3 token TTL 本轮补用例（NEG-TOKEN-003 已补）；③ 执行过程录屏（adb screenrecord，单段 180s，落 evidence）。
- **用户两次纠错（已固化）**：① token 失效类用例硬前置=先真实登录建立有效会话再注入/篡改，空 token 态重现无效记 BLOCKED（NEG-SESS-001~005、NEG-TOKEN-001~003 precondition 已修订）；② （隐含）验证码时效管理——旧码作废须重发。
- **环境事件**：宿主机 OOM（用户已清理）致模拟器 SystemUI ANR → QEMU 崩溃退出 2 次 + 渲染故障 1 次；已冷启动 swan-qa（-no-snapshot-load）并健康检查全绿。ADB UI dump/输入挂起有前科（005 轮亦发生），唤醒-观察哨-强停重派的处置链路已验证有效。
- **凭据变更**：05g 新增别名 acct-swan-mobile（短信回读，明文仅主对话会话内传递，不入库不入仓）；acct-qq-music 明文仍未确认；`G:\SwanApp-Data\test\credentials\` 目录不存在。
- **恢复入口**：读 005 执行任务卡 `plans/007-login-cards/007-card-executor.yaml` + `results/SWAN-20260907-005-login-execution/progress.md`（40 单元红绿灯 + BLOCKED 清单 + 纠错记录全在）→ 重派 qa-executor 从 POS-002 收码点续跑（号码明文需主对话会话内传递）→ 顺序：短信组收口 → 会话/token 组（按新前置）→ NEG-ANR-001 最后 → qa-reporter。
- **环境验证遗留**：SWAN-20260907-000 已验证测试服 `http://8.129.106.82/api` 发码+登录契约；JWT 有效期整 10 年（exp=iat+315360000s）作安全议题随报告上報。

## 2026-09-07 Claude Code 迁移部署

- 平台迁移：工作流载体由 Codex 迁移至 Claude Code（VS Code 扩展，主入口）。AIQA-MiaoYu 上游（RavenWangChina/AIQA-MiaoYu）克隆归档于 `F:\SwanApp-Toolchain\archives\aiqa-miaoyu-upstream\`。
- 已部署：主对话宪法 `F:\SwanApp-Toolchain\CLAUDE.md`（上游宪法 + 本地治理合并，路径指向 `docs/qa-knowledge/` 与 `templates-v2/`）；五个从对话 `.claude\agents\qa-{archaeologist,case-positive,case-negative,executor,reporter}.md`（各含本地知识库路径锚点）。
- **全局化改造（按用户 VS Code 插件主入口习惯）**：五从对话同时部署到全局 `C:\Users\swan\.claude\agents\`（含绝对根锚点，任意工作目录可用）；全局记忆 `C:\Users\swan\.claude\CLAUDE.md` 建立 QA 工作路由（开工先读宪法与 session-state，含 E/F/G 分层与环境事实）。F 盘部署保留，作为以该目录为工作区时的原生加载。
- 已实例化：`03-BUG库/模式库.md`（P-001 契约不同步 / P-002 嵌套包依赖边界 / P-003 启动时序 ANR，种子来自 001-004 号 BUG）。
- 已注册：禅道 MCP 至 Claude Code（`~/.claude/settings.json`，npx zentao-cli mcp）；**Git MCP 已连通**（`F:\SwanApp-Toolchain\mcp-server-git\venv\Scripts\mcp-server-git.exe`，mcp-git 1.29.1，12 工具，2026-09-07 注册并实测 git_status 通过；Codex 时期的握手 BLOCKED 确认为 Codex 侧问题，服务本身无故障）。相关仓库已加 git safe.directory 白名单（F:\SwanApp-Toolchain\docs、archives、E:\SwanApp\repos 下 7 个检出）。
- Maestro 确认已在用户 PATH（此前 session-state 记录过时，更正）。
- 部署自检：`docs/workflow/qa/selfcheck-claude-deploy.py` 全绿（0 失败 0 警告，2026-09-07）。
- 更正记录：Codex 的 memories_1.sqlite 为空，历史状态全部以本文件与 docs 文档为准；Codex 侧固定/临时会话链路问题不再跟踪（Claude Code subagent 无此问题）。
- 下一步候选：新会话冷启动验证（复述八步编排+三类检查点）；禅道 MCP 连通验证（拉一条真实工单）；然后承接遗留项（ANR 复现、Phase2 intake SOP、模块17 locator contract 闭合）。

- 证据采集工具链补全（2026-09-07）：qa-executor 定义（F 盘+全局）固化证据命令速查（screencap / screenrecord / scrcpy --record / maestro record / logcat+dropbox），BUG 复现纪律"先开录屏再复现"；scrcpy 4.1 经 winget 装机（当前进程 PATH 未刷新，新 shell 生效）；BUG 报告模板本就含"截图/日志/录屏路径"字段，报告层无需改动。

## 2026-09-07 框架审计与九项完善（主对话·运维会话）

- 审计结论（用户确认）：高风险 3 项（03c BUG 状态机 / 05e 回归触发 / intake 三源）**先经流程测试验证再完善**——流程测试方案：禅道 MCP 活动后走一次完整 BUG 生命周期演练（本地 BUG → 提单测试产品 → 状态回流 → 回归触发 → 关闭）。
- 已完善：④严重级改 S1-S4（模板+命名规范，与测试级别 L1-L4 严格区分；存量报告不回改）；⑤`metrics-rollup.py` 自动汇总并写入 00-索引 度量看板（METRICS 标记块）；⑧`baseline-gate.py` 基线/证据门禁（已实测，正确拦截 005 缺 summary.yaml）；⑨05f 审计日志实例化并写入宪法第 8 步；⑩03d flaky 表实例；⑪接口清单/架构总览骨架实例；⑫05g 凭据清单实例（禅道密码明文于 settings.json 登记为已接受风险，建议换 token）。
- 证据采集补全：qa-executor（双份）固化证据命令速查（screencap/screenrecord/scrcpy --record/maestro record/logcat+dropbox），纪律"BUG 复现先开录屏再复现"；scrcpy 4.1 已装。
- 待办（流程测试后）：03c/05e/intake 完善；音频客观指标与视觉断言（Midscene）工具选型需用户参与决策。

## 2026-09-07 SWAN-20260907-002-avd-repair（虚拟机修复 + 实机准备）

- swan-qa AVD 配置修复：GPU disabled→host、RAM 4G、heap 256M、1080×1920@420dpi（原 320×640 软渲染配置严重不达标，是 ANR 重大嫌疑；备份在 results/SWAN-20260907-002-avd-repair/config.ini.bak）。
- **占用事故**：本任务与登录测试会话双驱动 emulator-5554，13:15-13:18 爆发 19 条系统级 ANR（system_server 阻塞 15s），判定为争抢产物不计业务失败；探测方已退避。**规则生效：两会话开工前必须先查 00c 占用表**。
- 新增实例：`docs/qa-knowledge/00c-设备池清单.md`（设备台账 + 占用规则 + 事故表 + swan-qa 修复后参数）。
- 新增文档：`docs/runbooks/real-device-onboarding.md`（实机接入 SOP：预置/连接/保真度实测/登记/占用纪律/首轮验证）。实机预计 2026-09-08/09 到达，已在设备池预登记"待接入"。
- adb platform-tools 已入用户 PATH。
- 待复核：AVD 修复对 ANR 的实际效果需在设备池空闲窗口做单任务启动探针；GPU host 若渲染异常回退 swiftshader_indirect。

## 2026-09-07 SWAN-20260907-001-login-archaeology（qa-archaeologist）

- 登录模块只读考古完成：基线 App `dev@4d1ed7b` / Core `dev@402853ab`（实测确认，与任务卡一致）。
- 产出：`01-系统认知/模块卡片-login.md`（接口契约、token 三处存储、无 refresh、登出 4 触发点、11 已知坑、5 未决）；证据 `results/SWAN-20260907-001-login-archaeology/`。
- 未修改源码/用例库/BUG库；00-索引.md 模块清单已更新（卡片 4 张）。
- 关键未决：区号接口为外部 MXNZP 依赖（硬编码凭据）；token 明文 SharedPreferences 且冷启动不校验；扫码登录（pad）是否纳入 login 用例范围待主对话裁决。

## 当前状态快照（2026-09-04 Codex 时期，待迁移后复核）

- 当前阶段：Phase1.3 收口完成，进入 Phase2 intake polling/SOP 与 Phase3 执行准备；本轮完成 MCP/Git 状态核验，仅更新文档，不执行测试、不修改业务源码。
- 模板规划：`F:\SwanApp-Toolchain\docs\workflow\qa\templates-v2\` 作为 QA 模板域，承载首批 29 个模板（00-05）；路径符合知识环规划。
- 知识库根：`F:\SwanApp-Toolchain\docs\qa-knowledge\`；已存在 `flutter-vertical-workflow-20260903.md`。
- 角色边界：05a 任务卡内嵌考古/正向/逆向/执行/报告五角色 variant，可承接专项任务职责与禁令，确认采用。
- 最近完成：`SWAN-20260904-002-core-defect-triage` 只读分诊矩阵已归档。
- 本轮完成：`F:\SwanApp-Toolchain\docs\workflow\qa\task-split-rules-v1.md`，定义三源 intake、05b 拆分、L1-L4 双通道、依赖拓扑与并行约束。
- 本轮完成：模块17搜索的考古、正向、逆向三张独立任务卡；正向/逆向卡互盲，分别遵循 02-L2 与 02k 字段。
- 本轮完成：模块17搜索合并清单 `F:\SwanApp-Toolchain\results\SWAN-20260904-003-search-merged\merged-cases.yaml` 与覆盖缺口 `coverage-gaps.md`；保留 14 个 case ID 与三源产物路径。
- 本轮摘要：`F:\SwanApp-Toolchain\results\SWAN-20260904-003-search-merged\summary.yaml`，状态为 `merged_not_executed`；locator contract 仍待确认。
- 本轮决策：`SWAN-20260904-003-DEC-001` 将模块17 `NEG-CONCURRENCY-001` 的执行策略固化为 `latest-wins`；运行证据待 Phase3。
- MCP 状态（2026-09-04）：配置文件登记 7 个服务（含 `git`、`git_core`）；Git MCP 可执行文件存在，但当前会话未暴露可调用的 Git MCP 工具，判定为 `BLOCKED`（握手/工具暴露层）。
- Git CLI 状态：`HiVi-Network-FlutterApp` `dev` HEAD 已确认为 `4d1ed7b1d727f12906d6ac9fa9ed195966e464b3`；工作树保留既有 `analysis_options.yaml`、`pubspec.lock` 修改。该状态不受 Git MCP 阻塞影响。
- 最近验证基线：Core `dev` @ `402853ab964f026761ba63130f495b9d213ea8b5`；App `dev` @ `4d1ed7b1d727f12906d6ac9fa9ed195966e464b3`。
- 质量门禁：App L1/L2 已通过；Core 仍有 328 条 analyzer diagnostics、43 个测试失败，Core APK/全链路门禁保持阻塞。
- 会话通道：固定会话链路问题仍暂缓，当前按临时任务通道执行；不将会话基础设施问题归类为业务测试失败。
- 路径约定：`E:\SwanApp` 为代码与脚本根；`F:\SwanApp-Toolchain` 为工具、文档与结果根；`G:\SwanApp-Data` 为临时/生产/过程数据根。

## 待办

- `SWAN-20260904-005-search-execution`：模块17搜索 L2 双通道执行当前 `BLOCKED`（`device-required`）。`adb devices`、包/Activity 检查通过；ADB UI dump 曾挂起，Maestro hierarchy 探针捕获 `Swan Audio isn't responding` ANR 对话框，搜索页面不可达。Maestro 位于 `C:\Users\swan\maestro\bin\maestro.bat` 但未入 PATH。证据：`F:\SwanApp-Toolchain\results\SWAN-20260904-005-search-execution\`。
- 下一步（依赖解除后）：恢复 ADB UI shell/截图链路，定位搜索入口并关闭 `locator_contract`；确认 Maestro CLI 后执行 6 个正向 + 8 个逆向 L2 case。不得将本次环境阻塞登记为业务 BUG。
- 005 复核补充：`evidence/anr-recheck.png` 已保存；Maestro hierarchy 现可达登录页（仅登录 locator），搜索 locator contract 仍未确认。14 个 L2 case 均 `BLOCKED`，进度见 `results/SWAN-20260904-005-search-execution/progress.md`。新增 ANR 候选记录 `03-BUG库/SWAN-BUG-20260904-004-app-anr-candidate.md`，不计入业务失败。

1. 外部部署并校验 `templates-v2` 首批 29 个模板及其版本元数据。
2. Phase2 建立 `git-poll`、`zen-poll` 与人工 intake SOP，并将事件转换为标准化 intake。
3. 先闭合模块17正向 `locator_contract`，再审批执行环境与合并清单。
4. Phase3 分别调度正向/逆向执行卡，使用独立证据目录与 Flutter 全局互斥；优先验证 `latest-wins`。
5. 将 05a 五角色边界随执行任务卡下发，并在后续任务卡中记录实际 variant。
6. Phase3 处理覆盖缺口 G3/G4/G5/G6/G8；Core 仍按 `CORE-T1` 至 `CORE-T6` 依赖顺序推进。
7. 每轮结束回写本文件与 `00-索引.md`，记录当前任务、下一步、未决事项和各库状态。

## 未决事项

- 固定会话链路何时恢复，以及是否继续使用临时从对话通道。
- Core 43 个失败项中平台 stub 与时序项的最终归因，需在修复任务中隔离复现。
- 模板 v2 外部部署完成时间及其首个可用版本号。
- Git MCP 握手恢复时间；恢复前使用本地 Git CLI 做只读仓库操作，不宣称 Git MCP 已连通。

## 2026-09-09 SWAN-20260909-001-feature-map（功能地图 + 插件）

- 功能地图 v1 完成：01-系统认知/功能地图.md，18 功能域 / 123 功能点（[已考古]7 / [已扫描-未考古]104 / [发现-未确认]3 / 待测绘清单 12 项）；00-索引 已登记（考古从误加的过时 login 重复行已由主对话清理）。
- VS Code 便携版已装 gera2ld.markmap-vscode v0.2.11（markmap 官方）：知识库 md 可渲染为交互思维导图，auto 模式生成同名 svg/html。用户需 Reload Window 激活。
- 导出产物：G:\SwanApp-Data\exports\qa-knowledge-export-20260909.zip（知识库全量快照，无凭据明文，SHA256 已登记）。
- 登录轮（SWAN-20260907-005）暂停中：片 2 执行从因会话重启丢失完成记录，progress.md 显示 POS-002/004、MERGE-02 已收口、NEG-TOKEN-001/002 有预观察；NEG-SMS-002/MERGE-01/NEG-SMS-005 及会话侧单元待续（progress.md 为事实源）。
