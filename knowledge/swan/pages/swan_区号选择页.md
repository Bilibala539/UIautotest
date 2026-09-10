---
page_id: swan_区号选择页
name: "区号选择（选择归属地）"
aliases: [选择归属地, area_code_page]
route: /login/area-code
status: verified
last_updated: 2026-09-10
type: screen
package_name: com.swan.network
activity: null
orientation: portrait
---

# 区号选择（选择归属地） (swan_区号选择页)

## 页面概述

登录页手机号输入框左侧「+86」按钮（`login_area_code_button`）进入的归属地选择页。
标题"选择归属地"，当前构建下页面只渲染「热门」分组 4 行（中国+86 / 中国香港+852 /
中国澳门+853 / 中国台湾+886），右侧有索引条；热门组下方为 A-Z 完整国家列表
（2026-09-10 verify 复验已渲染：阿富汗/阿尔巴尼亚/阿尔及利亚等，与早前「未渲染」记录不符，以复验为准）。**全页无 accessibility key**（除返回箭头外连 desc 都很少），定位靠 OCR。
点击任意区号行 → 自动返回登录页，`login_area_code_button` 的 desc 更新为所选区号。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 页面标题 | 出现 | OCR"选择归属地" | 已进入本页 |
| 热门分组行 | 出现 | OCR"中国香港" | 列表已加载 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_验证码登录页]]` | `login_area_code_button`（key，desc=+86） | click | OCR"选择归属地" |

自然语言补充：需先登出回到登录页（验证码形态或密码形态均可，区号按钮两形态共用）。

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 返回箭头 | 无 key（左上角 [0,72][128,184]） | static | click / `press_back` | 回 `[[swan_验证码登录页]]` | 待截 | draft |
| 页面标题 | `OCR"选择归属地"` | static | 只读断言 | — | 待截 | draft |
| 热门分组标题 | `OCR"热门"`（列表内左上） | static | 只读断言 | — | 待截 | draft |
| 区号行-中国 | `OCR"中国"` / `SWAN_AREA_CODE_CHINA_ROW`（图，含 +86 整行，防误匹配港/澳/台行首） | static | click | 自动返回登录页，区号按钮 desc=+86（实测） | 已截 | verified |
| 区号行-中国香港 | `OCR"中国香港"`（desc="中国香港\n+852"） | static | click（未实测选择，预期返回后按钮 desc=+852） | 未验证 | 待截 | draft |
| 区号行-中国澳门 | `OCR"中国澳门"`（desc="中国澳门\n+853"） | static | 同上 | 未验证 | 待截 | draft |
| 区号行-中国台湾 | `OCR"中国台湾"`（desc="中国台湾\n+886"） | static | 同上 | 未验证 | 待截 | draft |
| 右侧索引条 | desc=热门（[648,442][704,1342]，竖条） | static | 未实测 | — | 待截 | draft |

### 元素截图（image/flutter，2026-09-10 aw-verify 真机走通复验通过，promote_image 已转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 「中国 +86」整行 | `SWAN_AREA_CODE_CHINA_ROW` | image_ai/flutter/swan_区号选择_中国行.png |

## 页面布局

- 顶栏：返回箭头 + 居中标题"选择归属地"
- 内容区：「热门」分组标题 + 4 个区号行（左国家名、右区号，行高 88px）；
  下方 A-Z 完整国家列表（2026-09-10 复验已渲染，可滚动）
- 右缘：分组索引条（竖条，当前只暴露"热门"）

## 功能关联

- 所属 feature：`[[feature_账号体系]]`（会话与登录域）
- 上游：`[[swan_验证码登录页]]`（`login_area_code_button`）
- 下游：`[[swan_验证码登录页]]`（选择区号后自动返回，区号按钮 desc 更新）
- 功能地图对应：区号选择 /login/area-code（pure_flutter_area_code_page.dart）
