---
flow_id: flow_导航_四tab切换
name: "底部四 Tab 轮巡（首页→平台→设备→我的→首页）+ 顶 Tab 持久化注意事项"
feature: "[[feature_导航框架]]"
status: draft
last_updated: 2026-09-10
automation: yes
risk: none
---

# 四 Tab 轮巡切换 (flow_导航_四tab切换)

## 完成什么功能

登录后在底部全局 Tab 壳（首页/平台/设备/我的）依次切换一圈，逐页做生效断言，验证导航框架的 Tab 切换与页面缓存。

## 前置条件

- 登录态：是（`tab_me` 为登录态判据；未登录时底部 tab 壳不存在）
- 设备：真机已连接，App 在前台任意全局 tab 页
- 账号：当前账号（13555555555）即可，无数据要求

## 步骤

| # | 页面 | 元素（locator） | 操作 | 预期 App 反应 |
|---|---|---|---|---|
| 1 | `[[swan_首页]]` | `tab_recommend`（key） | click | 切回首页容器。⚠️ **risk（顶 Tab 持久化）**：点 `tab_recommend`（即 `go_home()`）只回首页容器，**顶部五顶 Tab 停留在上次选择**（实测跨底栏切换、跨登出/登录均持久）；要稳定落在推荐 Tab 必须显式 `click_text("推荐")`（或 `click_image(SWAN_HOME_TAB_RECOMMEND)`） |
| 2 | `[[swan_首页]]` | OCR"最近播放"（内容区） | 断言 | 首页生效：内容区已渲染（完整/紧凑两种布局均含"最近播放"） |
| 3 | `[[swan_平台页]]` | `tab_platform`（key） | click | 平台页生效断言通过 |
| 4 | `[[swan_平台页]]` | `platform_page`（key，页面根节点） | 断言 | 根节点可见（desc 含"平台/总资产（惠币/HC）"）；可辅以 `image_exists(SWAN_PLATFORM_NETEASE_ROW)` |
| 5 | `[[swan_设备页]]` | `tab_device`（key） | click | 设备页生效断言通过 |
| 6 | `[[swan_设备页]]` | `device_page`（key，页面根节点）/ `device_add_button`（key） | 断言 | 根节点与右上角"添加设备"可见（可辅以 `image_exists(SWAN_DEVICE_ADD_BTN)`） |
| 7 | `[[swan_我的页]]` | `tab_me`（key） | click | 我的页生效断言通过 |
| 8 | `[[swan_我的页]]` | `me_user_profile_entry`（key）/ `SWAN_ME_FAVORITES_ROW`（图） | 断言 | 顶部账号入口与"SWAN收藏"列表行可见 |
| 9 | `[[swan_首页]]` | `tab_recommend`（key） | click | 回到首页容器，顶部 Tab 保持步骤 1 后的选择（持久化行为，非 bug） |

## 断言点

| # | 类型 | 内容 |
|---|---|---|
| 1 | OCR | 首页："最近播放"出现（两种轮换布局下均稳定） |
| 2 | key | 平台页：`platform_page` 根节点出现 |
| 3 | key | 设备页：`device_page` 根节点 + `device_add_button` 出现 |
| 4 | key | 我的页：`me_user_profile_entry` 出现 |
| 5 | 图片 | 我的页：`image_exists(SWAN_ME_FAVORITES_ROW)`（"SWAN收藏"列表行） |
| 6 | 图片 | 全程：`image_exists(SWAN_BOTTOM_PLAYER_BAR)` —— 底栏迷你播放条在四个 tab 页持续可见 |

## 风险与限制

- **risk（首页推荐 Tab 布局轮换）**：推荐 Tab 首屏在"完整布局"（搜索条+我喜欢/歌单/AI 卡片行+最近播放）与"紧凑布局"（仅 我喜欢|AI 卡片行+最近播放，**无「歌单」卡**）之间服务端动态轮换。本 flow 断言只选"最近播放"规避；依赖「歌单」卡片/搜索条的断言会间歇失败。
- **risk（顶 Tab 持久化）**：所有"回到首页"操作后必须显式点顶部"推荐"才能确定落在推荐 Tab（对 flow_歌单/flow_搜索 是硬前置）。
- **risk（设备卡 key 动态拼接）**：设备页 `wifi_device_card_<UUID>` 按 UUID 拼接，本 flow 只用根节点/静态 key，不碰设备卡（同步/音量设置有真机安全约束，⛔ 不点）。
- Tab 页有缓存与可见性暂停（feature 文档），切换回已访问 tab 不重载；断言以元素可见为准，不假设加载动画。

## 对应用例

- `tests/flutter/test_swan_readonly_pages.py::test_home_page_elements`
- `tests/flutter/test_swan_readonly_pages.py::test_platform_page_readonly`
- `tests/flutter/test_swan_readonly_pages.py::test_device_page_elements`
