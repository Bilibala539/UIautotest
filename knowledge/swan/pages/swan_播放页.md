---
page_id: swan_播放页
name: "播放页"
aliases: [全屏播放页, full_player, player]
route: "/player"
status: 页面
last_updated: 2026-09-14
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 播放页 (swan_播放页)

## 页面概述

全屏播放页（`unified_player_widget.dart`），从任意页面的底部播放条 `bottom_player` 进入，
`player_dismiss_button` 收起后回到进入前的页面。页面展示：当前输出设备名（无任务时 OCR"扬声器"）、
曲目名/歌手区（`player_title`，无任务时"- - / ---"）、进度条（00:00/00:00）、
五键播放控制条（循环/上一首/播放暂停/下一首/队列）与音量条。

⚠️ 本页所有探索均基于**无播放任务**状态（2026-09-10 Wave2 实测：本账号所有第三方音乐平台未授权，
AI 点歌也被拒"音乐服务需要授权"，无法建立播放任务）。有播放任务时的布局/队列/歌词待授权账号复验。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 页面根节点 | 出现 | `wait_accessibility(full_player_page)` | 进入播放页 |
| 收起按钮 | 出现 | `image_exists(SWAN_PLAYER_DISMISS_BTN)` | 顶栏已渲染（已转正图） |
| 播放/暂停圆钮 | 出现 | `image_exists(SWAN_PLAYER_PLAY_PAUSE_BTN)` | 无任务时为 ▶ 态（已转正图） |
| 进度时间 | 出现 | OCR"00:00"（无任务态） | 进度区已渲染（有任务时为动态时间，勿作固定断言） |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_首页]]` | `bottom_player`（resource-id） | click | 见「生效断言」 |
| `[[swan_我的页]]` / `[[swan_平台页]]` / `[[swan_设备页]]` | `bottom_player`（resource-id） | click | 同上（transitions 中部分仍标 pending） |
| `[[swan_歌单详情页]]` / `[[swan_收藏分组详情页]]` / `[[swan_我喜欢页]]` 等 push 页 | `bottom_player`（resource-id，贴底） | click | 同上 |

## 关键元素

> 控制类按钮（loop/previous/play_pause/next/queue/volume）按安全约定**只记录不点击**；
> dump 中 可点击=False 是 Flutter 手势未暴露所致，实际可点性由 verify 确认。

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 页面根节点 | `full_player_page`（resource-id，desc 含设备名+时间） | 动态 | 只读判据 | — | 动态-不截图 | 已验证 |
| 收起/返回 | `player_dismiss_button`（resource-id） | 静态 | click | 回到进入前页面 | `SWAN_PLAYER_DISMISS_BTN` | 已验证 |
| 输出设备切换 | `player_device_button`（resource-id，右上角） | 静态 | click | `[[swan_切换设备弹层]]` 生效断言（`multiroom_sheet`） | 已截 `SWAN_PLAYER_DEVICE_BTN`（image_ai 草稿，2026-09-10） | 草稿 |
| 曲目名/歌手 | `player_title`（key；无任务 desc"- -\n---"） | 动态 | 只读 | — | 动态-不截图 | 已验证 |
| 进度条 + 时间 | OCR"00:00 / 00:00"（无无障碍键） | 动态 | 只读 | — | 动态-不截图 | 草稿 |
| 循环模式 | `player_loop_mode_button`（resource-id） | 静态 | ⛔ 只断言不点 | — | 待截 | 草稿 |
| 上一首 | `player_previous_button`（resource-id） | 静态 | ⛔ 只断言不点 | — | 待截 | 草稿 |
| 播放/暂停 | `player_play_pause_button`（resource-id） | 静态 | ⛔ 只断言不点（真实音箱安全约定） | `image_exists(SWAN_PLAYER_PLAY_PAUSE_BTN)` | 已有（▶ 态） | 已验证 |
| 下一首 | `player_next_button`（resource-id） | 静态 | ⛔ 只断言不点 | — | 待截 | 草稿 |
| 播放队列 | `player_queue_button`（resource-id，右下） | 静态 | ⛔ 只断言不点 | ⚠️ 无播放任务时点击**无任何反应**（2026-09-10 实测），队列 弹层 待有任务账号复验 | 待截 | 草稿 |
| 音量 | `player_volume_button`（resource-id，OCR"0%"） | 静态 | ⛔ 只断言不点（不改音量） | — | 待截 | 草稿 |
| 输出设备名 | OCR"扬声器"（页顶中央） | 动态 | 只读 | — | 动态-不截图 | 草稿 |

### 元素截图（image/flutter，2026-09-08 aw-element 采集 + verify 复验转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 播放/暂停圆钮（无播放任务时的 ▶ 态） | `SWAN_PLAYER_PLAY_PAUSE_BTN` | image/flutter/swan_播放页_播放暂停按钮.png |
| 左上角收起按钮 | `SWAN_PLAYER_DISMISS_BTN` | image/flutter/swan_播放页_收起按钮.png |

### 元素截图（image/flutter，2026-09-10 aw-element Wave2 采集，已转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 右上角输出设备切换图标 | `SWAN_PLAYER_DEVICE_BTN` | image/flutter/swan_播放页_设备切换按钮.png |

## 页面布局

```
┌────────────────────────┐
│ [✕]      扬声器   [设备]   │  player_dismiss_button / 设备名(dynamic) / player_device_button
│                         │
│        - -              │  player_title（dynamic，无任务占位）
│        ---              │
│   （专辑封面区）            │  dynamic
│ 00:00 ———————— 00:00     │  进度条（dynamic）
│ [循环][上一首][播放][下一首][队列] │  五键控制条
│ 🔊 ———— 0% ————          │  player_volume_button（dynamic 音量值）
└────────────────────────┘
```

## Wave 2 探索发现（2026-09-10，无播放任务态）

- **播放队列入口**：`player_queue_button` 存在且 key 稳定，但无播放任务时点击无任何 UI 反应
  （页面 dump 前后完全一致）。`current_queue_bottom_sheet.dart` 的触发疑似依赖非空队列。
- **歌词入口**：点 `player_title` 区域（封面/标题中部）无反应；页面无其它疑似歌词入口节点。
  `lyric_view.dart` 疑似为播放中状态下封面区的展开形态，待有任务账号复验。
- **输出设备切换入口**：`player_device_button` → `[[swan_切换设备弹层]]`（`multiroom_sheet`，
  列出 Libretto_0E00 / Maestro1100_A20C / HiVi M300MKII / 手机扬声器 / Apple Music）。
  ⛔ 列表含真实音箱，自动化禁止选择，只断言弹层出现。
- 播放无法建立的原因链：首页音乐 Tab 歌单卡片 → "请先登录 QQ音乐…授权登录"弹层（⛔ 授权类）；
  电台 Tab 电台行 → "添加新平台…添加"弹层（⛔）；AI 对话点歌 → 回复"音乐服务需要授权，
  请到音乐页面完成授权后再试"。三条路都被授权门禁挡住。

## 功能关联

- 所属 feature：`[[feature_播放器]]`（2026-09-10 新建，原属 feature_导航框架；理由：播放域页面
  已成簇——播放页/切换设备弹层/（待解锁）队列与歌词，独立成 feature 便于用例归属）
- 上游：`[[swan_首页]]`、`[[swan_我的页]]`、`[[swan_平台页]]`、`[[swan_设备页]]`（bottom_player 进入）
- 下游：`[[swan_切换设备弹层]]`；（入口存在但未解锁）播放队列 弹层、歌词视图

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_导航框架.md | [[feature_导航框架]] |
| digest/features/feature_播放器.md | [[feature_播放器]] |
| digest/flows/flow_导航_迷你播放器展开.md | [[flow_导航_迷你播放器展开]] |
| pages/swan_切换设备弹层.md | [[swan_切换设备弹层]] |
| pages/swan_我喜欢页.md | [[swan_我喜欢页]] |
| pages/swan_播放历史页.md | [[swan_播放历史页]] |
| pages/swan_歌单详情页.md | [[swan_歌单详情页]] |
| pages/swan_歌单页.md | [[swan_歌单页]] |
| pages/swan_首页.md | [[swan_首页]] |
| pages/swan_首页AITab.md | [[swan_首页AITab]] |
| pages/swan_首页可视音箱Tab.md | [[swan_首页可视音箱Tab]] |
| pages/swan_首页电台Tab.md | [[swan_首页电台Tab]] |
| pages/swan_首页音乐Tab.md | [[swan_首页音乐Tab]] |

_自动生成于 2026-09-14 13:38_
<!-- backlinks:end -->
