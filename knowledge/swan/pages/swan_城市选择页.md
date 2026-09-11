---
page_id: swan_城市选择页
name: "城市选择"
aliases: [fm_select_city, 选择城市]
route: "/music_platform/radio/select-city"
status: 已验证
last_updated: 2026-09-10
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 城市选择页 (swan_城市选择页)

## 页面概述

❌ **不可达**。城市选择页（`/music_platform/radio/select-city`，fm_select_city_page.dart）
是 FM 电台族的内嵌子页，入口在 `[[swan_全国电台页]]`（或电台 Tab 的城市筛选）内。
2026-09-10 Wave4 实测：本账号未授权，全国电台/80/90 电台多级页全部被
`[[swan_授权门禁弹层]]` 拦截，城市选择入口无任何可见触达路径：

- 平台页·电台分类三个入口（全国/90/80 年代电台）→ 全部弹门禁
- 首页电台 Tab：搜索条 + 全国电台分组行 + 80/90 分组行，无城市筛选控件
- 搜索（"harmony" 等 FM 电台名）→ 空态（搜索源未授权）

## 生效断言

未进入，无断言。route 来自功能地图（App dev@4d1ed7b），未经真机验证。

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_全国电台页]]` | （未知，推测页内城市切换控件） | click | ⚠️ 上游页被授权门禁拦截，不可达 |

## 关键元素

未进入，无元素。待授权账号补全。

## 页面布局

未知。

## 功能关联

- 所属 feature：`[[feature_平台聚合]]`（电台/播客域）
- 上游：`[[swan_全国电台页]]`（推测）
- 阻断方：`[[swan_授权门禁弹层]]`

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| pages/swan_全国电台页.md | [[swan_全国电台页]] |

_自动生成于 2026-09-11 13:44_
<!-- backlinks:end -->