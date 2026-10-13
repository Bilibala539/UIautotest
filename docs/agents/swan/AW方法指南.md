# Swan AW 方法指南（唯一查询入口）

> **用途**：写新用例/新 AW 前必查——先看这里有没有能复用的方法，防止 AI 在不知情的情况下重复创建 AW 或错误使用。
> **写法规范**：新方法怎么写（签名/docstring 六要素/定位/断言收尾/自检清单）见 **`AW方法编写规范.md`**（强制）。
> **维护**：内容提取自 `utils/aw/business/swan.py`（SwanBusiness）与 `utils/aw/business/swan_regression.py`（回归 mixin）的 docstring，方法变更后同步更新本文件。权威细节以代码 docstring 为准（本文件是索引，docstring 是正文）。
> 生成日期：2026-10-12。

## 0. 三层 AW 体系与调用方式

```
用例: self.user.start_play(...)     ← 业务方法（User.__getattr__ 自动代理，勿绕写 user.business.xxx）
      self.aw.click_image(...)      ← 基础操作（user.aw 即 SwanBusiness 实例）
业务层 SwanBusiness(34 个公开方法)    ← 本指南 §2
回归 mixin swan_regression.py       ← 本指南 §3（用例域前置/清理，测试类继承使用）
基础层 AWBase + FlutterBaseAW        ← 本指南 §4（设备交互唯一入口）
```

- 继承链：`SwanBusiness(CommonBusinessMixin, FlutterBaseAW)` → 所有基础操作在 `user.aw` 上直接可用
- 账号：环境变量 `SWAN_PHONE` / `SWAN_PASSWORD`；包名 `SWAN_PACKAGE`（默认 com.swan.network）

## 1. 新增方法前的检查顺序（防重复创建）

1. 查本指南 §2/§3——功能是否已有方法承载（注意参数变体：`via=`/`mode=`/`source=`/`action=` 常已覆盖多场景）
2. `search_code` / `find_symbol`（codemap MCP）模糊确认无同名/同义实现
3. 已有方法**只差参数** → 优先给现有方法加参数（向后兼容，不破坏既有用例），不要另起炉灶
4. 确认要新建 → 落 `SwanBusiness`（不进 base 层、不进用例），docstring 必含：方案编号/服务用例号、定位方式（[图]/[OCR]）、踩坑注记；命名约定 `go_/open_`=导航、`set_`=设置、`assert_`=断言收尾、`_`前缀=内部辅助

## 2. SwanBusiness 业务方法（34 个，按域分组）

### 2.1 启动与登录（存量 key 实现，迁移待拍板——勿模仿新增）

| 方法 | 干嘛 | 关键参数/注意 |
|---|---|---|
| `login(method=..., ...)` | 登录统一入口，按 method 调度到子方法 | method: sms/password/wechat/weibo（wechat/weibo 未实现） |
| `login_by_sms(phone, wait_code=60)` | 验证码登录，**幂等**：已登录早退 | 未登录时先重启清残留表单再登录（表单残留会使协议反选） |
| `login_with_password(phone, password)` | 密码登录，自动从验证码页形态切换 | 存量 key 定位；连续 3 次错密码可能锁号 |
| `enter_sms_code_step(phone, timeout=15)` / `fill_sms_code(code)` | 验证码分步辅助（输入页→填码） | 一般经 login_by_sms，不单独调 |
| `logout_if_needed()` | 登出回登录页，**幂等**：未登录跳过 | |
| `relaunch_app(package, timeout=30)` | 冷启动重启 App | 前置归一化常用（App 停未知页时重置） |

### 2.2 导航与页面状态

| 方法 | 干嘛 | 关键参数/注意 |
|---|---|---|
| `go_home(timeout=15)` | 回首页容器 | [图]（2026-10-12 存量 key 迁移）；幂等：首页 Tab 选中时短路不点（选中态图未截，到位断言走顶 Tab 行图+OCR「推荐」）；push 页自动先 back_to_tab_shell |
| `go_bottom_tab(name, timeout=15)` | 底部四 Tab 轮巡（首页/平台/设备/我的） | [图] 未选中态图点击 + 各页特有锚断言到位（2026-10-12 核对：域4 起即 [图] 实现，无 key）；非法 name 报 ValueError |
| `go_top_tab(name, timeout=15)` | 首页五顶 Tab 切换（推荐/音乐/AI/可视音箱/电台） | [图]；顶 Tab 有持久化陷阱，方法内部已处理 |
| `open_home_card(name, timeout=15)` | 首页推荐卡片进入对应页 | [OCR]；歌单卡未找到时内部下拉刷新重试 |
| `back_to_tab_shell(max_backs=3)` | 逐级 press_back 退出 push 页回 tab 壳 | [图] 锚定判定；**teardown 链必备**（push 页直接 go_home 必炸） |

### 2.3 设备与输出切换

| 方法 | 干嘛 | 关键参数/注意 |
|---|---|---|
| `select_device(name, via="card"\|"player")` | 切输出设备（2026-09-28 新口径） | card=设备页点卡（本机分支点卡→电池优化弹窗→贴底条断言「扬声器」）；player=播放页弹层选行；切换真实生效**不自动回切**；输出已=目标时短路跳过（rig 行已选中态重入会导航分叉）；设备名比较走 compact 归一化（OCR 吞空格防 flaky） |

### 2.4 播放发起与控制

| 方法 | 干嘛 | 关键参数/注意 |
|---|---|---|
| `start_play(source="favorite", mode="all", index=0)` | 发起播放（A13，各域播放前置） | mode=all 点「播放全部」[图]（source: favorite/playlist，调用方须已在对应页）；mode=song OCR 点歌名（不在首屏自动上滑重找≤3 轮）；收尾断言播放页+播放态，**单次有界重试**（QQ 源 VIP 试听即停场景） |
| `player_control(action="play")` | 播放控制 | action: pause/play/next/prev；每次动作后自动断言对应播放态 |
| `set_loop_mode(mode="list")` | 切循环模式 | mode: list/single/shuffle；点至目标态图标出现（≤3 次），[图] 收尾 |
| `assert_playing()` | 播放态断言：⏸ [图] +（黑胶动检 或 进度 OCR 递增）双证据 | 轮询窗 20s（覆盖切歌瞬态 loading） |
| `assert_paused()` | 暂停态断言：▶ [图] + 进度时间静止 | 对偶口径；不区分「无任务」与「已暂停」 |
| `assert_now_playing(title, artist="")` | 当前曲目断言（曲目区 OCR，动态元素不截图） | artist 缺省只核歌名 |

### 2.5 进度与音量

| 方法 | 干嘛 | 关键参数/注意 |
|---|---|---|
| `seek_to(ratio, action="drag")` | 进度跳转 | action: drag/click；drag_on_template 元素锚定（非坐标）；OCR 双时间核对落点 |
| `set_volume(value, action="drag")` | 音量调节 | action: drag/click（value=目标百分比）/plus/minus（value=连点次数）；UI 态百分比核对（声学断言降级口径 §5③） |
| `volume_key(direction="up", long_press=False)` | 物理音量键 | 方向断言前先拖音量到中位 50 防 0/100% 边界失真（用例层已处理） |

### 2.6 歌单、收藏与最近播放

| 方法 | 干嘛 | 关键参数/注意 |
|---|---|---|
| `open_playlist_detail(platform, playlist="")` | 进歌单详情页 | platform 校验走 _require_platform_text；收尾断言页锚 |
| `favorite_playlist(platform, state="on")` | 歌单收藏开关 | state: on/off/toggle；两态图标 [图] 断言 |
| `collect_song(target_platform, playlist, source="player")` | 收藏当前曲到目标歌单（A30，12 条合 1） | source: player（播放页 [+]）/playlist_page（详情页行内 [+]，恒收最上行）；**同曲重复收藏会被 App 静默拦截**——先调 remove_song_from_playlist 预清理 |
| `remove_song_from_playlist(platform, playlist, song, ...)` | 从目标歌单移除指定曲（行内垃圾桶） | 测试清理语境可点（评估依据见 docstring）；后置条件=tab 壳 |
| `playlist_top_song(timeout=10)` / `top_song_row_name(timeout=10)` | 读歌单/源页最上行歌名 | 与 _tap_song_row_plus 同锚定，提取行=将收藏行 |
| `playlist_has_song(song, timeout=8)` | 判断歌单是否含某曲 | OCR 前缀匹配 |
| `recent_played_visible(kind, name, timeout)` / `assert_recent_played(kind, name, timeout=10)` | 最近播放入口→分类页断言条目 | kind: 歌曲/歌单/歌手/专辑/电台/播客；13 条合 1 |

### 2.6b 平台内容页（W1-D，2026-10-13 首版——真机验证待账号授权态）

| 方法 | 干嘛 | 关键参数/注意 |
|---|---|---|
| `open_platform(platform)` | 进入已授权平台主页（A27） | platform: qq/netease（酷狗未授权不可达，拍板忽略）；**未授权行体点击无反应**（explorer 实锤），仅已授权态可用；生效验证=主页搜索文案 [OCR] |
| `open_platform_entry(platform, entry, expect_title="")` | 主页入口跳转（A28） | expect_title **不可跨平台复用**（同名"排行榜"QQ 落飙升榜、网易云落排行榜页）——映射见 `_PLATFORM_ENTRY_TITLES`，未登记入口需先探索 |

配套用例（test_平台内容页进入 / test_平台入口跳转）带**授权态条件 skip**（未授权态 [图] 探针自动 skip）；授权域搁置中（网易云验证码不受控），首跑需人工读码授权后自动恢复运行。

### 2.7 搜索

| 方法 | 干嘛 | 关键参数/注意 |
|---|---|---|
| `search(keyword, entry="home", timeout=15)` | 发起搜索 | entry: home/平台名；[图] 搜索框+按钮，input_text 输入（adb 中文输入不可达，关键词用英文） |
| `assert_search_results(tab, platforms=None, ...)` | 搜索结果按 Tab 断言 | platforms 配置→断言有结果；缺省→断言空态（未授权稳定口径） |

### 2.8 辅助与探测

| 方法 | 干嘛 | 关键参数/注意 |
|---|---|---|
| `list_accessibility_keys_by_prefix(prefix)` | 按前缀枚举语义树 key | 仅探索/断言辅助（如 wifi_device_card_ 前缀数设备卡）；**运行时定位禁 key**（CLAUDE.md 规则 2） |
| `dismiss_auth_notice_popup(...)` | 授权提示弹层探测关闭 | 前置防护用 |
| 内部辅助（`_ocr_compact`/`_match_ocr_name`/`_wait_compact_text_in_region`/`_wait_player_page_open`/`_dismiss_full_player`/`_snap_chain_miss` 等 `_` 前缀） | OCR 归一化比较、播放页到位探测、收起钮多模板链、miss 存证 | 供 mixin/用例域调用；改造前读 docstring 踩坑注记 |

## 3. 回归 mixin（swan_regression.py，测试类继承获得）

三个 mixin：`SwanPlayerRegressionMixin`（播放器域）→ `SwanContentRegressionMixin`（内容域，覆写 teardown）→ `SwanLoginRegressionMixin`（登录域存量 key 口径）。**写用例缺前置/清理先来这里找，禁止复制粘贴**。

| 方法 | 干嘛 |
|---|---|
| `setup()`（自动调） | 实例化 self.user/self.aw/self.phone（login 另有 password/package） |
| `teardown()`（自动调） | G3/G4 清理链：关设备弹层→关音量弹层→尽力暂停→收播放页→（播放器域另含输出恢复）→back_to_tab_shell→go_home |
| `_preset_playing(device_type, source, mode)` | 播放前置：登录→确定输出（speaker 防污染校验/wifi 切 rig 含短路探测）→推荐顶 Tab→我喜欢页→start_play |
| `_preset_playing_on_favorite(source, mode)` | 内容域播放前置（到位判据改 OCR「宝藏音乐，随心收藏」） |
| `_ensure_logged_in_on_home()` | 幂等登录+首页壳三级锚断言（登录页/未知页先 relaunch 重置） |
| `_stay_on_recommend_tab()` / `_open_device_page()` / `_open_player_page()` / `_click_bottom_player_bar()` | 顶 Tab 复位（持久化陷阱）/设备页导航（2026-10-12 迁移 [图]：SWAN_TAB_DEVICE 点击，已在设备页锚可见时短路）/播放页导航（模板失配走条带 OCR 兜底） |
| `_probe_image(template, timeout, threshold)` | 模板缺失防护探测（find_image 对缺失模板是 assert 崩溃，可选命中一律走它） |
| `_close_sheet_if_any` / `_close_volume_popup_if_any` / `_pause_if_playing` / `_dismiss_player_if_any` | 残留清理四件套（弹层探测关闭/暂停/收播放页） |
| `_restore_speaker_output_if_needed()` / `_ensure_speaker_output()` | 输出防污染（teardown 非断言版 / speaker 前置硬断言版） |
| 登录域断言辅助 | `_assert_on_login_page` / `_assert_on_home` / `_assert_sms_form` / `_assert_password_form` / `_ensure_fresh_sms_form` / `_assert_any_text`（存量 key 口径） |

rig 环境变量（SWAN_DEVICE_NAME / SWAN_TEST_SONG / SWAN_COLLECT_* / SWAN_HISTORY_* / SWAN_SEARCH_*）清单见 swan_regression.py 模块 docstring。

## 4. 基础操作速查（AWBase + FlutterBaseAW，user.aw 上直接调）

| 类别 | 方法 | 说明 |
|---|---|---|
| 定位点击 | `click_image(tpl, threshold=0.8, timeout=10, dx, dy, region)` | **首选**；失败先查图片质量（规则 7），禁坐标回退 |
| | `click_text(text, timeout=10, dx, dy, region)` | 次选 OCR；筛选器/弹窗选项加 dy=8~12 |
| 断言 | `image_exists(tpl, threshold, timeout, region)` / `text_exists(text, timeout, region)` | 断言必须用它们收尾，禁"只断言没异常" |
| 探测 | `find_image` / `find_image_rect`（返回矩形）/ `find_text_by_ocr` / `ocr_scan_page(region)` | 找到返回坐标/矩形，未找到返回 None；`text_not_exists` 反向断言 |
| 输入 | `input_text(text)` / `clear_input()` | 走 adb；中文不可达 |
| 滑动手势 | `swipe/swipe_up/swipe_down/swipe_left/swipe_right/scroll_up/scroll_down` | 坐标滑动仅系统页可用 |
| | `drag_on_template(tpl, start_ratio, end_ratio, axis)` | **元素锚定滑动**（滑条/进度条），非坐标回退 |
| | `long_press(x, y)` / `long_press_text` / `long_press_image` | 长按族 |
| Flutter 专有 | `wait_toast(text, timeout=4, region)` | 动作后**立即**调用（toast 2-3.5s 即逝）；OCR 轮询 |
| | `region_changed(x, y, w, h, gap=0.5, samples=3)` | 区域动检（播放态第二证据） |
| | `dump_semantics` / `print_semantics` / `accessibility_exists` / `wait_accessibility` / `click_accessibility` | **仅 explorer 探索与调试**；运行时用例禁 key（规则 2） |
| 系统按键 | `press_back` / `press_home` / `press_key(key, long_press)` | |
| 系统弹窗 | `dismiss_app_popups(rules, rounds=3)` | 白名单处置（隐私协议/权限弹窗等），白名单外只记 WARNING |
| 系统网络 | `connect_wifi(ssid, password)` | 系统 WLAN 设置页 UI 自动化（D1 已拍板方案） |
| 截图 | `take_screenshot(save_path)` / `screenshot_for_explore` | 失败截图由 `_screenshot_on_failure` 装饰器统一落盘 |

## 5. 常见误用对照

| ❌ 错误 | ✅ 正确 |
|---|---|
| 用例里重写登录/导航序列 | mixin 的 `_ensure_logged_in_on_home` / `_preset_playing` |
| 同曲收藏前直接 collect_song | 先 `remove_song_from_playlist` 预清理（重复收藏被 App 静默拦截） |
| push 页收尾直接 `go_home` | 先 `back_to_tab_shell` 再 `go_home` |
| 切输出后假设会自动回切 | wifi 用例 teardown 已恢复；speaker 用例开场 `_ensure_speaker_output` 兜底 |
| OCR 断言裸子串比较（吞空格永假） | `_wait_compact_text_in_region` / compact 归一化 |
| 找不到循环钮就 tap 坐标 | `set_loop_mode` 已含三态轮巡定位；失败查图片质量 |
| 新建「打开某页」方法 | 先查 go_bottom_tab/go_top_tab/open_home_card/open_playlist_detail 是否已覆盖 |
