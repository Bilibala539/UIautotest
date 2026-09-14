---
page_id: swan_首页音乐Tab
name: "首页·音乐 Tab"
aliases: [音乐Tab, home_music_page]
route: null              # 内嵌于 /home/main 五顶 Tab 容器，无独立路由
status: 已验证
last_updated: 2026-09-10
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 首页·音乐 Tab (swan_首页音乐Tab)

## 页面概述

首页（`/home/main`）五顶 Tab 之一（推荐/音乐/AI/可视音箱/电台），搜索入口型页面：
顶部为「跨平台搜索音乐」搜索条，下方按第三方平台分组展示推荐歌单宫格
（QQ音乐 → 网易云音乐 → 酷狗音乐 → Apple Music → …），卡片内容为运营数据。
整个 Tab 无任何 无障碍键（除 `bottom_player` / 底部 tab 公共 key），定位全靠 OCR。

## 生效断言

> 本页加载成功的机器可判依据。图片断言留给 element 阶段，当前以 OCR 为主。

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 搜索条文案 | 出现 | OCR"跨平台搜索音乐" | 音乐 Tab 已生效 |
| 平台分组标题 | 出现 | OCR"QQ音乐" | 歌单数据已加载 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_首页]]` | `OCR"音乐"`（顶部 Tab 行） | click | 见「生效断言」 |
| `[[swan_首页AITab]]` 等其它顶 Tab | `OCR"音乐"`（顶部 Tab 行） | click | 见「生效断言」 |

注意（重要）：`go_home()`（点底部 `tab_recommend`）只会回到首页容器，**顶部 Tab 停留在上次选择**
（实测跨底栏切换、跨登出/登录均持久）。要稳定进入音乐 Tab 必须显式点顶部"音乐"。
顶部 Tab 文案"音乐"与页面内"网易云音乐""跨平台搜索音乐"等文案存在包含关系，
`click_text` 依赖 OCR 自上而下的首个命中（顶部 Tab 在最上方，实测稳定）。

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 顶部 Tab 行（推荐/音乐/AI/可视音箱/电台） | `SWAN_HOME_TAB_*`（图，未选中态 5 张）/ `OCR"音乐"` 等 5 个文案（无无障碍键，desc 与 OCR 一致） | 静态 | click | 对应 Tab 生效断言 | 已截（5 Tab 各一张未选中态，见下方） | 已验证 |
| 搜索条 | `OCR"跨平台搜索音乐"` / `SWAN_HOME_MUSIC_SEARCH_BAR`（图） | 静态 | click | 进入 /search（⛔ 本轮未实测，搜索域 ANR BLOCKED） | 已截 | 已验证 |
| 平台分组标题（QQ音乐/网易云音乐/酷狗音乐/Apple Music/Qobuz） | `OCR"QQ音乐"` 等 | 静态 | 只读断言 | — | 待截（每组标题） | 草稿 |
| 歌单卡片（封面+歌单名） | OCR 歌单名（如"200首华语金曲…"） | 动态 | ⛔ 不点（进歌单详情，未探索） | — | 动态-不截图 | 草稿 |
| 底部播放条 | `bottom_player`（无障碍键）/ `SWAN_BOTTOM_PLAYER_BAR` | 静态 | click | `[[swan_播放页]]` | 已有图 | 草稿 |
| 底部 4 tab | `tab_recommend` / `tab_platform` / `tab_device` / `tab_me`（无障碍键） | 静态 | click | 对应 tab 页 | 已有图 | 草稿 |

### 元素截图（image/flutter）

### 元素截图（image/flutter，2026-09-10 aw-verify 真机走通复验通过，promote_image 已转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 搜索条（完整 pill 含放大镜图标） | `SWAN_HOME_MUSIC_SEARCH_BAR` | image/flutter/swan_首页音乐Tab_搜索条.png |
| 顶部 Tab「音乐」（未选中态） | `SWAN_HOME_TAB_MUSIC` | image/flutter/swan_首页_音乐Tab按钮.png |

顶 Tab 行 5 张未选中态模板（`SWAN_HOME_TAB_RECOMMEND/MUSIC/RADIO/AI/VISION`）为五顶 Tab 页共用，2026-09-10 真机 click_image 冒烟通过（切 Tab 生效）。

## 页面布局

- 顶栏：五顶 Tab 行（推荐/音乐/AI/可视音箱/电台，屏幕最上部 y≈88-168 区域，选中态加粗）
- 内容区（可滚动）：
  - 搜索条「跨平台搜索音乐」（全宽）
  - 各平台分组：分组标题 + 3 列歌单卡片宫格（QQ音乐/网易云音乐/酷狗音乐/Apple Music/…）
  - ⚠️ 动态区域：歌单卡片内容随运营数据变化，禁止整卡截图
- 底栏：`bottom_player` 迷你播放条 + 底部 4 tab（与其它首页 Tab 共享）

## 功能关联

- 所属 feature：`[[feature_导航框架]]`（首页域）、`[[feature_平台聚合]]`（歌单来自第三方平台）
- 上游：`[[swan_首页]]`（推荐 Tab / 底部 tab 切回）
- 下游：搜索页 /search（未探索，SWAN-20260904-005 ANR BLOCKED）、歌单详情（未探索）、`[[swan_播放页]]`

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_导航框架.md | [[feature_导航框架]] |
| digest/flows/flow_搜索_关键词搜索全链路.md | [[flow_搜索_关键词搜索全链路]] |
| pages/swan_授权门禁弹层.md | [[swan_授权门禁弹层]] |
| pages/swan_搜索输入页.md | [[swan_搜索输入页]] |
| pages/swan_视频分类页.md | [[swan_视频分类页]] |
| pages/swan_首页AITab.md | [[swan_首页AITab]] |
| pages/swan_首页可视音箱Tab.md | [[swan_首页可视音箱Tab]] |
| pages/swan_首页电台Tab.md | [[swan_首页电台Tab]] |

_自动生成于 2026-09-14 13:38_
<!-- backlinks:end -->