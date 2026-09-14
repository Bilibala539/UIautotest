---
page_id: swan_首页可视音箱Tab
name: "首页·可视音箱 Tab"
aliases: [可视音箱Tab, home_vision_page, Vision]
route: null              # 内嵌于 /home/main 五顶 Tab 容器，无独立路由
status: 已验证
last_updated: 2026-09-10
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 首页·可视音箱 Tab (swan_首页可视音箱Tab)

## 页面概述

首页五顶 Tab 之一。**当前账号未绑定可视音箱设备**，页面为未绑定预览态：
居中展示「添加可视音响」标题 +「即刻开启沉浸式视觉与音乐交融的双重体验~」文案 +
「暂未添加可视音箱，此功能不可使用」提示。内容区无任何语义节点（dump 不暴露），
全部信息只能靠 OCR。绑定可视音箱后应有壁纸 /vision/wallpaper、唤醒词、语音包等内容（未验证）。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 未绑定提示 | 出现 | OCR"暂未添加可视音箱" | 可视音箱 Tab 已生效（未绑定态） |
| 添加引导标题 | 出现 | OCR"添加可视音响" | 同上 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_首页]]` | `OCR"可视音箱"`（顶部 Tab 行） | click | 见「生效断言」 |
| `[[swan_首页音乐Tab]]` 等其它顶 Tab | `OCR"可视音箱"`（顶部 Tab 行） | click | 见「生效断言」 |

注意：`go_home()` 只回首页容器，顶部 Tab 停留在上次选择。

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 顶部 Tab 行 | `OCR"可视音箱"` / `SWAN_HOME_TAB_VISION`（图，未选中态） | 静态 | click | 本页生效断言 | 已截 | 已验证 |
| 添加引导标题 | `OCR"添加可视音响"` | 静态 | 只读断言（⛔ 不点——推测进添加设备/配网流程，禁止误触） | — | 待截 | 草稿 |
| 未绑定提示 | `OCR"暂未添加可视音箱，此功能不可使用"` / `SWAN_HOME_VISION_UNBOUND_HINT`（图） | 静态 | 只读断言 | — | 已截 | 已验证 |
| 底部播放条 | `bottom_player`（无障碍键） | 静态 | click | `[[swan_播放页]]` | 已有图 | 草稿 |
| 底部 4 tab | `tab_recommend` 等（无障碍键） | 静态 | click | 对应 tab 页 | 已有图 | 草稿 |

### 元素截图（image/flutter）

### 元素截图（image/flutter，2026-09-10 aw-verify 真机走通复验通过，promote_image 已转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 未绑定提示行（灰字整行） | `SWAN_HOME_VISION_UNBOUND_HINT` | image/flutter/swan_首页可视音箱Tab_未绑定提示.png |
| 顶部 Tab「可视音箱」（未选中态） | `SWAN_HOME_TAB_VISION` | image/flutter/swan_首页_可视音箱Tab按钮.png |

## 页面布局

- 顶栏：五顶 Tab 行（本 Tab 为"可视音箱"）
- 内容区（未绑定态）：
  - 居中引导区：添加可视音响标题 + 引导文案 + 不可用提示
  - ⚠️ 绑定设备后内容未知（壁纸/唤醒词/语音包等，见功能地图 Vision 域），待有设备后补充
- 底栏：`bottom_player` + 底部 4 tab

## 功能关联

- 所属 feature：`[[feature_导航框架]]`（首页域）；可视音箱 Vision 域（功能地图：壁纸 /vision/wallpaper 允许未绑定预览、唤醒词 /vision/wake-words、语音包 /vision/voice-pack、高级设置 /vision/advanced-settings*，均未探索）
- 上游：`[[swan_首页]]`
- 下游：`[[swan_播放页]]`；添加设备流程（⛔ 禁止自动化进入）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_导航框架.md | [[feature_导航框架]] |
| pages/swan_Vision域不可达页.md | [[swan_Vision域不可达页]] |

_自动生成于 2026-09-14 13:38_
<!-- backlinks:end -->