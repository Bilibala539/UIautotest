---
page_id: swan_批量操作页
name: "批量操作"
aliases: [bulk_operate]
route: "/player/bulk-operate"
status: 已验证
last_updated: 2026-09-14
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 批量操作 (swan_批量操作页)

## 页面概述

⛔ **入口未知**（2026-09-11 R3 归因修正）。`bulk_operate_page.dart`（`/player/bulk-operate`，
位于 unified_music/ 目录下）未找到 UI 入口。**归因修正**：KB 原记"本账号无歌曲数据无法触发"
已被 .144 证伪——已授权账号（1160 首收藏）长按歌曲行**仍无多选态** ⇒ 入口不在歌曲行长按路径，
与账号数据量、授权状态无关。预期入口形态仍为歌曲列表的多选/批量管理模式，待后续复验。

## 生效断言

未进入，无断言。route 来自功能地图，未经真机验证。

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| （未知；已排除歌曲行长按路径与账号数据量归因） | — | — | — |

## 关键元素

未进入，无元素。

## 页面布局

未知。

## 功能关联

- 所属 feature：`[[feature_收藏管理]]`
- 相关：`[[swan_统一音乐库页]]`、`[[swan_选择歌单页]]`（批量把歌曲加入歌单的下游）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_收藏管理.md | [[feature_收藏管理]] |
| pages/swan_统一音乐库页.md | [[swan_统一音乐库页]] |
| pages/swan_选择歌单页.md | [[swan_选择歌单页]] |

_自动生成于 2026-09-14 13:38_
<!-- backlinks:end -->
