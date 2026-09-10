---
page_id: swan_<stable_page_id>
name: "页面名称"
aliases: []
route: "/login"            # 功能地图中的路由常量；弹层/半屏无路由填 null
status: draft              # draft → page（promote_knowledge.py 验证转正）
last_updated: null         # YYYY-MM-DD，每次实质更新时改
type: screen               # screen | sheet（半屏弹层） | dialog（居中弹窗）
package_name: com.swan.network
activity: null
orientation: portrait
---

# 页面名称 (swan_<stable_page_id>)

## 页面概述

说明页面用途、进入条件和可观察的稳定 UI 状态。

## 生效断言

> 本页加载成功的机器可判依据。优先图片断言（`image_exists`），其次 accessibility key，最后 OCR 文案。

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 示例：页面标题栏 | 出现 | `image_exists(SWAN_XXX_TITLE)` | 进入本页即出现 |
| 示例：加载弹层 | 消失 | `image_exists(...)` 等待超时 | 数据加载完成 |

## 进入方式

> 结构化入口表：从哪个页面、操作什么元素、什么操作、以什么断言确认到达本页。

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_xxx]]` | `tab_me`（key） | click | 见「生效断言」 |

自然语言补充（不适合入表的特殊前置条件，如需登录态、需先滚动到底部）写在这里。

## 关键元素

> `类型` 判定标准见 CONTRIBUTING.md：内容固定可截图的为 static；内容随状态变化的为 dynamic（不截图，用 key/OCR 锚定）。

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 示例按钮 | `login_phone_field` | static | click | 目标页生效断言 | `SWAN_XXX_BUTTON` | draft |

### 元素截图（image/flutter）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 示例行 | `SWAN_ME_XXX_ROW` | image/flutter/swan_xxx_行.png |

## 页面布局

描述区域划分（顶栏/内容区/底栏），不写死坐标。动态区域（内容随播放状态/设备状态变化的）单独标注。

## 功能关联

- 所属 feature：`[[feature_xxx]]`（digest/features/）
- 相关 flow：`[[flow_xxx]]`（digest/flows/）
- 上游：`[[swan_xxx]]`（从哪里进来）
- 下游：`[[swan_yyy]]`（能去哪里）
