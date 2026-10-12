# swan_我的页

> 状态：page（2026-09-08 真机 dump + verify 复验转正）
> 数据来源：登录态下点 tab_me 实机 dump

## 页面概述

个人中心。顶部账号入口（头像+昵称+手机号），下方功能列表：我的权益、充值与消费记录、
家庭管理、SWAN收藏、设备管理、音质设置、帮助与反馈、关于与升级。

## 进入方式

任意已登录页面点 `tab_me`

## 关键元素（来源：uiautomator dump）

| 无障碍键 | 文案/说明 | 可点击 | 备注 |
|---|---|---|---|
| `me_user_profile_entry` | 顶部账号入口（惠威2b11\n13555555555） | ✅ | 进个人信息页 |
| 扫一扫 | `SWAN_ME_SCAN_ICON`（图；⚠️ 实测为纯图标按钮，无无障碍键 无文案，OCR 不可用） | ✅ | 顶部右侧（头像行右端 48x48），进扫一扫页（首次触发相机权限弹窗） |
| 其余列表项 | OCR 文本（无无障碍键） | ✅（部分） | 充值与消费记录/家庭管理/SWAN收藏/设备管理/音质设置/帮助与反馈/关于与升级 |


### 元素截图（image/flutter，2026-09-08 aw-element 采集 + verify 复验转正）

| 元素                     | 常量（image/image_name_mapping.py） | 图片文件                                           |
| ---------------------- | ------------------------------- | ---------------------------------------------- |
| 列表行「家庭管理」              | `SWAN_ME_FAMILY_MANAGE_ROW`     | image/flutter/swan_我的_家庭管理行.png |
| 列表行「SWAN收藏」            | `SWAN_ME_FAVORITES_ROW`         | image/flutter/swan_我的_收藏行.png     |
| 列表行「设备管理」（设备管理分组下的可点行） | `SWAN_ME_DEVICE_MANAGE_ROW`     | image/flutter/swan_我的_设备管理行.png |
| 列表行「音质设置」              | `SWAN_ME_SOUND_QUALITY_ROW`     | image/flutter/swan_我的_音质设置行.png |
| 右上角扫一扫图标 | `SWAN_ME_SCAN_ICON` | image/flutter/swan_我的_扫一扫图标.png（2026-09-10 Wave1 采集，离线匹配 1.000，已转正） |
| 顶部账号信息入口行头像本体（logout 路径第一步，⚠️ 只截图断言；不含昵称/手机号个人数据） | `SWAN_ME_ACCOUNT_ENTRY`（草稿） | image_ai/flutter/swan_我的_账号信息入口.png（2026-10-12 W1-A 采集，待 verify 转正；元素超浅色 std≈7，验收留意） |
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
| digest/features/feature_导航框架.md | [[feature_导航框架]] |
| digest/flows/flow_导航_四tab切换.md | [[flow_导航_四tab切换]] |
| digest/flows/flow_收藏_查看分组空态.md | [[flow_收藏_查看分组空态]] |
| pages/swan_个人信息页.md | [[swan_个人信息页]] |
| pages/swan_关于与升级页.md | [[swan_关于与升级页]] |
| pages/swan_家庭管理页.md | [[swan_家庭管理页]] |
| pages/swan_帮助与反馈页.md | [[swan_帮助与反馈页]] |
| pages/swan_扫一扫页.md | [[swan_扫一扫页]] |
| pages/swan_播放页.md | [[swan_播放页]] |
| pages/swan_收藏分组详情页.md | [[swan_收藏分组详情页]] |
| pages/swan_收藏页.md | [[swan_收藏页]] |
| pages/swan_音质设置页.md | [[swan_音质设置页]] |
| pages/swan_首页.md | [[swan_首页]] |

_自动生成于 2026-09-14 15:41_
<!-- backlinks:end -->