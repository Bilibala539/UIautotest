# swan_首页

> 状态：page（2026-09-08 登录成功后真机 dump，verify 复验转正；只覆盖首屏，滚动区/各 tab 待补）
> 数据来源：验证码登录成功后实机 dump

## 页面概述

登录成功落地页。当前账号（13555555555）首屏包含第三方音乐源入口、我喜欢/歌单/AI 卡片、
最近播放、底部播放条与全局 tab 栏。未授权时推荐区提示"您还未授权无法为您推荐音乐"。

> ⚠️ **推荐 Tab 内容区存在服务端动态布局轮换（2026-09-10 aw-verify 实测）**：
> 同一登录态下，推荐 Tab 首屏在两种布局间**间歇切换**（非客户端版本变化，疑服务端配置下发，
> 下拉刷新不保证触发切换）：
> - **完整布局**：搜索条「跨平台搜索音乐」+ 音源图标行 + 我喜欢｜歌单｜AI 卡片行 + 最近播放
>   （「歌单」卡片唯一出现形态，是 `[[swan_歌单页]]` 的入口）
> - **紧凑布局**：仅 我喜欢｜AI 卡片行 + 最近播放（**无「歌单」卡**）
>
> 自动化影响：依赖「歌单」卡片/搜索条的断言会因轮换而间歇失败，进歌单页前必须
> dump 检查 desc='歌单' 卡片是否存在，不存在则下拉刷新/等待轮换回完整布局。

## 进入方式

- 登录成功后自动进入
- 任意页面点 `tab_recommend`（首页）

## 关键元素（来源：uiautomator dump）

| 无障碍键 | 文案/说明 | 可点击 | 备注 |
|---|---|---|---|
| `tab_recommend` | 首页 tab | ✅ | |
| `tab_platform` | 平台 tab | ✅ | |
| `tab_device` | 设备 tab | ✅ | |
| `tab_me` | 我的 tab | ✅ | 登录态判据 |
| `bottom_player` | 底部播放条（"扬声器 - -"） | ✅ | 点进播放页 |

无无障碍键 的 OCR 文本元素：网易云练习/网易云音乐/酷狗音乐/Apple Music/Qobuz（音源入口）、
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
- [[swan_歌单页]]（推荐 Tab 歌单卡片，2026-09-10 Wave2）
- [[swan_我喜欢页]]（推荐 Tab 我喜欢卡片，2026-09-10 Wave2）
- [[swan_播放历史页]]（推荐 Tab 已播歌曲卡片，2026-09-10 Wave2）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_导航框架.md | [[feature_导航框架]] |
| digest/flows/flow_导航_四tab切换.md | [[flow_导航_四tab切换]] |
| digest/flows/flow_导航_迷你播放器展开.md | [[flow_导航_迷你播放器展开]] |
| digest/flows/flow_搜索_关键词搜索全链路.md | [[flow_搜索_关键词搜索全链路]] |
| digest/flows/flow_歌单_新建歌单弹窗开关.md | [[flow_歌单_新建歌单弹窗开关]] |
| digest/flows/flow_登录_验证码登录全链路.md | [[flow_登录_验证码登录全链路]] |
| pages/swan_平台页.md | [[swan_平台页]] |
| pages/swan_我喜欢页.md | [[swan_我喜欢页]] |
| pages/swan_我的页.md | [[swan_我的页]] |
| pages/swan_播放历史页.md | [[swan_播放历史页]] |
| pages/swan_播放页.md | [[swan_播放页]] |
| pages/swan_收藏分组详情页.md | [[swan_收藏分组详情页]] |
| pages/swan_收藏页.md | [[swan_收藏页]] |
| pages/swan_歌单页.md | [[swan_歌单页]] |
| pages/swan_设备页.md | [[swan_设备页]] |
| pages/swan_首页AITab.md | [[swan_首页AITab]] |
| pages/swan_首页可视音箱Tab.md | [[swan_首页可视音箱Tab]] |
| pages/swan_首页电台Tab.md | [[swan_首页电台Tab]] |
| pages/swan_首页音乐Tab.md | [[swan_首页音乐Tab]] |
| pages/swan_验证码登录页.md | [[swan_验证码登录页]] |
| pages/swan_验证码输入页.md | [[swan_验证码输入页]] |

_自动生成于 2026-09-11 13:44_
<!-- backlinks:end -->