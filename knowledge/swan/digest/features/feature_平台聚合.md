---
feature_id: feature_平台聚合
name: "平台聚合"
aliases: [音乐平台, 第三方平台]
status: 草稿
last_updated: 2026-09-10
domains: [音乐平台聚合, 电台/播客, 搜索]
---

# 平台聚合 (feature_平台聚合)

## 功能定义

QQ音乐/网易云/酷狗/Qobuz/AppleMusic 等第三方音乐平台的聚合浏览与授权，电台/播客，站内搜索。

## 包含页面

| 页面 | 角色 | 状态 |
|---|---|---|
| `[[swan_平台页]]` | 平台入口页 /main/platform | 页面 |

缺口：各平台多级页（量大，按平台逐个建）、艺人页、排行榜、全国电台/80/90 电台/城市选择、搜索输入页与结果页（已知 ANR BUG-004 执行 BLOCKED，探索不受影响）。

## 包含 flow

- （待建）flow_平台_浏览平台入口
- （待建）flow_搜索_关键字搜索播放

## 边界与危险操作

- 平台授权管理 `/music_platform/manage-one`：授权/解除授权影响账号状态，只断言页面。
- 平台 VIP 内容播放提示：只断言弹层出现。
- Spotify：UI 入口未确认，先确认存在性。

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/flows/flow_搜索_关键词搜索全链路.md | [[flow_搜索_关键词搜索全链路]] |
| pages/swan_全国电台页.md | [[swan_全国电台页]] |
| pages/swan_城市选择页.md | [[swan_城市选择页]] |
| pages/swan_授权门禁弹层.md | [[swan_授权门禁弹层]] |
| pages/swan_排行榜页.md | [[swan_排行榜页]] |
| pages/swan_搜索结果页.md | [[swan_搜索结果页]] |
| pages/swan_搜索输入页.md | [[swan_搜索输入页]] |
| pages/swan_艺人页.md | [[swan_艺人页]] |
| pages/swan_视频分类页.md | [[swan_视频分类页]] |
| pages/swan_首页电台Tab.md | [[swan_首页电台Tab]] |
| pages/swan_首页音乐Tab.md | [[swan_首页音乐Tab]] |

_自动生成于 2026-09-14 13:26_
<!-- backlinks:end -->