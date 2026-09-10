---
page_id: swan_播放历史页
name: "播放历史"
aliases: [最近播放, play_history]
route: "/me/play-history"
status: verified
last_updated: 2026-09-10
type: screen
package_name: com.swan.network
activity: null
orientation: portrait
---

# 播放历史 (swan_播放历史页)

## 页面概述

播放历史页（`play_history_page.dart`，路由 `/me/play-history`），标题「最近播放」。
首页·推荐 Tab「最近播放」区的「已播歌曲」卡片进入。顶部六个分类 Tab：
歌曲/艺人/专辑/歌单/电台/播客，内容区为历史列表（本账号空态「暂无历史播放」——
注意首页卡片显示"已播歌曲 1首"但本页歌曲 Tab 为空，两处统计口径不一致，待有播放数据账号复验）。

⚠️ 全页无 accessibility key（除 `bottom_player`），本页无底部 4 tab（push 页，仅贴底播放条）。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 页面标题 | 出现 | OCR"最近播放"（顶栏中央） | 进入本页 |
| 分类 Tab 行 | 出现 | OCR"歌曲"（Tab 行 y≈204-276） | Tab 框架已渲染 |
| 空态 | 出现 | OCR"暂无历史播放"（无历史时） | 数据加载完成 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_首页]]`（推荐 Tab） | `OCR"已播歌曲"`（最近播放区左卡片，desc='已播歌曲\n1首'；卡片可能被 bottom_player 遮挡下半部，需先滚动露出） | click | 见「生效断言」 |

自然语言补充：首页需先滚动到「最近播放」区（swipe_up 1 次）；「已播歌手」「已播专辑」卡片
预期分别进本页对应 Tab（未逐一验证）。

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 返回按钮 | 无文案 ImageView [0,72][128,184] | static | click / press_back | 回 `[[swan_首页]]` | 可复用 `SWAN_PLAYLIST_BACK_BTN`（同款箭头，见歌单页注）或顶栏整条图 | verified（press_back 实测；顶栏整条图断言通过） |
| 标题 | OCR"最近播放" [287,104][433,152] | static | 只读 | — | 已转正（含顶栏）`SWAN_HISTORY_TOPBAR`（2026-09-10 verify 图断言通过） | verified |
| 分类 Tab | OCR"歌曲"/"艺人"/"专辑"/"歌单"/"电台"/"播客"（六 Tab，y≈204-276） | static | click | 列表切换（未逐一验证） | 已转正（Tab 条整条）`SWAN_HISTORY_TABBAR`（2026-09-10 verify 图断言通过，歌曲 Tab 选中态） | verified |
| 空态 | OCR"暂无历史播放" [0,732][720,772] | dynamic | 只读 | — | dynamic-不截图 | verified（2026-09-10 verify 实测） |
| 底部播放条 | `bottom_player`（key，[0,1470][720,1528]） | static | click | `[[swan_播放页]]` | 已有图 | verified |

### 元素截图（2026-09-10 aw-verify 真机验证通过，已转正 image/flutter/）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 顶栏整条（返回箭头 + 「最近播放」标题，全宽） | `SWAN_HISTORY_TOPBAR` | image/flutter/swan_播放历史页_顶栏.png |
| 分类 Tab 条整条（歌曲…播客六 Tab，歌曲选中态） | `SWAN_HISTORY_TABBAR` | image/flutter/swan_播放历史页_分类Tab条.png |

## 页面布局

```
┌────────────────────────┐
│ [←]     最近播放          │
│ 歌曲 艺人 专辑 歌单 电台 播客 │  六分类 Tab（可横滑）
│                        │
│      （空态插图）         │
│     暂无历史播放           │
│ [bottom_player（贴底）]  │  ⚠️ 无底部 4 tab
└────────────────────────┘
```

## 功能关联

- 所属 feature：`[[feature_收藏管理]]`（曲库域；播放历史属听歌曲库数据）
- 上游：`[[swan_首页]]`（推荐 Tab 已播歌曲卡片）
- 下游：`[[swan_播放页]]`（bottom_player）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_收藏管理.md | [[feature_收藏管理]] |
| pages/swan_首页.md | [[swan_首页]] |

_自动生成于 2026-09-10 14:19_
<!-- backlinks:end -->
