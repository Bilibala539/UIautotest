---
page_id: swan_设备详情页
name: "设备详情页（全屏播放页·设备入口形态）"
aliases: [device_detail, 设备详情, 卡片详情页]
route: null               # 无独立路由：即 full_player_page，非独立页面
status: 草稿
last_updated: 2026-09-28
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 设备详情页 (swan_设备详情页)

## 页面概述

新构建（test/profile 5.3.1，2026-09-24 实测，账号 13555555555）设备页点 Wi-Fi
设备卡（状态行或卡体任意非按钮区）进入的页面。**核心结论：这不是独立详情页，
就是全屏播放页 `full_player_page` 本身**（与 [[swan_播放页]] 同根节点、同控制区），
叠加设备上下文：页头显示当前输出设备名 + 右上角切换设备弹层入口，
媒体区显示该输出设备正在播放的任务，徽章行带音源平台/VIP/连接良好三标。
即「设备卡 → 播放页」在新构建已融合为一页，不存在单独的设备详情 DOM。

原始件：`explorer_output/aw_explorer_tmp/devdetail/`（dump/OCR/截图/log.jsonl）。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 页面根节点 | 出现 | `wait_accessibility(full_player_page)`（desc 含 `连接良好`） | 已进入本页 |
| 输出设备名 | 出现 | `wait_accessibility(player_device_name)`，desc=输出设备名（如 `HiVi M300MKII`） | 设备上下文已加载（新键，2026-09-24 dump） |
| 设备切换钮 | 出现 | `wait_accessibility(player_device_button)`（右上角） | 弹层入口就位 |
| 连接徽章 | 出现 | OCR `连接良好`（y≈1229 徽章行） | 设备连接态已回显 |

⚠️ 语义树瞬时失败频发（动画中 dump 缺节点，player_device_name 等 key 偶发
读不到）：断言须带重试（wait_accessibility 自带轮询），勿单次 dump 定生死。

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_设备页]]` | 当前输出设备卡状态行：OCR「连接良好」行中心（落在 `wifi_device_selected_<UUID>` 容器内） | click | 见「生效断言」 |
| `[[swan_设备页]]` | 卡体任意非按钮空白区（同上容器 bounds 内；2026-09-24 实测 (620,475) 与状态行同效） | click | 见「生效断言」 |
| `[[swan_首页]]` 等任意带底栏页 | `bottom_player` 封面/标题区（左半条） | click | 见「生效断言」（普通播放页入口） |

⚠️ **返回不可假设落点 tab**：press_back 正常回落来源设备页；但 2026-09-24
一次实测回落到平台页（导航历史残留）。自动化收尾一律 `back_to_tab_shell()` +
显式点目标 tab，勿断言"back 必回设备页"。

## 关键元素

| 元素 | locator（key / OCR 文案） | 类型 | 操作 | 成功断言 | 验证状态 |
|---|---|---|---|---|---|
| 页面根节点 | `full_player_page`（resource-id，desc=`VIP\n连接良好\nVIP歌曲只支持试听`） | 静态 | 只读判据 | — | 已验证（2026-09-24 dump） |
| 收起按钮 | `player_dismiss_button`（左上 [0,64][128,176]） | 静态 | click | 回 tab 壳 | 已验证（key 沿用） |
| **输出设备名** | `player_device_name`（resource-id，**新键**）desc=`HiVi M300MKII` [128,91][592,149] | 静态 | 只读 | 设备名=当前输出 | 已验证（输出=手机扬声器时 desc 变 `扬声器`） |
| **设备切换钮** | `player_device_button`（resource-id）右上 [592,64][720,176] | 静态 | click | `[[swan_切换设备弹层]]` 打开 | 已验证（语义键+图模板 SWAN_PLAYER_DEVICE_BTN 双通道实测） |
| 封面区 | 无键 [46,203][674,831] click=True | 静态 | 未测（勿点） | — | 未验证 |
| 歌名/艺人 | `player_title` / `player_artist` | 静态 | 只读 | — | 已验证 |
| 歌词占位 | desc=`此歌曲暂无歌词内容，请欣赏` | 静态 | 只读 | — | 已验证 |
| 徽章行 | OCR `QQ音乐` `VIP` `连接良好`（y≈1229；左端另有无键 `0%` 节点 [0,1227][81,1323]，语义不可读） | 静态 | 只读 | 连接良好=设备在线 | 已验证 |
| 进度条 | `player_progress_bar` desc=`00:00\n01:00`（VIP 试听 1:00 口径；OCR 实测 00:14 在走=试听自动播放） | 静态 | 只读 | — | 已验证 |
| 控制行 | `player_loop_mode_button` / `player_previous_button` / `player_play_pause_button` / `player_next_button` / `player_queue_button`（y 1346-1469） | 静态 | ⛔ 播放控制禁点 | — | 已验证（存在性） |
| 底行 | `player_volume_button`（⛔ 真机音量）+ 两枚无键图标钮 [318,1490][402,1574]、[501,1490][586,1574]（身份未测） | 静态 | ⛔ 禁点 | — | 未验证 |

### 输出切换联动（2026-09-24 往返实测）

- 输出 `HiVi M300MKII` → `手机扬声器`：经 `player_device_button` 弹层点行后，
  **页头变 `扬声器`、曲目区清空**（Swan 占位封面 + `- -` + 00:00/00:00），
  弹层自动关闭、停留本页；系统弹「是否忽略电池优化？」对话框（取消/忽略，
  点「忽略」放行后台音频后切换继续）。
- 切回 `HiVi M300MKII`：曲目/艺人/徽章/进度（00:14/01:00）全部恢复，
  底栏播放条 desc 恢复 `HiVi M300MKII\n多远都要在一起 - G.E.M.邓紫棋`。

### 用例 11「点击设备卡片切换输出设备」自动化路径结论

设备卡点击在新构建**不切换输出**（进本页）。正确路径二选一：
1. **短路径（推荐）**：任意带底栏页 → 底栏最右 cast 图标 [608,1386][688,1466]
   （无键无文案，需图模板）→ 直开 `[[swan_切换设备弹层]]` → 点目标设备行。
   2026-09-24 实测 cast 图标直达弹层（multiroom_sheet 出现，不经过本页）。
2. **长路径**：设备卡 → 本页 → `player_device_button`（语义键）→ 弹层 → 点行。

弹层点行后勾选生效断言：当前输出设备行**升至列表首位且无单选圆点**（旧 KB
口径沿用，2026-09-24 复验）；行勾选态图 SWAN_DEVICE_SHEET_CHECKED 待重截。

## 页面布局

```
┌────────────────────────────┐
│ [<]  HiVi M300MKII   [设备钮] │  player_dismiss_button / player_device_name / player_device_button
│                            │
│        ┌──────────┐        │
│        │  专辑封面   │        │  [46,203][674,831]
│        └──────────┘        │
│   多远都要在一起              │  player_title
│   G.E.M.邓紫棋              │  player_artist
│  此歌曲暂无歌词内容，请欣赏     │
│                            │
│ QQ音乐  VIP  连接良好  [0%]   │  徽章行（y≈1229）
│ 00:14 ──────●────── 01:00   │  player_progress_bar（VIP试听1:00）
│ ⟳   ⏮   ⏯   ⏭   ≡         │  loop/prev/play/next/queue
│  🔊      [+]      ♡        │  volume + 两枚无键钮
└────────────────────────────┘
```

## 对 [[swan_设备页]] 的勘误与增补（转正时合入 pages/swan_设备页.md）

2026-09-24 新构建（5.3.1）dump 实测，与现 KB（2026-09-08 口径）差异：

1. **设备清单变化**：HiVi M5A_003C 不再在列；WIFI 区 = HiVi M300MKII（深色当前输出卡）
   + Libretto_0E00（白色卡），UUID 分别为
   `FF31F012_A286_3C8E_FB6C_CC84FF31F012` / `FF311BB6_477E_9FD6_13A6_0E00FF31F012`。
2. **新增整卡可点击节点**：当前输出设备卡被 `wifi_device_selected_<UUID>`
   （desc=`连接良好\n<歌名>\n<艺人>`，click=True）覆盖（旧 KB 记其为"仅选中态出现的
   动态键"——现证实它就是"当前输出态"整卡容器，点击=进设备详情/播放页，不切换输出）。
3. **新增独立设备名节点** `wifi_device_name_<UUID>`（desc=设备名，click=False）；
   `wifi_device_settings_<UUID>`（click=True）仍覆盖设备名行 = 设置入口（⛔ 内含
   删除设备风险，维持禁点）。
4. **卡片新增媒体信息区**：当前输出卡显示在播歌名/艺人/封面；空闲设备显示 `- - : - - -`。
5. **OCR 口径**：卡标题 OCR 为 `HiViM300MKII>`（空格丢失+尾随箭头），状态行读作
   `·连接良好`（带前导点）——select_device 的 compact 归一化继续有效。
6. **本机分区结构**（下滑后）：本机头 + 扬声器卡（desc=`扬声器\n - - : - - -\n - - : - - -`，
   click=True，**无 resource-id**）+ **Apple Music 分区**（头 + 扬声器卡
   desc=`扬声器\n连接 Apple Music\n连接 Apple Music`，click=True）+ 低音炮分区
   （头 + 「添加低音炮」卡 ⛔ 配网流程勿点）+ DSP 分区头。本机扬声器卡点击
   **不进详情页**，而是触发系统「是否忽略电池优化？」对话框（切换到本机输出的前置）。
7. **空态变体**（2026-09-28 复核，Wi-Fi 音箱离线时）：WIFI 区变空态卡
   desc=`暂无WIFI设备\n暂无歌曲\n暂无艺术家`（无任何 UUID 键）；本机扬声器卡转深色
   （=当前输出态样式）；底栏 desc=`扬声器\n - - `，且播放/队列按钮 click=False
   （无内容时禁用）、cast 钮仍 click=True。
8. 底栏播放条右侧三钮（播放/队列/cast [448-688,1386-1466]）均无键无文案；
   cast 钮直开切换设备弹层（见上），另两钮身份未测。

## 功能关联

- 本页即 `[[swan_播放页]]`（同根 full_player_page），设备上下文=页头设备名+连接徽章
- 设备切换走 `[[swan_切换设备弹层]]`（player_device_button / 底栏 cast 直达）
- 上游：`[[swan_设备页]]`（Wi-Fi 设备卡状态行/卡体）
- feature：`[[feature_播放器]]`、`[[feature_设备管理]]`

## 缺口

- 封面区点击行为、底行两枚无键图标钮身份未测（疑似收藏/更多，勿盲点）
- `0%` 无障碍节点语义未解（音量浮层残片？）
- 返回落 tab 残留态（back→平台页）成因未深究，自动化已按"勿假设"规避
- 弹层行首勾选圆点选中态图 SWAN_DEVICE_SHEET_CHECKED 待重截（旧图缺失）
- 底栏 cast 图标无键无文案，需 aw-element 截图登记（建议名
  `swan_底栏_切换设备钮.png`）
