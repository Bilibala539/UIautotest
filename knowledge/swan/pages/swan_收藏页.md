# swan_收藏页（SWAN收藏）

> 状态：page（2026-09-08 真机 dump + OCR + verify 复验转正）
> 数据来源：我的页点"SWAN收藏"列表项实机 dump + OCR；截图 explorer_output/screenshots/swan/swan_收藏页

## 页面概述

SWAN收藏页。收藏歌单分组列表（我的家庭 / 我的音乐），底部固定"添加新的收藏歌单"
按钮。页内无 无障碍键，定位靠 OCR 文本。

## 进入方式

- 我的页点 OCR 文本"SWAN收藏"（无无障碍键，click_text 定位）

## 关键元素（来源：uiautomator dump / OCR）

无无障碍键。OCR 文本元素：

| 文案                     | 可点击 | 备注                         |
| ---------------------- | --------- | -------------------------- |
| 我的家庭                   | ✅         | 收藏分组卡片 [32,204][704,348]   |
| 我的音乐                   | ✅         | 收藏分组卡片 [32,368][704,512]   |
| 添加新的收藏歌单               | ✅         | 底部固定按钮 [32,1448][688,1528] |
| SWAN收藏（页标题）            | ❌         |                            |
| 左上返回按钮 [0,72][128,184] | ✅         | 无文案图标，press_back 等效        |


### 元素截图（image/flutter，2026-09-08 aw-element 采集 + verify 复验转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 「我的家庭」分组行 | `SWAN_FAV_FAMILY_GROUP_ROW` | image/flutter/swan_收藏_我的家庭分组行.png |
| 「我的音乐」分组行 | `SWAN_FAV_MUSIC_GROUP_ROW` | image/flutter/swan_收藏_我的音乐分组行.png |
| 「添加新的收藏歌单」按钮 | `SWAN_FAV_ADD_PLAYLIST_BUTTON` | image/flutter/swan_添加收藏歌单按钮.png |
## 页面布局

```
┌────────────────────────┐
│ [←]      SWAN收藏        │
│ ┌──────────────────┐   │
│ │     我的家庭        │ │
│ └──────────────────┘   │
│ ┌──────────────────┐   │
│ │     我的音乐        │ │
│ └──────────────────┘   │
│ [添加新的收藏歌单]          │
└────────────────────────┘
```

## 缺口

- 我的家庭分组内部已探索（见 [[swan_收藏分组详情页]]）；我的音乐分组仍未进入
- 添加收藏歌单流程未探索

## 关联

- [[swan_我的页]]（列表项进入，press_back 返回）
- [[swan_收藏分组详情页]]（click_text 分组行进入，press_back 返回，2026-09-08 已探索）
- [[swan_首页]]（"我喜欢"卡片疑与此功能相关，待验证）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_收藏管理.md | [[feature_收藏管理]] |
| digest/flows/flow_收藏_查看分组空态.md | [[flow_收藏_查看分组空态]] |
| pages/swan_我的页.md | [[swan_我的页]] |
| pages/swan_收藏分组详情页.md | [[swan_收藏分组详情页]] |
| pages/swan_歌单页.md | [[swan_歌单页]] |

_自动生成于 2026-09-14 13:26_
<!-- backlinks:end -->