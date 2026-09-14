# swan_设备页

> 状态：page（2026-09-08 真机 dump + OCR + verify 复验转正）
> 数据来源：登录态下首页点 tab_device 实机 dump；截图 explorer_output/screenshots/swan/swan_设备页

## 页面概述

设备页：左侧按 WIFI/本机/Apple/低音炮/DSP 分类的设备列表区，默认 WIFI 区展示
当前账号绑定的 2 台设备卡片（Libretto_0E00、HiVi M5A_003C，均"连接良好"），
每卡片带 设置/同步设备/音量设置 操作。右上角"添加设备"。

## 进入方式

- 首页（或任意全局 tab 页）点 `tab_device`

## 关键元素（来源：uiautomator dump）

⚠️ 设备卡片类 key 按设备 MAC/UUID 动态拼接，模式固定但后缀因设备而异：
`wifi_device_card_<UUID>` / `wifi_device_settings_<UUID>` / `wifi_device_sync_<UUID>`。
另：`wifi_device_selected_<UUID>` 为**选中态才出现的动态键**（2026-09-11 R3 补充）：
.229 常规 dump 无此键，.144 选中设备后出现 ⇒ 仅设备被选中时存在，勿用作常驻判据。
当前实测两台设备 UUID：
- `FF311BB6_477E_9FD6_13A6_0E00FF31F012`（Libretto_0E00）
- `FF315AE1_446A_A8D7_BBD3_003CFF31F012`（HiVi M5A_003C）

| 无障碍键 | 文案/说明 | 可点击 | 备注 |
|---|---|---|---|
| `device_page` | 页面根节点 | ❌ | 页面判据 |
| `device_add_button` | 添加设备（右上角） | ✅ | |
| `device_wifi_section` | WIFI（左侧分类） | ✅ | |
| `device_refresh_button` | 列表区（无文案，刷新） | ✅ | |
| `wifi_device_card_<UUID>` | 设备卡片（连接良好 + 音源状态） | ✅ | 每设备一个 |
| `wifi_device_settings_<UUID>` | 设备名入口（如"Libretto_0E00"） | ✅ | 未点（内含删除设备风险） |
| `wifi_device_sync_<UUID>` | 同步设备 | ✅ | 未点（会向真机下发同步） |

无无障碍键 的 OCR 文本元素：

| 文案 | 可点击 | 备注 |
|---|---|---|
| 本机 / Apple / 低音炮 / DSP（左侧分类） | ✅ | 未点 |
| 更多（每卡片） | ✅ | 未点（可能含删除设备） |
| 音量设置（每卡片） | ✅ | ⛔ 未点（控制真实音箱音量） |
| 扬声器 卡片（"本机"分类下） | ✅ | 本机虚拟卡片 |


### 元素截图（image/flutter，2026-09-08 aw-element 采集 + verify 复验转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 右上角「添加设备」图标 | `SWAN_DEVICE_ADD_BTN` | image/flutter/swan_添加设备按钮.png |
## 页面布局

```
┌────────────────────────┐
│ 设备           [添加设备] │  device_add_button
│──────┬─────────────────│
│ WIFI │ WIFI（区标题）      │  device_refresh_button 覆盖列表区
│ 本机 │ ┌─ Libretto_0E00 ─┐ │
│ Apple│ │ 连接良好          │ │  wifi_device_card_FF311BB6…
│ 低音炮│ │ [更多][同步设备][音量设置]│
│ DSP  │ └────────────────┘ │
│      │ ┌─ HiVi M5A_003C ─┐ │
│      │ │ 连接良好 …       │ │  wifi_device_card_FF315AE1…
│      │ └────────────────┘ │
│      │ 本机：扬声器 卡片      │
│ [bottom_player] 首页|平台|设备|我的 │
└────────────────────────┘
```

## 缺口

- wifi_device_settings / 更多 / 音量设置 / 同步设备 均只记录入口未实测（真机安全约束）
- 添加设备流程未探索（会进入配网流程）
- Apple/低音炮/DSP 分类下内容未探索（当前账号无此类设备）

## 关联

- [[swan_首页]]（tab 切换）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_导航框架.md | [[feature_导航框架]] |
| digest/features/feature_设备管理.md | [[feature_设备管理]] |
| digest/flows/flow_导航_四tab切换.md | [[flow_导航_四tab切换]] |
| pages/swan_播放页.md | [[swan_播放页]] |
| pages/swan_首页.md | [[swan_首页]] |

_自动生成于 2026-09-14 13:38_
<!-- backlinks:end -->