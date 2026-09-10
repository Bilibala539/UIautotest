---
page_id: swan_AI形象页
name: "AI 形象（头像动图选择）"
aliases: [AI形象, role_images, 头像选择]
route: /ai/role/images
status: draft
last_updated: 2026-09-10
type: screen
package_name: com.swan.network
activity: null
orientation: portrait
---

# AI 形象 (swan_AI形象页)

## 页面概述

AI 角色头像选择页（路由 /ai/role/images，从角色编辑页「形象生成→选择」进入）。
标题「AI 形象」，内容为预设动图头像卡竖列（实测 4 张，每张整卡可点，卡右上角标「动图」）。
底部双按钮：「完成」（左，选定返回）+「DIY形象」（右，进 DIY 形象生成页）。
列表不可再滚动出更多卡（4 张为固定集合，实测滚动后仍 4 张）。全页无 accessibility key。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 页面标题 | 出现 | OCR"AI形象"（顶栏居中） | 进入本页 |
| 动图卡标 | 出现 | OCR"动图"（×4，卡右上角） | 卡片列表渲染完成 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_角色编辑页]]` | `OCR"选择"`（形象生成区右上） | click | 见「生效断言」（2026-09-10 Wave5 实测） |

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 返回按钮 | 顶栏左上图标（无 key 无文案，[0,72][128,184]） | static | click / press_back | 回 `[[swan_角色编辑页]]` | 待截 | verified（press_back 实测） |
| 动图头像卡（×4） | 无 key 无文案（整卡可点，卡内 OCR"动图"角标锚定卡位置） | dynamic | click 选中（未实测选中态样式） | 选中标记出现（未验证） | 待截 | draft |
| 完成按钮 | `OCR"完成"`（底部左半） | static | click（未实测，应携带所选头像返回角色编辑页） | 回 `[[swan_角色编辑页]]` | 待截 | draft |
| DIY形象按钮 | `OCR"DIY形象"`（底部右半） | static | click | `[[swan_DIY形象页]]`（2026-09-10 Wave5 实测） | `swan_AI形象页_DIY形象按钮.png`（正式） | verified |

### 元素截图（image/flutter）

| 常量 | 文件（image/flutter，正式；2026-09-10 aw-verify 真机验证通过后转正） |
|---|---|
| `SWAN_ROLE_IMAGES_DIY_BTN` | `swan_AI形象页_DIY形象按钮.png`（2026-09-10 Wave5 采集，真机 find_image 0.8 通过） |

## 页面布局

```
┌────────────────────────┐
│ [←]      AI 形象        │
│ ┌────────────────────┐ │
│ │        （动图）      │ │ ← 卡1 整卡可点
│ └────────────────────┘ │
│ ┌────────────────────┐ │
│ │        （动图）      │ │ ← 卡2
│ └────────────────────┘ │
│ …（共 4 张）             │
│ [  完成  ][ DIY形象 ]    │
└────────────────────────┘
```

## 功能关联

- 所属 feature：建议新单列 `feature_AI助手`（AI 角色域）
- 上游：`[[swan_角色编辑页]]`（选择按钮）
- 下游：`[[swan_DIY形象页]]`（DIY形象按钮）
- 功能地图对照：/ai/role/images [已扫描-未考古] → 本页实测补全
