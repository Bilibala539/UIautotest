---
page_id: swan_AI对话页
name: "AI 对话页"
aliases: [AI角色对话, ai_chat]
route: null              # 首页·AI Tab 点角色卡进入，路由未在功能地图单列（待考古）
status: verified
last_updated: 2026-09-10
type: screen
package_name: com.swan.network
activity: null
orientation: portrait
---

# AI 对话页 (swan_AI对话页)

## 页面概述

AI 角色对话页，首页·AI Tab 点角色卡（惠威百科/小薇/惠声远）进入。顶栏：返回 + 角色名 +
副标题「暂无设备」（未绑定输出设备时）+ 三个功能图标（语音输入/字幕通话/自动朗读设备）。
中部为对话流（气泡），底部输入框「发送消息..」+ 发送按钮，页脚常驻「内容由AI生成」。

Wave2 实测（小薇）：发送"play a song"，AI 回复「音乐服务需要授权，请到音乐页面完成授权后再试」
——AI 点播同样被平台授权门禁拦截（可作为"未授权账号无法建立播放"的旁证用例）。

⚠️ 中文输入注意：`adb shell input text` 不支持非 ASCII（NPE），中文消息无法经现有 AW 输入，
只有 ASCII 消息可发；中文输入需 IME 方案（框架层，须用户决策）。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 角色名标题 | 出现 | OCR 角色名（顶栏 y≈116-162） | 进入本页 |
| 欢迎语 | 出现 | OCR"我是你的好朋友"（首次进入） | 对话区已渲染 |
| 页脚 | 出现 | OCR"内容由AI生成" | 页面完整加载 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_首页AITab]]` | `OCR"小薇"`（角色卡，卡片含头像图） | click | 见「生效断言」 |

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 返回按钮 | 无文案 ImageView [0,100][128,212] | static | press_back | 回 `[[swan_首页AITab]]` | 待截 | verified（press_back 实测） |
| 语音输入图标 | 顶栏图标① [432,116][512,196]（无 key/desc） | static | click | 系统麦克风权限弹窗（`permission_deny_button` 等系统 key） | 已转正 `SWAN_AI_CHAT_VOICE_BTN`（2026-09-10 verify 图断言通过；⛔ 未点击避免麦克风权限） | verified |
| 字幕/通话图标 | 顶栏图标② [528,116][608,196] | static | click | 进入通话态（OCR"字幕"+"按住说话"） | 待截 | draft（未验证） |
| 自动朗读设备图标 | 顶栏图标③ [624,116][704,196] | static | click | 「自动朗读设备」弹层（OCR"自动朗读设备"+"完成"） | 待截 | draft（未验证） |
| 对话流 | 文本节点（text 属性，非 desc） | dynamic | 只读 | — | dynamic-不截图 | verified（欢迎语 OCR 实测） |
| 输入框 | OCR"发送消息.."（无 key，[64,1418][588,1510]） | static | click 后 input_text（仅 ASCII） | 键盘弹出 | 已转正 `SWAN_AI_CHAT_INPUT`（2026-09-10 verify 图断言通过，含占位文案；不输入中文） | verified |
| 发送按钮 | 无文案图标（输入框右侧） | static | click | 消息气泡出现 | 待截 | draft（未验证） |

### 「自动朗读设备」弹层（本页内嵌 sheet）

列表：全选 / HiVi M300MKII / 手机扬声器（与 `[[swan_切换设备弹层]]` 同款设备单选，
⛔ 含真实音箱禁止选择），「完成」按钮关闭（OCR"完成"）。

### 系统麦克风权限弹窗（首次点语音输入）

系统权限弹窗，key 与扫一扫相机权限同族：`permission_allow_foreground_only_button`（使用时允许）/
`permission_allow_one_time_button`（仅本次使用时允许）/`permission_deny_button`（拒绝）。

### 元素截图（2026-09-10 aw-verify 真机验证通过，已转正 image/flutter/）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 顶栏语音输入图标① | `SWAN_AI_CHAT_VOICE_BTN` | image/flutter/swan_AI对话页_语音按钮.png |
| 底部输入框（含占位文案"发送消息.."，未获麦克风权限未点击，无弹窗干扰） | `SWAN_AI_CHAT_INPUT` | image/flutter/swan_AI对话页_输入框.png |

## 页面布局

```
┌────────────────────────┐
│ [←]  小薇       [🎤][字幕][朗读] │
│      暂无设备             │
│  （对话气泡流，dynamic）    │
│ [发送消息..........] [➤] │
│      内容由AI生成          │
└────────────────────────┘
```

## 功能关联

- 所属 feature：`[[feature_导航框架]]`（AI Tab 域；建议后续单列 feature_AI助手）
- 上游：`[[swan_首页AITab]]`（角色卡）
- 下游：自动朗读设备弹层（本页内）；对话记录回显在 AI Tab 历史对话记录区

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_导航框架.md | [[feature_导航框架]] |
| pages/swan_首页AITab.md | [[swan_首页AITab]] |

_自动生成于 2026-09-10 14:19_
<!-- backlinks:end -->
