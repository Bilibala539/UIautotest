---
page_id: swan_批量操作页
name: "批量操作"
aliases: [bulk_operate]
route: "/player/bulk-operate"
status: draft
last_updated: 2026-09-10
type: screen
package_name: com.swan.network
activity: null
orientation: portrait
---

# 批量操作 (swan_批量操作页)

## 页面概述

⛔ **入口受限**：`bulk_operate_page.dart`（`/player/bulk-operate`，位于 unified_music/ 目录下）
未找到 UI 入口。预期入口形态为歌曲列表的多选/批量管理模式（长按歌曲或列表页「管理/多选」按钮），
而本账号所有歌曲列表均为空（歌单 0 首、我喜欢 0 首、播放历史空），且第三方平台未授权，
不存在可长按的歌曲行。待 Wave 2b 有歌曲数据的账号复验。

## 生效断言

未进入，无断言。route 来自功能地图，未经真机验证。

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| （未知，疑似 `[[swan_统一音乐库页]]` 或歌单详情歌曲区） | — | — | — |

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

_自动生成于 2026-09-10 14:19_
<!-- backlinks:end -->
