# swan_family_manage_page（家庭管理）

> 状态：draft（2026-09-08 真机 dump + OCR 验证）
> 数据来源：我的页点"家庭管理"列表项实机 dump + OCR；截图 explorer_output/screenshots/swan/swan_family_manage_page

## 页面概述

家庭管理页。展示当前家庭卡片：家庭名"惠威2b11"（当前账号为创建人），
右上角为成员/添加图标按钮。页面内无任何 accessibility key，定位全靠 OCR 文本。

## 进入方式

- 我的页点 OCR 文本"家庭管理"（无 key，click_text 定位）

## 关键元素（来源：uiautomator dump / OCR）

无 key。OCR 文本元素：

| 文案 | clickable | 备注 |
|---|---|---|
| 家庭管理（页标题） | ❌ | 顶部居中 |
| 我的家庭 | ✅ | dump 有此可点节点（无文案 key） |
| 惠威2b11 / 创建人 | ❌ | 家庭卡片文本 |
| 右上角图标按钮 [610,73][720,183] | ✅ | OCR"器/只+"，功能未知（疑添加成员/更多），未点 |
| 左上返回按钮 [0,72][128,184] | ✅ | 无文案图标，press_back 等效 |
| 成员行右侧「添加成员」图标（人形+，[621,314][656,353]） | ✅ | 已截图 | 
| 家庭头像/图标 [32,306][130,404] | ❌ | |


### 元素截图（image_ai/flutter 草稿，2026-09-08 aw-element 采集，待 verify 转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 成员行右侧「添加成员」图标（人形+号，非右上角宫格图标） | `SWAN_FAMILY_ADD_MEMBER_ICON` | image_ai/flutter/swan_family_add_member_icon.png |
## 页面布局

```
┌────────────────────────┐
│ [←]      家庭管理    [?) │
│ 我的家庭                  │
│ ┌──────────────────┐   │
│ │ (icon) 惠威2b11  [+?]│ │
│ │        创建人       │ │
│ └──────────────────┘   │
└────────────────────────┘
```

## 缺口

- 全页无 accessibility key，只能 click_text/截图定位；图标按钮已补截图（见元素截图表）- 全页无 accessibility key，只能 click_text/截图定位；建议 element 截图补图标按钮
- 添加成员/家庭设置流程未探索

## 关联

- [[swan_me_page]]（列表项进入，press_back 返回）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| pages/swan_me_page.md | [[swan_me_page]] |

_自动生成于 2026-09-08 15:00_
<!-- backlinks:end -->