# swan_me_page（我的）

> 状态：draft（2026-09-08 真机 dump 验证，待 verify 走通后转正）
> 数据来源：登录态下点 tab_me 实机 dump

## 页面概述

个人中心。顶部账号入口（头像+昵称+手机号），下方功能列表：我的权益、充值与消费记录、
家庭管理、SWAN收藏、设备管理、音质设置、帮助与反馈、关于与升级。

## 进入方式

任意已登录页面点 `tab_me`

## 关键元素（来源：uiautomator dump）

| key | 文案/说明 | clickable | 备注 |
|---|---|---|---|
| `me_user_profile_entry` | 躣账号入口（惠威2b11\n13555555555） | ✅ | 进个人信息页 |
| 扫一扫 | OCR 文本（无 key） | ❓ | 顶部右侧 |
| 其余列表项 | OCR 文本（无 key） | ✅（部分） | 充值与消费记录/家庭管理/SWAN收藏/设备管理/音质设置/帮助与反馈/关于与升级 |

⚠️ dump 中"我的权益""设备管理""更多"出现两次（标题行 + 可点击行），实际可点的是后者。

## 关联

- [[swan_home_page]]（tab 切换）
- [[swan_person_info_page]]（点 me_user_profile_entry）
- [[swan_family_manage_page]]（OCR"家庭管理"，已探索）
- [[swan_favorites_page]]（OCR"SWAN收藏"，已探索）
- [[swan_sound_quality_page]]（OCR"音质设置"，底部弹层，已探索）
