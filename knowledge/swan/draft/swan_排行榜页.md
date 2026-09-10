---
page_id: swan_排行榜页
name: "排行榜"
aliases: [rank_list, 榜单]
route: "/music_platform/rank-list"
status: draft
last_updated: 2026-09-10
type: screen
package_name: com.swan.network
activity: null
orientation: portrait
---

# 排行榜页 (swan_排行榜页)

## 页面概述

❌ **不可达**。排行榜页（`/music_platform/rank-list`）在未授权账号下无可见入口。
2026-09-10 Wave4 排查过的入口面：

1. 首页音乐 Tab：内容全部为平台区块（QQ音乐/网易云/酷狗/Apple Music/Qobuz 歌单宫格），
   无独立「排行榜」区块；平台区块标题/歌单卡均弹 `[[swan_授权门禁弹层]]` 变体 B
2. 平台页·音乐分类：六平台行（QQ音乐/Spotify/网易云/酷狗/Apple/Qobuz）行本体不可点
   （点击无反应，仅右侧图标可点＝授权入口，未点）
3. 平台页·电台分类：三个 FM 电台入口（推测含 Qobuz 奖榜/榜单的多级页同族）均弹门禁变体 A
4. 搜索结果页：空态（搜索源未授权）

推断：排行榜页挂在各平台多级页内（如 Qobuz 首页「奖榜」、Apple Music「榜单」分类），
需平台授权后才可见。

## 生效断言

未进入，无断言。route 来自功能地图（App dev@4d1ed7b），未经真机验证。

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| （未知，推测平台多级页内） | — | — | ⚠️ 平台多级页被授权门禁拦截 |

## 关键元素

未进入，无元素。待授权账号补全。

## 页面布局

未知。

## 功能关联

- 所属 feature：`[[feature_平台聚合]]`（音乐平台聚合域）
- 阻断方：`[[swan_授权门禁弹层]]`
