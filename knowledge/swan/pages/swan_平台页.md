# swan_平台页

> 状态：page（2026-09-08 真机 dump + OCR + verify 复验转正）
> 数据来源：登录态下首页点 tab_platform 实机 dump；截图 explorer_output/screenshots/swan/swan_平台页

## 页面概述

平台页：展示惠币（HC）总资产、充值入口、消费明细入口，以及按 音乐/AI/电台 分类
的第三方平台授权列表（QQ音乐/Spotify/网易云音乐/酷狗音乐/Apple Music/Qobuz，
当前账号全部"未授权"）。底部播放条与全局 tab 栏持续可见。

## 进入方式

- 首页（或任意全局 tab 页）点 `tab_platform`

## 关键元素（来源：uiautomator dump）

| key | 文案/说明 | clickable | 备注 |
|---|---|---|---|
| `platform_page` | 页面根节点（文本含"平台/总资产（惠币/HC）/0.50000000/充值购买便可购买更多服务哦"） | ❌ | 可作页面判据 |
| `netease_platform_entry` | 网易云音乐 未授权 | ✅ | 唯一有 key 的平台行 |
| `bottom_player` | 底部播放条 | ✅ | 全局 |
| `tab_recommend` / `tab_platform` / `tab_device` / `tab_me` | 全局 tab | ✅ | |

无 key 的 OCR 文本元素：

| 文案 | clickable | 备注 |
|---|---|---|
| 消费明细（右上角） | ✅ | 待探索（未点） |
| 充值 + 充值按钮（VIP 卡片右侧，OCR"充值"） | ✅ | 涉及真实付费，未点 |
| 音乐 / AI / 电台（左侧分类栏） | ✅ | 分类切换，未点 |
| QQ音乐/Spotify/网易云音乐/酷狗音乐/Apple Music/Qobuz 行 | ✅ | 各行右侧有一个"+"图标按钮（OCR 识别为 +/?，无 key，推测为授权/添加入口，未点） |


### 元素截图（image/flutter，2026-09-08 aw-element 采集 + verify 复验转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 网易云音乐授权行（整行卡片，⚠️ 含「未授权」状态文字，授权后该行文案会变） | `SWAN_PLATFORM_NETEASE_ROW` | image/flutter/swan_平台_网易云音乐行.png |
## 页面布局

```
┌────────────────────────┐
│ 平台          [消费明细] │
│ VIP 总资产（惠币/HC）      │
│ 0.50000000      [充值]   │
│ 充值购买便可购买更多服务哦   │
│──────┬─────────────────│
│ 音乐 │ QQ音乐  未授权 [+] │
│ AI   │ Spotify 未授权 [+] │
│ 电台 │ 网易云音乐 未授权[+] │  ← netease_platform_entry
│      │ 酷狗音乐 未授权 [+] │
│      │ Apple Music 未授权[+]│
│      │ Qobuz   未授权 [+] │
│ [bottom_player 扬声器 - -] │
│ 首页 | 平台 | 设备 | 我的   │
└────────────────────────┘
```

## 缺口

- 充值/消费明细/平台授权按钮均未点击（涉及真实资产/授权，留待用户决策或专项测试）
- AI、电台分类页签内容未探索
- 平台行右侧"+"按钮无 key，后续需 element 截图或 OCR 文案确认

## 关联

- [[swan_首页]]（tab 切换）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| pages/swan_首页.md | [[swan_首页]] |

_自动生成于 2026-09-09 08:29_
<!-- backlinks:end -->