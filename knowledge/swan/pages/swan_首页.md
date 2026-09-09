# swan_首页

> 状态：page（2026-09-08 登录成功后真机 dump，verify 复验转正；只覆盖首屏，滚动区/各 tab 待补）
> 数据来源：验证码登录成功后实机 dump

## 页面概述

登录成功落地页。当前账号（13555555555）首屏包含第三方音乐源入口、我喜欢/歌单/AI 卡片、
最近播放、底部播放条与全局 tab 栏。未授权时推荐区提示"您还未授权无法为您推荐音乐"。

## 进入方式

- 登录成功后自动进入
- 任意页面点 `tab_recommend`（首页）

## 关键元素（来源：uiautomator dump）

| key | 文案/说明 | clickable | 备注 |
|---|---|---|---|
| `tab_recommend` | 首页 tab | ✅ | |
| `tab_platform` | 平台 tab | ✅ | |
| `tab_device` | 设备 tab | ✅ | |
| `tab_me` | 我的 tab | ✅ | 登录态判据 |
| `bottom_player` | 底部播放条（"扬声器 - -"） | ✅ | 点进播放页 |

无 key 的 OCR 文本元素：网易云练习/网易云音乐/酷狗音乐/Apple Music/Qobuz（音源入口）、
我喜欢/歌单/AI 卡片、最近播放（已播歌曲/已播歌手/已播专辑）、立马授权。


### 元素截图（image/flutter，2026-09-08 aw-element 采集 + verify 复验转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| bottom_player 播放条整体（⚠️ 含当前曲目名区，曲目变化时文字区会变） | `SWAN_BOTTOM_PLAYER_BAR` | image/flutter/swan_底部播放条.png |
## 页面布局（首屏）

```
┌────────────────────────┐
│   [音源入口横排: 网易云/酷狗/Apple Music/Qobuz] │
│ ┌─────────┐ ┌─────────┐ │
│ │我喜欢    │ │ 歌单    │ │
│ │暂无歌曲  │ ├─────────┤ │
│ │         │ │ AI     │ │
│ └─────────┘ └─────────┘ │
│ 最近播放                  │
│ [已播歌曲][已播歌手][已播专辑]│
│ ┌── bottom_player ────┐ │
│ │ 扬声器  - -  [控制键] │ │
│ └─────────────────────┘ │
│ 首页 | 平台 | 设备 | 我的  │  tab_recommend/platform/device/me
└────────────────────────┘
```

## 关联

- [[swan_验证码输入页]]（登录进入）
- [[swan_播放页]]（点 bottom_player，已探索）
- [[swan_平台页]]（点 tab_platform，已探索）
- [[swan_设备页]]（点 tab_device，已探索）
- [[swan_我的页]]（点 tab_me，已探索）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| pages/swan_平台页.md | [[swan_平台页]] |
| pages/swan_我的页.md | [[swan_我的页]] |
| pages/swan_播放页.md | [[swan_播放页]] |
| pages/swan_收藏分组详情页.md | [[swan_收藏分组详情页]] |
| pages/swan_收藏页.md | [[swan_收藏页]] |
| pages/swan_设备页.md | [[swan_设备页]] |
| pages/swan_验证码登录页.md | [[swan_验证码登录页]] |
| pages/swan_验证码输入页.md | [[swan_验证码输入页]] |

_自动生成于 2026-09-09 08:29_
<!-- backlinks:end -->