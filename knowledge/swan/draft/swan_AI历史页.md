---
page_id: swan_AI历史页
name: "AI 历史对话记录"
aliases: [AI历史, ai_history, 历史对话记录页]
route: /ai/history
status: draft
last_updated: 2026-09-10
type: screen
package_name: com.swan.network
activity: null
orientation: portrait
---

# AI 历史对话记录 (swan_AI历史页)

## 页面概述

AI 对话历史全量页（路由 /ai/history，ai_history_page.dart）。标题「历史对话记录」，
下方为会话记录列表（每条：会话首句摘要 + AI 回复摘要，整行可点）。
点击记录行 → 进入对应对话的 `[[swan_AI对话页]]`（对话内容回显）。
本账号仅 1 条历史（Wave2 发送的 "play a song"）。
页面极简：顶栏返回 + 标题 + 列表，无底部 tab、无 accessibility key。

注意区分：首页·AI Tab 也有一个「历史对话记录」**区块**（内嵌摘要），
点区块内的记录行直接进 AI 对话页；只有点区块**标题行本身**（可点 ImageView）才进本页。
从本页/AI 对话页 press_back 均回 AI Tab（对话页在栈上替换，不回本页）。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 页面标题 | 出现 | OCR"历史对话记录"（顶栏居中，且顶 tab 行/角色卡区消失） | 进入本页（非 AI Tab 内嵌区块） |
| 会话记录 | 出现 | OCR 记录首句（如 "play a song"） | 列表渲染完成 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_首页AITab]]` | `OCR"历史对话记录"`（区块标题行本身，⚠️ 不是记录行；无 key，可点 ImageView） | click | 见「生效断言」（2026-09-10 Wave5 实测） |

自然语言补充：AI 对话页顶栏三图标（语音/字幕通话/自动朗读设备）均不是历史入口；
本页入口只有 AI Tab 历史区标题行这一个。

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 返回按钮 | 顶栏左上图标（无 key 无文案，[0,72][128,184]） | static | click / press_back | 回 `[[swan_首页AITab]]` | 待截 | verified（press_back 实测，落地 AI Tab） |
| 页面标题行 | `OCR"历史对话记录"`（顶栏居中，OCR (252,110,469,150)） | static | 只读断言（region 限定顶栏） | 进入本页 | `swan_AI历史页_标题行.png`（正式） | draft（图像已采集，2026-09-10 aw-verify 真机存在断言通过后转正） |
| 会话记录行 | OCR 记录摘要文案（如 "play a song"，整行可点；无 key） | dynamic | click | `[[swan_AI对话页]]`（对应对话回显，2026-09-10 Wave5 实测） | dynamic-不截图 | verified |
| 空态 | 本账号未出现（已有 1 条历史）；推测无历史时显示空态文案（未验证） | dynamic | 只读 | — | dynamic-不截图 | draft |

### 元素截图（image/flutter）

| 常量 | 文件（image/flutter，正式；2026-09-10 aw-verify 真机验证通过后转正） |
|---|---|
| `SWAN_AI_HISTORY_TITLE` | `swan_AI历史页_标题行.png`（2026-09-10 Wave5 采集，真机 find_image 0.8 通过） |

## 页面布局

```
┌────────────────────────┐
│ [←]   历史对话记录       │
│ [头像] play a song       │
│        音乐服务需要授权…  │
│ （更多会话记录…）         │
└────────────────────────┘
```

## 功能关联

- 所属 feature：建议新单列 `feature_AI助手`（AI 对话域）
- 上游：`[[swan_首页AITab]]`（历史对话记录标题行）
- 下游：`[[swan_AI对话页]]`（记录行）
- 功能地图对照：AI 历史 /ai/history [已扫描-未考古] → 本页实测补全
