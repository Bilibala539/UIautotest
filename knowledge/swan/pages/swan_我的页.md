# swan_我的页

> 状态：page（2026-09-08 真机 dump + verify 复验转正）
> 数据来源：登录态下点 tab_me 实机 dump

## 页面概述

个人中心。顶部账号入口（头像+昵称+手机号），下方功能列表：我的权益、充值与消费记录、
家庭管理、SWAN收藏、设备管理、音质设置、帮助与反馈、关于与升级。

## 进入方式

任意已登录页面点 `tab_me`

## 关键元素（来源：uiautomator dump）

| key | 文案/说明 | clickable | 备注 |
|---|---|---|---|
| `me_user_profile_entry` | 顶部账号入口（惠威2b11\n13555555555） | ✅ | 进个人信息页 |
| 扫一扫 | OCR 文本（无 key） | ❓ | 顶部右侧 |
| 其余列表项 | OCR 文本（无 key） | ✅（部分） | 充值与消费记录/家庭管理/SWAN收藏/设备管理/音质设置/帮助与反馈/关于与升级 |


### 元素截图（image/flutter，2026-09-08 aw-element 采集 + verify 复验转正）

| 元素                     | 常量（image/image_name_mapping.py） | 图片文件                                           |
| ---------------------- | ------------------------------- | ---------------------------------------------- |
| 列表行「家庭管理」              | `SWAN_ME_FAMILY_MANAGE_ROW`     | image/flutter/swan_我的_家庭管理行.png |
| 列表行「SWAN收藏」            | `SWAN_ME_FAVORITES_ROW`         | image/flutter/swan_我的_收藏行.png     |
| 列表行「设备管理」（设备管理分组下的可点行） | `SWAN_ME_DEVICE_MANAGE_ROW`     | image/flutter/swan_我的_设备管理行.png |
| 列表行「音质设置」              | `SWAN_ME_SOUND_QUALITY_ROW`     | image/flutter/swan_我的_音质设置行.png |
⚠️ dump 中"我的权益""设备管理""更多"出现两次（标题行 + 可点击行），实际可点的是后者。

## 关联

- [[swan_首页]]（tab 切换）
- [[swan_个人信息页]]（点 me_user_profile_entry）
- [[swan_家庭管理页]]（OCR"家庭管理"，已探索）
- [[swan_收藏页]]（OCR"SWAN收藏"，已探索）
- [[swan_音质设置页]]（OCR"音质设置"，底部弹层，已探索）
- [[swan_帮助与反馈页]]（OCR"帮助与反馈"，需先 swipe_up 滚动，2026-09-08 已探索）
- [[swan_关于与升级页]]（OCR"关于与升级"，需先 swipe_up 滚动，2026-09-08 已探索）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| pages/swan_个人信息页.md | [[swan_个人信息页]] |
| pages/swan_关于与升级页.md | [[swan_关于与升级页]] |
| pages/swan_家庭管理页.md | [[swan_家庭管理页]] |
| pages/swan_帮助与反馈页.md | [[swan_帮助与反馈页]] |
| pages/swan_收藏分组详情页.md | [[swan_收藏分组详情页]] |
| pages/swan_收藏页.md | [[swan_收藏页]] |
| pages/swan_音质设置页.md | [[swan_音质设置页]] |
| pages/swan_首页.md | [[swan_首页]] |

_自动生成于 2026-09-09 08:29_
<!-- backlinks:end -->