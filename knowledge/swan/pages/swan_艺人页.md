---
page_id: swan_艺人页
name: "艺人页"
aliases: [artists, 艺人列表/详情]
route: "/music_platform/artists(/detail)"
status: 已验证
last_updated: 2026-09-10
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 艺人页 (swan_艺人页)

## 页面概述

❌ **不可达**。艺人页（`/music_platform/artists(/detail)`，artists_page.dart）在未授权账号下
无可见入口。2026-09-10 Wave4 排查过的入口面：

1. 搜索结果页「艺人」Tab：任意关键词（"piano"/"harmony"）均空态，无艺人结果行可点
   （搜索源依赖平台授权，与关键词无关）
2. 首页音乐 Tab 平台区块（QQ音乐/Apple Music 等）：区块标题与歌单卡均弹
   `[[swan_授权门禁弹层]]` 变体 B
3. 首页推荐 Tab「已播歌手」卡：进入的是 `[[swan_播放历史页]]`（route /me/play-history，
   落地「艺人」子 Tab，空态「暂无历史播放」）——**注意口径**：首页卡片显示「已播歌手 1位歌手」
   但页内空态（与已播歌曲计数口径不一致问题同族，runtime_experience 已记）
4. 播放历史页「艺人」Tab：空态（无历史数据）

待验证假设：播放历史页「艺人」Tab 的内容组件可能就是 artists_page（/music_platform/artists）
的复用——需有播放历史的账号点击艺人行后比对路由，当前无法验证。

## 生效断言

未进入，无断言。route 来自功能地图（App dev@4d1ed7b），未经真机验证。

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_搜索结果页]]` | 艺人 Tab 下的艺人结果行 | click | ⚠️ 结果空态不可达（需授权账号） |
| `[[swan_播放历史页]]` | 艺人 Tab 下的艺人行（假设，未验证） | click | ⚠️ 空态不可达 |

## 关键元素

未进入，无元素。待授权账号补全。

## 页面布局

未知。

## 功能关联

- 所属 feature：`[[feature_平台聚合]]`（音乐平台聚合域）
- 上游（假设）：`[[swan_搜索结果页]]`（艺人 Tab）、`[[swan_播放历史页]]`（艺人 Tab）
- 阻断方：`[[swan_授权门禁弹层]]`、搜索空态

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/flows/flow_搜索_关键词搜索全链路.md | [[flow_搜索_关键词搜索全链路]] |
| pages/swan_搜索结果页.md | [[swan_搜索结果页]] |

_自动生成于 2026-09-14 13:38_
<!-- backlinks:end -->