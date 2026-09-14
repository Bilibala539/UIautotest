---
feature_id: feature_导航框架
name: "导航框架"
aliases: [tab壳, 主框架]
status: 草稿
last_updated: 2026-09-10
domains: [主框架与导航, 首页]
---

# 导航框架 (feature_导航框架)

## 功能定义

登录后的底部四 Tab 壳（推荐/音乐/设备/我的）+ 首页五顶 Tab 容器（推荐/音乐/电台/AI/可视音箱）+ 底栏迷你播放器包裹规则。约 130 条命名路由；Tab 页有缓存与可见性暂停。

## 包含页面

| 页面 | 角色 | 状态 |
|---|---|---|
| `[[swan_首页]]` | 首页容器+推荐 Tab | 页面 |
| `[[swan_首页音乐Tab]]` / `[[swan_首页电台Tab]]` / `[[swan_首页AITab]]` / `[[swan_首页可视音箱Tab]]` | 首页五顶 Tab（Wave1 已建页） | 已验证 |
| `[[swan_我的页]]` | 我的 Tab | 页面 |
| `[[swan_平台页]]` | 平台 Tab（实为 /main/platform） | 页面 |
| `[[swan_设备页]]` | 设备 Tab | 页面 |
| `[[swan_AI对话页]]` | AI 角色对话页（AI Tab 角色卡进入） | 草稿 |

注：`[[swan_播放页]]` 2026-09-10 Wave2 起归 `[[feature_播放器]]`（播放域页面成簇后拆分）。

缺口：音乐权益初始化页待确认。

## 包含 flow

- （待建）flow_导航_四tab切换
- （待建）flow_导航_迷你播放器展开全屏

## 边界与危险操作

- 无。纯导航，可自由点击。

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/flows/flow_导航_四tab切换.md | [[flow_导航_四tab切换]] |
| digest/flows/flow_导航_迷你播放器展开.md | [[flow_导航_迷你播放器展开]] |
| pages/swan_AI对话页.md | [[swan_AI对话页]] |
| pages/swan_Vision域不可达页.md | [[swan_Vision域不可达页]] |
| pages/swan_所有角色页.md | [[swan_所有角色页]] |
| pages/swan_首页AITab.md | [[swan_首页AITab]] |
| pages/swan_首页可视音箱Tab.md | [[swan_首页可视音箱Tab]] |
| pages/swan_首页电台Tab.md | [[swan_首页电台Tab]] |
| pages/swan_首页音乐Tab.md | [[swan_首页音乐Tab]] |

_自动生成于 2026-09-14 15:41_
<!-- backlinks:end -->