---
page_id: swan_选择歌单页
name: "选择歌单"
aliases: [select_playlist]
route: "/player/select-playlist"
status: 已验证
last_updated: 2026-09-14
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 选择歌单 (swan_选择歌单页)

## 页面概述

⛔ **入口路径未知**（2026-09-11 R3 归因修正）。`select_playlist/`（`/player/select-playlist`）
预期入口形态为「收藏/加入歌单」动作的目标选择页。原记"疑似歌曲收藏菜单/批量操作页下游"
已被证伪：.229 全量 dump 零命中，.144 已排除批量操作页路径（见 [[swan_批量操作页]]），
**与账号数据量无关**。待后续复验。

## 生效断言

未进入，无断言。route 来自功能地图，未经真机验证。

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| （未知；已排除批量操作页路径与账号数据量归因） | — | — | — |

## 关键元素

未进入，无元素。

## 页面布局

未知。

## 功能关联

- 所属 feature：`[[feature_收藏管理]]`
- 相关：`[[swan_批量操作页]]`、`[[swan_歌单页]]`（歌单数据同源）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_收藏管理.md | [[feature_收藏管理]] |
| pages/swan_批量操作页.md | [[swan_批量操作页]] |
| pages/swan_统一音乐库页.md | [[swan_统一音乐库页]] |

_自动生成于 2026-09-14 13:38_
<!-- backlinks:end -->
