---
page_id: swan_切换设备弹层
name: "切换设备弹层"
aliases: [multiroom_sheet, 输出设备切换]
route: null
status: 已验证
last_updated: 2026-09-10
type: 弹层
package_name: com.swan.network
activity: null
orientation: portrait
---

# 切换设备弹层 (swan_切换设备弹层)

## 页面概述

播放页右上角 `player_device_button` 打开的底部弹层（`multiroom_sheet` key 是本弹层唯一
无障碍键）。标题「切换设备」，下方为输出设备单选列表（含真实 Wi-Fi 音箱、
手机本机扬声器和 AirPlay 目标），顶部有纱罩 scrim（desc='纱罩'）。

⚠️⚠️ **安全红线**：列表含实验室真实音箱（Libretto_0E00 / Maestro1100_A20C / HiVi M300MKII），
自动化**只允许断言弹层出现，禁止点击任何设备行**（切换输出会把播放下发到真实音箱）。
关闭方式：press_back 或点纱罩区域。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 弹层根节点 | 出现 | `wait_accessibility(multiroom_sheet)`（desc='切换设备'） | 弹层已打开 |
| 当前输出设备行 | 出现 | OCR 当前设备名（本机态为"手机扬声器"，无单选圆点） | 列表已加载 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_播放页]]` | `player_device_button`（无障碍键，右上角） | click | 见「生效断言」 |

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 弹层根节点 | `multiroom_sheet`（无障碍键） | 静态 | 只读判据 | — | 待截 | 已验证（2026-09-10 verify key 实测） |
| 标题 | OCR"切换设备" [31,847]×[177,888] | 静态 | 只读 | — | 已转正 `SWAN_DEVICE_SHEET_TITLE`（2026-09-10 verify 图断言通过，标题行整条；设备行 动态 不截） | 已验证 |
| 纱罩 | desc='纱罩' [0,0][720,792]（无无障碍键） | 静态 | click 关闭（未实测，用 press_back） | 弹层消失 | 待截 | 已验证（press_back 实测关闭） |
| 设备行列表 | OCR 设备名（Libretto_0E00 / Maestro1100_A20C / HiVi M300MKII / 手机扬声器 / Apple Music） | 动态 | ⛔ 禁止点击（真实音箱） | — | 动态-不截图 | 已验证（2026-09-10 verify OCR 实测五行齐全） |
| 底部播放条 | `bottom_player`（无障碍键） | 静态 | click | `[[swan_播放页]]` | 已有图 | 已验证 |

设备行无无障碍键（仅 desc），顺序与内容随网络发现动态变化（family 内 Wi-Fi 设备 + AirPlay）。

### 元素截图（2026-09-10 aw-verify 真机验证通过，已转正 image/flutter/）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 标题行整条（「切换设备」，全宽；⚠️ 依赖播放页可达，本账号靠残留播放任务进入） | `SWAN_DEVICE_SHEET_TITLE` | image/flutter/swan_切换设备弹层_标题行.png |

## 页面布局

```
│ （播放页内容，被纱罩压暗）      │
│ ░░░░░░ 纱罩 ░░░░░░░░░░░░    │
├────────────────────────┤
│ 切换设备                  │  标题（左上）
│ ○ Libretto_0E00          │
│ ○ Maestro1100_A20C       │
│ ○ HiVi M300MKII          │
│   手机扬声器（当前，无圆点）    │
│ ○ Apple Music            │
└────────────────────────┘
```

## 功能关联

- 所属 feature：`[[feature_播放器]]`
- 上游：`[[swan_播放页]]`（player_device_button）
- 相关：AI 对话页「自动朗读设备」弹层（同款设备单选列表：HiVi M300MKII / 手机扬声器 / 全选 / 完成）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_播放器.md | [[feature_播放器]] |
| pages/swan_AI对话页.md | [[swan_AI对话页]] |
| pages/swan_播放页.md | [[swan_播放页]] |

_自动生成于 2026-09-14 13:38_
<!-- backlinks:end -->
