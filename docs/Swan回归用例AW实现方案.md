# Swan 回归用例 AW 实现方案

> 来源：人工校验过的《回归用例.xlsx》（76 条 P0 用例，9 大模块）。
> 本文是把这些用例翻译成自动化 AW 的**实现清单**，按 driver / base / business 三层组织，经用户确认后拆派给 aw-element（截图）和 aw-codegen（写代码）。
>
> 定稿日期：2026-09-23

---

## 0. 三条定位铁律（本文所有 AW 的前提）

| 标记 | 含义 | 使用场景 |
|---|---|---|
| **[图]** | OpenCV 模板匹配（`click_image` / `find_image`），首选 | 静态图标、按钮，元素周围背景稳定 |
| **[OCR]** | 文字识别定位（`click_text` / `find_text_by_ocr`），次选 | 动态元素（歌名、设备名、时间）、元素周围有动态背景、纯文字入口 |
| ~~[key]~~ | accessibility 定位，**运行时禁止** | 仅限 explorer 探索与调试 |

补充说明：

- **滑动/拖动不是坐标回退**：以模板图片矩形为锚做比例定位（如"进度条拖到 75%"），依赖 base 层新增的 `find_image_rect`，见 §2。
- 现有登录域 AW 全部用 key 定位，本次一并改造为 [图]/[OCR]（见 §3.1）。

---

## 1. 用例 → AW 的合并思路

76 条用例若一比一生成 AW 会爆炸成 70+ 个方法。实际按三个维度合并后，**业务层只需 32 个方法**：

| 维度 | 例子 | 合并结果 |
|---|---|---|
| 设备类型 | 扬声器 vs WIFI 音箱设备 | 同一方法加参数 |
| 音乐平台 | QQ音乐 / 网易云 / 酷狗 / swan | 同一方法加参数 |
| 交互方式 | 拖动 vs 点击、播放页 vs 歌单页入口 | 同一方法加 action/source 参数 |

典型例子：

- 用例 16–22（列表/单曲/随机循环 × 扬声器/设备 共 18 条）→ `player_control` + `set_loop_mode` + `assert_playing` 三个方法承载
- 用例 44–55（12 条收藏）→ `collect_song(target_platform, playlist, source)` 一个方法
- 用例 56–68（13 条最近播放）→ `assert_recent_played(kind, name)` 一个断言方法

---

## 2. 各层实现清单

### 2.1 Driver 层（`utils/aw/driver/android_driver.py`）⚠️ 框架层，需用户批准

框架层改动按项目规则须用户决策。**3 个方法待批准：**

| # | 方法 | 说明 | 服务用例 |
|---|---|---|---|
| D1 | `connect_wifi(ssid, password)` | ✅ 已拍板并实现（2026-09-24）：HONOR 阉割 `cmd wifi connect-network`（Uid 2000 无权限）、`add-suggestion` 仅注册不强制连，改为系统 WLAN 设置页 UI 自动化——driver 原语 `start_action` / `wifi_current_ssid` + `AndroidBaseAW.connect_wifi`（dump_nodes 语义定位 + `cmd wifi status` 断言，详见 runtime_experience）。热点配网必须跳出 App 连系统 WiFi | 10 热点配网 |
| D2 | `press_key(key, long_press=False)` | 现方法扩展：`input keyevent --longpress`，支持物理音量键长按 | 27, 28 |
| D3 | `get_foreground_package()`（可选） | dumpsys 查前台包名，热启动恢复断言的稳定性辅助 | 3 |

已有 `start_app` / `stop_app` / `swipe` / `long_press` / `press_home` 够用，不动。

### 2.2 Base 层（`flutter_base.py` + AWBase）

规则 1 授权范围内（AWBase/平台 base 属业务层可要求补充的基础能力）。**5 个方法：**

| # | 方法 | 放哪 | 说明 | 服务用例 |
|---|---|---|---|---|
| B1 | `find_image_rect(template, threshold, timeout, region)` | AWBase | 返回模板**矩形** `(x, y, w, h)`。现 `find_image` 只返回中心点，滑条按比例定位必须知道整条滑条的范围 | 23–26 进度/音量 |
| B2 | `wait_toast(text, timeout)` | flutter_base | toast 2–3 秒即逝：动作完成后**立即**高频截图（约 300ms 间隔）+ OCR 查文本 | 配网、多房间、循环模式 toast 断言 |
| B3 | `long_press_key(key)` | flutter_base | 调 driver 的长按 keyevent（音量键长按） | 27, 28 |
| B4 | `region_changed(x, y, w, h, gap, samples)` | flutter_base | 区域多帧像素差分 → 判"画面在动"。黑胶唱片旋转、歌词滚动的播放态第二证据 | 13–22 播放态断言 |
| B5 | `drag_on_template(template, start_ratio, end_ratio, axis)` | flutter_base | 以模板矩形为锚的滑条拖动：`find_image_rect` 拿矩形 → 按比例算起止点 → `swipe`。**元素锚定手势，非坐标回退** | 23–26 |

> ⚠️ toast 捕获有时序风险：`wait_toast` 必须在触发动作的**同一方法内紧接着调用**，不能隔了截图/OCR 才开始找。

### 2.3 Business 层（`SwanBusiness`，9 个域 32 个方法）

统一入口按参数调度 + 分方式子方法（模式同现有 `login` → `login_by_sms` / `login_with_password`）。

---

#### 域 1：启动与登录（用例 1–8）——改造为主

| # | 方法 | 关键步骤定位 | 用例 |
|---|---|---|---|
| A1 | `login(method="sms"\|"password"\|"wechat"\|"weibo", ...)` | 统一入口，按 method 调度到下面 4 个子方法 | 全部 |
| A2 | `login_by_sms(phone)` 🔧改造 | 手机号输入框 [图]、协议勾选框 [图]（新截）、下一步 [图]（已有）、验证码框 [图]（已有） | 4 |
| A3 | `login_with_password(phone, pwd)` 🔧改造 | 右上角"密码登录" [OCR]、输入框/勾选框/登录钮 [图] | 5 |
| A4 | `login_by_wechat(phone)` | 微信图标 [图]（新截）→ 微信 App"允许" [OCR]（跨 App）→ 绑定手机页输入框 [图]、完成 [OCR] | 6 |
| A5 | `login_by_weibo(phone)` | 同 A4，微博分支 | 7 |
| A6 | `cold_start_expect_login()` | `relaunch_app` + 登录页锚点 [图] | 1 |
| A7 | `background_resume(expect_anchor, wait_s=30)` | `press_home` 后台 → `start_app` 前台 → 一级/三级界面锚点 [图/OCR] | 3 |
| A8 | `bind_phone_back()` | 左上角关闭 [图]（新截）→ 回登录页 [图] | 8 |

> 🔧改造 = 现 key 定位（`click_accessibility`）全部换成 [图]/[OCR]，登录页各控件需补截元素图。

---

#### 域 2：配网（用例 9–10）

| # | 方法 | 关键步骤定位 | 用例 |
|---|---|---|---|
| A9 | `provision(mode="ble"\|"hotspot", device_name, ssid, password)` | 统一入口调度 | 9, 10 |
| A10 | `provision_by_ble(...)` | 设备名核对 [OCR]、下一步 [图]（已有）、SSID/密码框 [图]（新截）、连接 [OCR]、配网进度 [OCR]、`wait_toast("配网成功")`、5s 内设备列表出现 [OCR] | 9 |
| A11 | `provision_by_hotspot(...)` | "前往设置" [OCR] → `connect_wifi`（已实现）→ 回 App 弹窗 [图]（新截）→ WiFi 列表 [OCR]、密码框 [图]、完成 [OCR] → `wait_toast("连接成功")` | 10 |

---

#### 域 3：播放器与播放控制（用例 11–28）——复用度最高

| # | 方法 | 关键步骤定位 | 用例 |
|---|---|---|---|
| A12 | `select_device(name, via="card"\|"player")` | card：卡片设备名 [OCR] + 选中态 [图]（新截）；player：设备切换钮 [图]（`SWAN_PLAYER_DEVICE_BTN`，草稿转正）→ 弹层设备名 [OCR] + 勾选态 [图]（新截） | 11, 12 |
| A13 | `start_play(source, mode="all"\|"song", index=0)` | 全部播放 [图]（已有：我喜欢页、歌单详情页两张）；单曲 [OCR] 歌名 | 13, 14 及各域前置 |
| A14 | `player_control(action="next"\|"prev"\|"pause"\|"play")` | 控制键 [图]（新截：上一首/下一首/⏸；▶ 已有） | 16–22 |
| A15 | `set_loop_mode(mode="list"\|"single"\|"shuffle")` | 循环钮 [图] 新截 3 态，点至目标态图标出现 | 15, 19 |
| A16 | `assert_playing()` / `assert_paused()` | ⏸/▶ [图] + 黑胶区 `region_changed`（B4）双帧差分 | 13–22 |
| A17 | `assert_now_playing(title, artist)` | 曲目区 [OCR]（`player_title` 是动态元素） | 16–22 |
| A18 | `seek_to(ratio, action="drag"\|"click")` | 进度条整条 [图]（新截）→ `drag_on_template`（B5）或 `click_image` 偏移 | 23, 24 |
| A19 | `set_volume(value, action="drag"\|"click"\|"plus"\|"minus")` | 音量图标 [图]（新截）开弹窗、滑条整条 [图]（新截）、加减钮 [图]（新截） | 25, 26 |
| A20 | `volume_key(direction, long_press=False)` | `long_press_key`（B3）物理音量键 | 27, 28 |

---

#### 域 4：导航（用例 29–31）

| # | 方法 | 关键步骤定位 | 用例 |
|---|---|---|---|
| A21 | `go_bottom_tab(name)` | 平台/设备/首页/我的 4 图标 [图]（新截） | 29 |
| A22 | `go_top_tab(name)` | 音乐/AI/电台/推荐 4 张 [图]（已有）+ 可视音箱 [图]（补截） | 30 |
| A23 | `open_home_card(name)` | 我喜欢/歌单/AI/最近播放/个性化推荐卡片 [OCR]（卡片内容动态，背景在动） | 31 |

---

#### 域 5：平台授权（用例 32–37）

| # | 方法 | 关键步骤定位 | 用例 |
|---|---|---|---|
| A24 | `authorize_platform(platform, entry="platform"\|"home")` | 授权图标/置灰图标 [图]（新截 ×3 平台）、授权登录按钮 [图]（已有）、三方 App 内授权确认 [OCR]（跨 App） | 32–37 |
| A25 | `assert_platform_state(platform, authorized)` | 授权方框两态；先试 OCR"已授权"文字，不稳再截两态图 | 32–37 |
| A26 | `deauthorize_platform(platform)` | AI 平台管理页 [图]（已有）、解除授权 [OCR]——**用例前置/清理用**（用例都假设"未授权"起始态） | 前置 |

---

#### 域 6：平台内容页（用例 38–40）

| # | 方法 | 关键步骤定位 | 用例 |
|---|---|---|---|
| A27 | `open_platform(platform)` | 平台图标 [图]（网易云行已有，QQ/酷狗新截）或 [OCR] 平台名 | 38–40 |
| A28 | `open_platform_entry(platform, entry, expect_title)` | 入口文字 [OCR] + 到达页标题 [OCR]（深层内容多为动态图文） | 38–40 |

> 知识库缺口：QQ 音乐主页 / 网易云主页 / 酷狗主页三个 draft 页需 explorer 先补，本域延后实现。

---

#### 域 7：歌单、收藏与历史（用例 41–68）——条数最多，合并收益最大

| # | 方法 | 关键步骤定位 | 用例 |
|---|---|---|---|
| A29 | `favorite_playlist(platform, state="on"\|"off"\|"toggle")` | 收藏图标两态 [图]（新截） | 41–43 |
| A30 | `collect_song(target_platform, playlist, source="player"\|"playlist_page")` | 歌曲收藏图标 [图]（新截）、平台选择 [OCR]、目标歌单 [OCR] 歌单名 | 44–55（12 条合 1） |
| A31 | `assert_recent_played(kind, name)` | 最近播放入口 [OCR]、分类 Tab 条 [图]（已有）、条目 [OCR] | 56–68（13 条合 1） |
| A32 | （播放入口复用 A13/A14） | 歌手/电台/博客页点条目 [OCR] | 62–66 |

> 用例 68（自动切歌记录最近播放）需等整曲播完，**耗时极长**，建议安排在夜间跑或选最短歌曲。

---

#### 域 8：搜索（用例 69–72）

| # | 方法 | 关键步骤定位 | 用例 |
|---|---|---|---|
| A33 | `search(keyword, entry="home"\|"<platform>")` | 搜索框 [图]（已有）、搜索按钮 [图]（已有）、`input_text` 输入 | 69–72 |
| A34 | `assert_search_results(tab, platforms)` | Tab 切换 [OCR]（单曲/艺人/专辑/歌单/电台/博客）、结果区 [OCR] | 69–72 |

---

#### 域 9：多房间（用例 73–76）——有硬阻塞，见 §5

| # | 方法 | 关键步骤定位 | 用例 |
|---|---|---|---|
| A35 | `sync_rooms(main, subs, on=True)` | 同步设备按钮 [图]（新截）、勾选框 [图]（新截）/设备名 [OCR]、完成 [OCR]、`wait_toast("正在更新设备"/"多房间模式设置成功"/"单房间模式设置成功")` | 73–76 |
| A36 | `assert_room_synced(main, subs, state)` | 卡片子设备区 [OCR] | 73–76 |

> A31 芯片（A31/H76D/H76G）流程一致，芯片型号只是数据差异，无需按芯片分方法。

---

## 3. 元素图片需求表（aw-element 待截，约 20 张）

新图一律先进 `image_ai/flutter/`，跑通后转正（规则 4）。

| 域 | 图片 | 现状 |
|---|---|---|
| 登录 | 手机号输入框、协议勾选框、密码登录入口、微信图标、微博图标、绑定手机页关闭钮 | 新截 |
| 播放页 | ⏸ 暂停态按钮、上一首、下一首、循环模式 3 态（列表/单曲/随机）、音量图标、进度条整条、音量弹窗（滑条+加减钮） | KB 已标"待截" |
| 播放页 | `SWAN_PLAYER_DEVICE_BTN` | image_ai 草稿，转正 |
| 设备页 | 底部导航 4 图标（平台/设备/首页/我的）、设备卡片选中态、同步设备按钮、勾选框、完成按钮 | 新截 |
| 歌单/播放页 | 收藏图标 × 收藏/未收藏两态（歌单 + 歌曲两套） | 新截 |
| 平台页 | 授权方框 未授权/已授权 × 3 平台（先试 OCR，不稳再截） | 新截 |
| 首页 | 顶部"可视音箱"Tab | 补截 |

已有可直接复用（62 张转正图中）：全部播放（我喜欢页/歌单详情页）、搜索框/搜索按钮、4 张顶部 Tab 中 4 张、授权登录按钮、AI 平台管理页、网易云平台行等。

---

## 4. 用例文件组织（2026-10-12 改版：一用例一文件一 test 方法）

铁律（CLAUDE.md 规则 8）：每个用例 .py 文件**有且仅有一个 `test_` 方法**；同一场景的数据变体用 `@pytest.mark.parametrize` 挂在该方法上。文件名 = 用例名，保留 `test_` 前缀（pytest 收集 + run_parallel 匹配的硬约束，中文文件名已实测兼容）。唯一例外 `test_case_driver.py`（平台 YAML 用例执行载体）。用例间共用的前置/清理编排沉到 `utils/aw/business/swan_regression.py`（播放器域/内容域/登录域三个 mixin）。

首批已拆分落地（tests/flutter/，26 个用例文件）：

| 文件 | 用例 | 变体矩阵 |
|---|---|---|
| test_设备页卡片切换输出.py | 11 | — |
| test_播放页弹层切换输出.py | 12 | — |
| test_播放全部发起播放.py | 13 | 设备类型 |
| test_点歌名单曲播放.py | 14 | 设备类型 |
| test_循环模式与播放控制.py | 15-22 | 设备类型 × 循环模式 |
| test_进度条跳转.py | 23-24 | 设备类型 × drag/click |
| test_音量调节.py | 25-26 | 设备类型 × 4 动作 |
| test_物理音量键.py | 27-28 | 设备类型 × 方向×长短按 |
| test_底部Tab轮巡.py | 29 | 4 Tab |
| test_顶部Tab切换.py | 30 | 5 Tab |
| test_首页卡片进入.py | 31 | 3 卡片 |
| test_歌单收藏开关.py | 41-43 | 平台 |
| test_歌曲收藏.py | 44-55 | 目标平台 × 来源 |
| test_最近播放.py | 56-68 | 分类 |
| test_搜索.py | 69-72 | 范围 |

存量登录域 12 个（key 定位迁移待拍板）：test_验证码登录 / test_登录态重启持久化 /
test_登出回登录页 / test_登录登出闭环 / test_登录页形态互切 / test_密码登录成功 /
test_错误密码拒绝 / test_首页只读断言 / test_平台页只读断言 / test_设备页只读断言 /
test_播放页开关 / test_收藏分组详情。

未拆分待排（随各域 AW 实现时按本铁律一用例一文件新建）：用例 1-8（启动登录改造）、
9-10（配网）、32-40（授权/平台内容页）、73-76（多房间）。

---

## 5. 待拍板事项（阻塞项）

| # | 事项 | 影响 | 说明 |
|---|---|---|---|
| ① | Driver 层 D1–D3 是否批准 | 配网/音量/热启动 | D1 已拍板（2026-09-24，UI 自动化路线，已实现+冒烟通过）；D2/D3 仍待批 |
| ② | 播放控制键安全约定是否放开 | 用例 16–28 | 知识库标注 loop/prev/next/volume"⛔只断言不点"（探索期约定 + 无任务时点击无反应）。回归必须真点真音箱 |
| ③ | 声学断言降级口径 | 用例 25–28 | "声音如期变大变小"无法自动断言，降级为音量条位置/静音图标 UI 态 |
| ④ | 实体设备 rig | 用例 9–14、19–28、73–76 | 多房间需 ≥3 台 A31 + 3 台 H76D/H76G；切换/播放需 ≥2 台 WiFi 音箱常在线；配网需 1 台**未配网**设备。设备清单谁准备 |
| ⑤ | 三方 App 登录态 | 用例 6–7、32–40、41–68 | 微信/微博/QQ音乐/网易云/酷狗账号须预置在测试手机且不退出（参照 18946151218 的管理方式） |
| ⑥ | 授权用例半自动化程度 | 用例 32–37 | 授权最终一步在三方音乐 App 内，全自动跨 App 抖动大；可选人工辅助或 OCR 兜底 |

---

## 6. 实施顺序建议

```
第一批（无阻塞，纯 App 内）：
  域3 播放控制 → 域4 导航 → 域7 收藏历史 → 域8 搜索

第二批（需三方 App 登录态，事项⑤）：
  域5 授权 → 域6 平台内容页（先让 explorer 补 3 个平台主页 draft）

第三批（需登录域改造 + 新截图）：
  域1 启动登录（A2/A3 改造 + A4/A5 新增）

第四批（需设备 rig + Driver 批准）：
  域2 配网（事项①④）→ 域9 多房间（事项④）→ 设备切换/设备播放分支
```

配套工作并行：aw-element 按 §3 截图（第一批前完成约 12 张核心图），explorer 补平台主页 3 页 draft。

---

## 附：AW 方法总数

| 层 | 数量 | 备注 |
|---|---|---|
| Driver | +2（D1 已实现） | start_action / wifi_current_ssid 原语；connect_wifi 编排在 AndroidBaseAW（见 Base 行） |
| Base | +5 | find_image_rect / wait_toast / long_press_key / region_changed / drag_on_template |
| Business | 36 个方法（9 域，A1–A36） | 含登录域 6 个改造、3 个统一入口、2 个纯前置/清理 |
