---
page_id: swan_统一音乐库页
name: "统一音乐库"
aliases: [unified_music]
route: "/player/unifiedMusic"
status: 已验证
last_updated: 2026-09-10
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 统一音乐库 (swan_统一音乐库页)

## 页面概述

⛔ **入口受限**：`unified_music_page.dart`（约 4900 行，`/player/unifiedMusic`）在真机全路径排查
未找到 UI 入口。2026-09-10 Wave2 排查过的入口面：首页推荐 Tab（音源卡/我喜欢/歌单/AI/最近播放）、
首页音乐 Tab（歌单宫格，第三方歌单被授权弹层拦截）、歌单页（平台 Tab 未授权空态、创建/聚合 chip、
右上角新建歌单弹窗）、歌单详情页（⋮ 菜单仅修改名称/删除歌单）、播放页（队列/设备/标题区均无反应）、
我的页全部功能行、播放历史页。疑似入口在**平台歌单详情/歌曲行上下文菜单**（需平台授权后才有
歌曲列表数据）或搜索结果页（/search，SWAN-20260904-005 ANR BLOCKED）。

一级页面骨架（顶部分类/入口/布局）：**未取得**——待 Wave 2b 用已授权平台账号或搜索页修复后补全。

## 生效断言

未进入，无断言。route 来自功能地图（App dev@4d1ed7b），未经真机验证。

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| （未知） | — | — | — |

排查记录（2026-09-10）：见「页面概述」入口清单；全平台未授权（QQ音乐/网易云/酷狗/Qobuz/电台平台），
授权按钮按安全约定一律不点。

## 关键元素

未进入，无元素。深级内容待 Wave 2b 补全。

## 页面布局

未知。

## 功能关联

- 所属 feature：`[[feature_收藏管理]]`（曲库域）
- 相关：`[[swan_批量操作页]]`（bulk_operate_page.dart 位于 unified_music/ 目录下，疑似从本页进入）、
  `[[swan_选择歌单页]]`

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_收藏管理.md | [[feature_收藏管理]] |
| pages/swan_批量操作页.md | [[swan_批量操作页]] |

_自动生成于 2026-09-11 13:44_
<!-- backlinks:end -->
