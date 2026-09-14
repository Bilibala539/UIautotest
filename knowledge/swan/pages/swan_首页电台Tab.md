---
page_id: swan_首页电台Tab
name: "首页·电台 Tab"
aliases: [电台Tab, home_radio_page]
route: null              # 内嵌于 /home/main 五顶 Tab 容器，无独立路由
status: 已验证
last_updated: 2026-09-10
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 首页·电台 Tab (swan_首页电台Tab)

## 页面概述

首页五顶 Tab 之一（最右侧），搜索入口型页面：顶部「搜索电台」搜索条，
下方「全国电台」分组列出各地广播电台（北京交通广播/河北交通广播/怀旧金曲964/石家庄交通广播…），
再往下为 80er-Radio harmony 等 80/90 年代电台分组（部分可见）。
电台列表为动态数据。除公共 key 外无任何 无障碍键。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 搜索条文案 | 出现 | OCR"搜索电台" | 电台 Tab 已生效 |
| 分组标题 | 出现 | OCR"全国电台" | 电台列表已加载 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_首页]]` | `OCR"电台"`（顶部 Tab 行最右） | click | 见「生效断言」 |
| `[[swan_首页音乐Tab]]` 等其它顶 Tab | `OCR"电台"`（顶部 Tab 行最右） | click | 见「生效断言」 |

注意：`go_home()` 只回首页容器，顶部 Tab 停留在上次选择（见 `[[swan_首页音乐Tab]]` 同款说明）。
"电台"文案与页面内电台名（如"石家庄交通广播"）无包含冲突，但与音乐 Tab 的分类行"电台"同名——
跨 Tab 状态下点"电台"前先确认当前在首页容器内。

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 顶部 Tab 行 | `OCR"电台"` / `SWAN_HOME_TAB_RADIO`（图，未选中态） | 静态 | click | 本页生效断言 | 已截（5 Tab 分图共用） | 已验证 |
| 搜索条 | `OCR"搜索电台"` / `SWAN_HOME_RADIO_SEARCH_BAR`（图） | 静态 | click | 进入 /search（⛔ 未实测，搜索域 ANR BLOCKED） | 已截 | 已验证 |
| 分组标题 | `OCR"全国电台"` | 静态 | 只读断言 | — | 待截 | 草稿 |
| 电台行（台名+频率+封面） | OCR 台名（如"北京交通广播"） | 动态 | ⛔ 不点（触发播放，未探索） | — | 动态-不截图 | 草稿 |
| 80/90 年代分组 | OCR"harmony"（部分可见） | 动态 | 只读 | — | 动态-不截图 | 草稿 |
| 底部播放条 | `bottom_player`（无障碍键） | 静态 | click | `[[swan_播放页]]` | 已有图 | 草稿 |
| 底部 4 tab | `tab_recommend` / `tab_platform` / `tab_device` / `tab_me`（无障碍键） | 静态 | click | 对应 tab 页 | 已有图 | 草稿 |

### 元素截图（image/flutter）

### 元素截图（image/flutter，2026-09-10 aw-verify 真机走通复验通过，promote_image 已转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 搜索条（完整 pill 含放大镜图标） | `SWAN_HOME_RADIO_SEARCH_BAR` | image/flutter/swan_首页电台Tab_搜索条.png |
| 顶部 Tab「电台」（未选中态） | `SWAN_HOME_TAB_RADIO` | image/flutter/swan_首页_电台Tab按钮.png |

## 页面布局

- 顶栏：五顶 Tab 行（本 Tab 为最右"电台"）
- 内容区（可滚动）：
  - 搜索条「搜索电台」（全宽）
  - 「全国电台」分组：电台行列表（左侧频率/台标，右侧台名），行高约 224px
  - ⚠️ 动态区域：电台列表内容随数据变化
  - 下方 80/90 年代电台分组（harmony 等）
- 底栏：`bottom_player` + 底部 4 tab（与其它首页 Tab 共享）

## 功能关联

- 所属 feature：`[[feature_导航框架]]`（首页域）、`[[feature_平台聚合]]`（电台/播客域）
- 上游：`[[swan_首页]]`
- 下游：搜索页 /search（未探索）、电台播放（未探索，点击电台行即播放）、`[[swan_播放页]]`
- 功能地图对应：全国电台 /music_platform/radio/country、80/90 电台 /music_platform/radio/80s、90s

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_导航框架.md | [[feature_导航框架]] |
| pages/swan_全国电台页.md | [[swan_全国电台页]] |
| pages/swan_授权门禁弹层.md | [[swan_授权门禁弹层]] |
| pages/swan_搜索输入页.md | [[swan_搜索输入页]] |

_自动生成于 2026-09-14 13:26_
<!-- backlinks:end -->