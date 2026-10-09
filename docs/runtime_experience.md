# 运行时经验知识库（子 Agent 执行经验沉淀）

> 按编排约定，子 agent 返回 [完成] 后由 orchestrator 把新验证的 AW 方法 / 新坑追加到对应表格，供向量检索注入。
> 记录格式：场景 / 正确做法 / 来源与日期。

## Swan 项目（flutter）

| 场景 | 正确做法 | 来源 |
|------|----------|------|
| 发送验证码 | 点"下一步"（`login_submit_button`）即自动发送，页面无"获取验证码"按钮 | explorer 2026-09-08 |
| 验证码输入 | 4 位填满自动提交，无需点确认；等 `tab_me` 出现判成功 | explorer 2026-09-08 |
| 取码链路 | App 触发后 `GET <SWAN_OTP_GATEWAY>/api/test/otp/latest?phone=` 取码；开发接口为 `https://testnetwork.hivi.com/api/user/captcha/mockCode`（必须带 api 前缀） | orchestrator 2026-09-08 |
| 拿未登录态 | 杀进程无效（登录态持久）、OPPO 禁 pm clear；唯一途径：我的→个人信息→退出登入 | element 2026-09-08 |
| 测试账号边界 | 自动化只用基线测试账号 13555555555（OTP 白名单内）；**18946151218 是一次性演示账号，禁止任何自动化登录/登出**（白名单不含，退出不可逆）；draft 差分记录中该账号的个人数据均为示例值，禁作断言期望 | orchestrator 2026-09-15 |
| 自定义内容区不断言 | 平台授权行副文案（平台昵称）、家庭名/成员昵称、自建歌单/分组名、用户曲库歌曲行、头像/封面、惠币余额——全部是**用户自定义或服务端动态内容**，任何账号下都只断言结构/元素存在（如"授权行存在副文案"、"[−]图标存在"），**禁止硬编码具体值作期望**（昵称会改、歌单会删、余额会变） | orchestrator 2026-09-15 |
| 登录页"下一步"图 | `swan_下一步按钮` 模板是置灰态，仅作存在性断言；点击一律走 key `login_submit_button` | element 2026-09-08 |
| 新建歌单弹窗 | `press_back` 关不掉（09-10 实测：一次不关闭且弹窗整体下移，推翻 09-08"两次返回可关"旧结论）；须点右上关闭按钮 `SWAN_PLAYLIST_NEWDLG_CLOSE_BTN` | verify 2026-09-08 + explorer 2026-09-10 Wave2 合并 |
| 音质弹层关闭判定 | 不能用"音质设置"文案判（列表项同名），判 OCR"流畅音质"/"完成"消失 | verify 2026-09-08 |
| 设备卡定位 | key 按设备 UUID 动态拼接：`wifi_device_card_<UUID>`，用前缀匹配 | explorer 2026-09-08 |
| 密码页 press_back | 只收键盘，不退出 App（验证码输入页的 press_back 才会退出） | codegen 2026-09-08 |
| 密码错误提示 | 是常驻语义节点 `login_error_text`（content-desc"密码错误，请重新输入！"），不是 toast，可直接 key 断言 | codegen 2026-09-08 |
| 登录页脏表单 | 提交失败后已填文本+协议勾选态残留；盲点勾选框会把已勾选态反选导致提交按钮置灰。重跑前重启 App 重置（登录页无状态持久化） | codegen 2026-09-08 |
| 统一登录入口 | `user.login()` 默认从 `SWAN_PHONE` / `SWAN_PASSWORD` 取凭据走密码登录；`method="sms"` 走验证码。须从登录页或有底部导航的页面调用；未登录时重启清理表单，已登录时复用会话回底栏首页，不校验账号身份或切号。验证码输入页出现后才取码 | codegen + verify 2026-09-19：12 项单测与用户代理验证通过，尚未真机验证 |
| 输入取证含敏感内容 | 现有 `AWBase.input_text` 将输入原文传入 `step_evidence.record`；启用 `EVIDENCE=1` 时密码也会进入截图标注。取证层脱敏尚未实现，须在框架层处理，不能将业务入口视为已脱敏 | orchestrator 2026-09-19：代码审查（未使用真实凭据） |
| 输入框复用 | 登录类输入前先 `clear_input()`，避免上一轮残留 | codegen 2026-09-08 |
| 我的页滚动位 | 从帮助/关于页返回后页面停在滚动位，`me_user_profile_entry` 离屏不在语义树中；判该 key 前先 swipe_down 复位 | verify 2026-09-08 |
| 危险入口 | `person_info_cancel_account_button`（注销账号）紧邻退出登入，⛔ 任何自动化禁止点击 | explorer 2026-09-08 |
| 真实音箱安全 | 播放/音量/同步/授权/充值类按钮只做 image_exists，不下发点击 | 编排约定 2026-09-08 |
| 修改密码页 FLAG_SECURE | 该页防截屏：`adb screencap` 返回空、OCR 0 项，离开即恢复；禁止对该页截图/OCR 断言，"截图失败"本身可作页面判据 | explorer 2026-09-10 |
| `logout_if_needed()` 误判 | 在个人信息页会静默跳过（`tab_me` 不可见即视为未登录）；须先 `press_back` 回我的页再登出 | explorer 2026-09-10 |
| 首页顶 Tab 持久化 | 顶 Tab 选择跨底栏切换、跨登出/登录持久，`go_home()` 不重置；要稳定进推荐 Tab 必须显式 `click_text("推荐")` | explorer 2026-09-10 |
| uiautomator dump 瞬时失败 | 页面动画中 dump 只返回 1-2 个节点，重试即可（3 次内置重试） | explorer 2026-09-10 |
| 个人信息页行可点性 | 手机号行是非 clickable View（点击无反应）；昵称/密码行 clickable 状态以 raw dump 为准（时序可能不显示） | explorer 2026-09-10 |
| 昵称编辑页返回 | `press_back` 需两次（收键盘+返回）；头像弹层点 OCR"取消"关闭 | explorer 2026-09-10 |
| 短文案 OCR 歧义 | "AI"等短文案在页内多处出现（顶 Tab y≈121 vs 页内 y≈737），用 region 限定区域提高鲁棒性 | explorer 2026-09-10 |
| 扫一扫权限弹窗 | 首次进入触发系统相机权限；用 `permission_allow_one_time_button` 最小授权 / `permission_deny_button` 断言不进页 | explorer 2026-09-10 |
| 顶 Tab 选中态判定 | 选中 Tab 文字近黑（暗像素≈1000），未选中灰（≈0）；顶 Tab 截图一律取未选中态（`SWAN_HOME_TAB_*`），交叉匹配选中态仅 0.48-0.67 不会误命中 | element 2026-09-10 |
| 推荐 Tab 内容（勘误） | 推荐 Tab = 音源卡+我喜欢/歌单/AI+最近播放（与 09-08 首页 dump 一致）；音乐 Tab = 歌单宫格；电台 Tab = 全国电台。09-10 element 记录的"推荐与电台内容相同"系顶 Tab 持久化陷阱下的误读（采集时实际停在电台 Tab） | explorer 2026-09-10 Wave2 勘误 |
| AI 角色设置入口 | 实为「添加更多AI角色」右侧的图标按钮（无文案，OCR 不可用），图模板 `SWAN_HOME_AI_ROLE_SETTINGS`；实测落地「所有角色」页（系统角色+自定义区） | element 2026-09-10 |
| 区号行防误匹配 | 区号页"中国"两字会模板匹配到"中国香港"行首；`SWAN_AREA_CODE_CHINA_ROW` 必须含行尾 +86 的整行裁剪（港澳台行交叉得分 0.61-0.67） | element 2026-09-10 |
| 完成按钮双义 | 资料编辑页昵称输入态下顶栏"完成"与 IME 键盘右下"完成"同文案；`SWAN_PROFILE_EDIT_DONE` 仅匹配顶栏位置 | element 2026-09-10 |
| 中文输入 | `adb shell input text` 不支持中文（NullPointerException）；AI 对话/歌单名等中文输入现框架不可达，需 IME 方案（框架层，待用户决策） | explorer 2026-09-10 Wave2 |
| 播放态前置 | 播放队列/歌词入口在无播放任务时点击零反应；用例设计必须前置播放任务（本账号全平台未授权，无法建立播放） | explorer 2026-09-10 Wave2 |
| 授权门禁弹层 | "授权登录"/"去授权"/"添加"弹层带 desc='纱罩' scrim，`press_back` 可关；⛔ 授权按钮不点（Wave5 补充第三种文案变体"请先添加该 AI 平台"，判据不变） | explorer 2026-09-10 Wave2 |
| 设备单选列表 | 切换设备弹层与 AI 自动朗读设备弹层共用设备列表（真实音箱×3+手机扬声器+Apple Music），⛔ 全部禁止选择 | explorer 2026-09-10 Wave2 |
| AI 语音按钮权限 | 触发系统麦克风权限弹窗，key 与相机权限同族（permission_allow_one_time_button 等） | explorer 2026-09-10 Wave2 |
| 播放历史计数口径 | 首页卡片"已播歌曲 1首"与播放历史页内"暂无历史播放"口径不一致（App 行为，断言以页内为准） | explorer 2026-09-10 Wave2 |
| 歌单域两套详情 | 歌单页路径详情带右上 ⋮（修改名称/删除歌单），收藏页路径无 ⋮；布局同模板数据同源但行为两套 | explorer 2026-09-10 Wave2 |
| 音乐/电台 Tab 滚动位残留 | 从子页返回后页面停在滚动位，搜索条/卡片 OCR 屏外报 AssertionError；先 swipe_down x2 复位再定位 | explorer 2026-09-10 Wave4 |
| 平台页分类持久 | 左侧分类（音乐/AI/电台）跨会话持久，与首页顶 Tab 同款；切过"电台"后再进平台页点"QQ音乐"等音乐分类行文案会找不到 | explorer 2026-09-10 Wave4 |
| 搜索页 T9 键盘 | 输入框是原生 EditText，App 自定义 T9 键盘下 `adb input text` 英文仍有效；键盘区有"搜索"同名键，顶栏搜索按钮 OCR 须 region 限定 | explorer 2026-09-10 Wave4 |
| 搜索历史 chip | 整行可点节点（desc=关键词），一键带词复搜直达结果页，省去输入步骤 | explorer 2026-09-10 Wave4 |
| 授权门禁弹层判据 | desc='纱罩' 是唯一稳定判据（两文案变体）；press_back 一次即关；电台行播放不需授权、分组标题进多级页才需要 | explorer 2026-09-10 Wave4 |
| 搜索页返回行为 | 结果页 press_back 回输入页后关键词**不回填**（显示 hint，X 按钮消失）；再 press_back 停留输入页不清空，第三次才回首页——回首页计数别按两次写 | element 2026-09-10 Wave4 |
| 搜索提交 region 限定 | T9 键盘区有"搜索"同名键，提交必须 region 限定顶栏（y≈100-160），否则点中键盘键 | element 2026-09-10 Wave4 |
| 平台页分类复位 | 左侧分类持久但上一会话结束态不定，进平台页后须显式 `click_text("电台", region=左侧栏)` 切换；电台分类三行（全国/90/80）箭头图标完全相同可共用一张图 | element 2026-09-10 Wave4 |
| 首页顶 Tab 前置 | 顶 Tab 行只存在于首页；从其他页回首页·推荐必须先点底部 `tab_recommend` 再点顶 Tab"推荐" | element 2026-09-10 Wave4 |
| AI 平台管理页标题歧义 | 顶栏标题「平台」两字与底 tab 同名,OCR 断言须 region 限定顶栏 | explorer 2026-09-10 Wave5 |
| 「历史对话记录」双入口 | 首页 AI Tab 区块**标题行**→AI历史页;**记录行**(区块内或历史页内)→直达 AI 对话页(回显对话),落点不同别混用 | explorer 2026-09-10 Wave5 |
| 角色编辑表单两屏长 | 语音/昵称/「完成」在下半屏,须 **swipe_up x3**(400px/次)才进屏(x2 不够,完成按钮仍贴底) | explorer 2026-09-10 Wave5;element 2026-09-10 修正 |
| DIY形象付费功能 | 0.2 惠币/张起;「开始生成/充值」⛔ 只断言不点 | explorer 2026-09-10 Wave5 |
| 授权门禁第三变体 | AI 平台管理页行右侧按钮弹「添加新平台」门禁(文案:请先添加该 AI 平台…),纱罩判据不变,press_back 关 | explorer 2026-09-10 Wave5 |
| 所有角色页多选态判据 | 点「多选」后原位变「取消」+底栏「全选/删除」出现;`on_text("全选")` 出现/消失即可作多选态进出判据,无需截图 | verify 2026-09-10 Wave5 |
| HONOR 系统 WiFi 命令被阉割 | `cmd wifi connect-network` 报 `Uid 2000 does not have access`（help 里也无此项,HnWifiService 定制）；`add-suggestion` 仅注册不强制连且不会离开有网 WiFi。连 WiFi 一律走 `aw.connect_wifi(ssid, password)`（JDY-AN00 / Android 14 实测） | orchestrator 2026-09-24 |
| connect_wifi 边界 | 系统 WLAN 页定位走 dump_nodes（SSID=`android:id/title`、密码框/连接/取消=`com.android.settings:id/password`/`btn_wifi_connect`/`btn_wifi_cancel`），搜索前先回顶（页面保留上次滚动位）；幂等（已连目标网直接 True）；密码仅 ASCII（adb input text）；断言用 `driver.wifi_current_ssid()`（cmd wifi status）；无互联网确认弹窗白名单 `WIFI_NO_INTERNET_RULES` 文案待真机热点实测补齐；**真实连接链路（输密+点连接）冒烟未覆盖**，待配网用例验证 | orchestrator 2026-09-24 |

## 框架 / 环境

| 场景 | 正确做法 | 来源 |
|------|----------|------|
| 元素图转正门禁 | image_ai 暂存 → 离线匹配（scripts/verify_element_match.py，≥0.8）→ verify 真机点击反应 → 才 promote_image；禁止跳步 | 编排约定 2026-09-08 |
| 嵌入模型下载 | huggingface / hf-mirror 均被网络拦截；用 ModelScope 下载到本地 `models/`，管线经 `UIAUTOTEST_EMBEDDING_MODEL` 指向 | orchestrator 2026-09-08 |
| protobuf 版本 | 必须钉 3.20.2：chromadb 会把它顶到 7.x 弄坏 PaddleOCR；连带 googleapis-common-protos 钉 1.63.2 | orchestrator 2026-09-08 |
| paddle+torch 同进程 | 先 import paddle 再 import torch 会 shm.dll 崩溃；两者分进程跑（向量管线不含 paddle，天然安全） | orchestrator 2026-09-08 |
| 验证码页返回 | press_back 会退出 App（不是回登录页）；重启后回登录页 | element 2026-09-08 |
| paddle 抢占 root logger | import paddleocr 后再 logging.basicConfig 是 no-op，独立验证脚本 INFO 全被吞（exit 0 但无日志）；import 后须显式 root.addHandler(StreamHandler(sys.stdout)) + setLevel(INFO)，并把 ppocr/paddle logger 压到 WARNING | verify 2026-09-10 Wave4 |
| 本机 adb 路径 | 本机 adb 在 `D:\scrcpy-win64-v4.1\adb.exe`（`C:\platform-tools\adb.exe` 不存在，那是远端 166 的路径）；脚本直连 adb 时勿混用两机路径 | verify 2026-09-10 Wave5 |

| 场景 | 正确做法 |
|------|----------|
| uiautomator dump 失败时 cat 陈旧 /sdcard/uiat_aw_hierarchy.xml | accessibility_exists/find_nodes 会返回上次成功 dump 的幻影结果（2026-09-28 element 三连误判实证）；语义断言前先确认 dump 时间戳或 `adb shell rm` 该文件；根治需改 android_driver.dump_nodes（框架层待决策） |
| 播放任务会过期 | 进度 00:00/00:00 但按钮 glyph 形态不变（暂停态残留）——播放页相关断言勿以"进度非零"为前提；rig 电台会话跨 relaunch 持久（服务端记忆），"无会话态"一经播放不可逆达 |
| 底排图标四件套全部背景依赖 | 设备钮/加号钮/收起钮/音量图标配色随背景明度自适应（浅底黑glyph/深底白glyph），单模板跨背景必失配——一律走多模板链（参照 _find_dismiss_btn/_DEVICE_BTN_TEMPLATES/_PLUS_TEMPLATES），新图标采图紧贴 glyph+浅深双变体 |
| 真机单租户纪律 | dev-runner 与 element 并发操作同一设备=双方产出作废（2026-09-28 实证）；设备派发一律经 main 串行排队 |
