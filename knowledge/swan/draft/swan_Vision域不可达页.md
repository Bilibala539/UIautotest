---
page_id: swan_Vision域不可达页
name: "Vision 可视音箱域页面族（壁纸/唤醒词/语音包/高级设置）"
aliases: [vision_wallpaper, 壁纸, wake_words, 唤醒词, voice_pack, 语音包, vision_advanced, 高级设置]
route: null              # 族内路由：/vision/wallpaper、/vision/wake-words、/vision/voice-pack、/vision/advanced-settings*
status: draft
last_updated: 2026-09-10
type: screen
package_name: com.swan.network
activity: null
orientation: portrait
---

# Vision 可视音箱域页面族 (swan_Vision域不可达页)

## 页面概述

**❌ 不可达（设备未绑定）**：Vision 域四个页面族——壁纸 /vision/wallpaper、唤醒词
/vision/wake-words、语音包 /vision/voice-pack、高级设置 /vision/advanced-settings*——
的唯一入口预计在绑定可视音箱后的 `[[swan_首页可视音箱Tab]]` 内容区。

2026-09-10 Wave5 实测（账号未绑定可视音箱）：可视音箱 Tab 内容区为一个**整体合并的
不可点 ImageView**（desc 含"添加可视音响/即刻开启沉浸式视觉与音乐交融的双重体验～/
暂未添加可视音箱，此功能不可使用"三段文案，占满 [0,184][720,1528]），
raw dump 确认无任何隐藏可点子节点——**未绑定态连一个入口都没有**。

⚠️ 与功能地图的出入：功能地图标注壁纸 /vision/wallpaper「允许未绑定预览」，
但真机未绑定态 UI 上不存在任何壁纸预览入口（Tab 内容区零可点节点）。
该说法未在 UI 层实现（或预览入口在其他路径，全页排查未见）。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 未绑定提示 | 出现 | OCR"暂未添加可视音箱"（已有 `SWAN_HOME_VISION_UNBOUND_HINT` 图） | Vision 域入口不可用的前置状态 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_首页可视音箱Tab]]` | —（未绑定态无入口） | — | ❌ 不可达 |

自然语言补充：绑定可视音箱设备后本 Tab 内容区预计出现壁纸/唤醒词/语音包/高级设置入口
（未验证）；「添加可视音响」引导区不可点且涉配网流程（⛔ 自动化禁止进入添加设备流程）。
设备页的可视音箱设备卡设置项（绑定后出现）可能也是入口之一（未验证）。

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| （不可达） | — | — | — | — | — | ❌ 未绑定无入口 |

## 页面布局

未触达。实现文件（功能地图）：vision_wallpaper.dart:48、
wake_words/vision_wake_words_page.dart、ai_roles/vision_voice_pack_page.dart、
advanced/vision_advanced_pages.dart（高级设置族）。

## 功能关联

- 所属 feature：`[[feature_导航框架]]`（首页域；建议单列 feature_可视音箱Vision）
- 上游：`[[swan_首页可视音箱Tab]]`（绑定后，未验证）
- 前置条件：**需要绑定可视音箱设备**（本测试机无可视音箱）
- 待办：有可视音箱设备后补测四页面与入口布局
