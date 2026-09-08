# swan_player_page（播放页）

> 状态：draft（2026-09-08 真机 dump + OCR 验证，仅进入观察，未操作播放控制）
> 数据来源：首页点 bottom_player 实机 dump；截图 explorer_output/screenshots/swan/swan_player_page

## 页面概述

全屏播放页。当前无播放任务：标题区为"- - / ---"，设备名"扬声器"，进度 00:00/00:00，
音量 0%。底部控制条：循环模式/上一首/播放暂停/下一首/播放队列，下方音量条。
左上角收起按钮返回原页面。

## 进入方式

- 任意带 bottom_player 的页面（首页/平台/设备/我的）点 `bottom_player`

## 关键元素（来源：uiautomator dump）

| key | 文案/说明 | clickable | 备注 |
|---|---|---|---|
| `full_player_page` | 页面根节点（文本"扬声器 00:00 00:00"） | ❌ | 页面判据 |
| `player_dismiss_button` | 左上角收起/返回 | ✅ | 返回进入前页面 |
| `player_device_button` | 右上角设备切换 | ✅ | 未点 |
| `player_title` | 歌名/歌手区（"- - / ---"） | ❌ | |
| `player_loop_mode_button` | 循环模式 | ❌（dump 标记） | ⛔ 控制类，只记录 |
| `player_previous_button` | 上一首 | ❌（dump 标记） | ⛔ 只记录 |
| `player_play_pause_button` | 播放/暂停 | ❌（dump 标记） | ⛔ 只记录 |
| `player_next_button` | 下一首 | ❌（dump 标记） | ⛔ 只记录 |
| `player_queue_button` | 播放队列 | ❌（dump 标记） | ⛔ 只记录 |
| `player_volume_button` | 音量（OCR "0%"） | ✅ | ⛔ 不改音量 |

注：控制类按钮（loop/previous/play_pause/next/queue）在 dump 中 clickable=False
（Flutter 手势未暴露 clickable），但 key 稳定，可经 `click_accessibility` 定位中心点——
测试时是否可点需 verify 阶段确认。

无 key 的 OCR 文本元素：`0%`（音量值）、进度 `00:00 / 00:00`、
底部两个无 key 节点 [336,1479][384,1527] / [501,1479][549,1527]（疑音量滑轨端点）。

## 页面布局

```
┌────────────────────────┐
│ [✕]      扬声器   [设备]   │  player_dismiss_button / player_device_button
│                         │
│        - -              │  player_title
│        ---              │
│   （专辑封面区）            │
│ 00:00 ———————— 00:00     │
│ [循环][上一首][播放][下一首][队列] │
│ 🔊 ———— 0% ————          │  player_volume_button
└────────────────────────┘
```

## 缺口

- 播放/切歌/音量等控制一律未实测（真机音箱安全约束）
- player_title 有内容时的布局、队列页未探索

## 关联

- [[swan_home_page]]（bottom_player 进入，player_dismiss_button 返回）
