---
page_id: swan_全国电台页
name: "全国电台（FM 多级页族入口）"
aliases: [fm_country_radio, 全国电台页]
route: "/music_platform/radio/country"
status: draft
last_updated: 2026-09-10
type: screen
package_name: com.swan.network
activity: null
orientation: portrait
---

# 全国电台页 (swan_全国电台页)

## 页面概述

⚠️ **授权门禁拦截，未进入**。FM 电台族完整页（`/music_platform/radio/country`，
fm_country_radio_page.dart）在未授权账号下所有入口均弹 `[[swan_授权门禁弹层]]`
（变体 A「添加新平台/添加」）。电台 FM 虽是自有数据服务（fm_radio_http_service.dart，
首页电台 Tab 无授权也能拉到电台列表），但**多级页入口按「平台」处理，需先添加电台平台**。

同族页面（同一门禁，同日实测）：
- 80 年代电台 `/music_platform/radio/80s`（fm_harmony_radio_page.dart）
- 90 年代电台 `/music_platform/radio/90s`
- 城市选择 `/music_platform/radio/select-city`（见 `[[swan_城市选择页]]`，嵌套在本页族内）

2026-09-10 Wave4 实测入口与拦截证据：
1. 平台页·电台分类 →「全国电台」行：行本体不可点（clickable=false，点击无反应），
   右侧**圆形箭头图标**可点 → 弹门禁（变体 A）
2. 平台页·电台分类 →「90年代电台」「80年代电台」行：同构
3. 首页电台 Tab →「全国电台」分组标题（整行 clickable）→ 弹门禁（变体 A）
4. 首页电台 Tab →「80er-Radio harmony」分组标题 → 弹门禁（变体 A）
5. 电台 Tab 内电台行（北京交通广播等）直接可点（触发播放，按约定不点）——
   即**电台行播放不需要授权，分组标题进多级页才需要**

## 生效断言

未进入页面本体，无断言。到达门禁的判据见 `[[swan_授权门禁弹层]]`。

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_平台页]]` | 电台分类「全国电台」行右侧圆形箭头图标（无 key 无文案，待截图） | click | ⚠️ 未授权账号弹 `[[swan_授权门禁弹层]]` |
| `[[swan_首页电台Tab]]` | `OCR"全国电台"`（分组标题行） | click | ⚠️ 同上 |
| `[[swan_首页电台Tab]]` | `OCR"80er-Radio harmony"` / OCR"90年代电台"（分组标题行） | click | ⚠️ 同上（80s/90s 变体入口） |

前置：需先「添加」电台平台（⛔ 授权操作，自动化只断言不点击）。

## 关键元素

页面本体未进入，无元素。门禁元素见 `[[swan_授权门禁弹层]]`。

入口侧元素（已实测）：

| 元素 | locator | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 平台页电台行右侧箭头图标 | 无 key 无文案（圆形 chevron） | static | click | 弹门禁（未授权） | 待截 `SWAN_PLATFORM_RADIO_ROW_ARROW` | verified（拦截行为） |
| 电台 Tab 分组标题 | `OCR"全国电台"` / `OCR"80er-Radio harmony"` | static | click | 弹门禁（未授权） | 待截 | verified（拦截行为） |

## 页面布局

未知（未进入）。fm_country_radio_page.dart 骨架待授权账号补全；
城市选择入口推测在本页内（切换城市），待验证。

## 功能关联

- 所属 feature：`[[feature_平台聚合]]`（电台/播客域）
- 上游：`[[swan_平台页]]`（电台分类）、`[[swan_首页电台Tab]]`
- 下游：`[[swan_城市选择页]]`（推测）、电台播放
- 阻断方：`[[swan_授权门禁弹层]]`
