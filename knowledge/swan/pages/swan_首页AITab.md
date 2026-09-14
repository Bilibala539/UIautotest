---
page_id: swan_首页AITab
name: "首页·AI Tab"
aliases: [AITab, home_ai_page, AI角色主页]
route: /home/aiRoles
status: 已验证
last_updated: 2026-09-14
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 首页·AI Tab (swan_首页AITab)

## 页面概述

首页五顶 Tab 之一（AI 角色主页，路由 /home/aiRoles）。上半部为 AI 角色卡横向滑动区
（当前账号可见角色：惠威百科 / 小薇 / 惠声远，左右有翻页箭头），下方一排入口：
「添加更多AI角色」「AI 角色设置」；再下方「历史对话记录」区（新账号为空态：
暂无对话记录 / 你与AI的对话将展示在这里）。除公共 key 外无任何 无障碍键。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 入口文案 | 出现 | OCR"添加更多AI角色" | AI Tab 已生效 |
| 历史区标题 | 出现 | OCR"历史对话记录" | 页面加载完成 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_首页]]` | `OCR"AI"`（顶部 Tab 行） | click | 见「生效断言」 |
| `[[swan_首页音乐Tab]]` 等其它顶 Tab | `OCR"AI"`（顶部 Tab 行） | click | 见「生效断言」 |

注意：`go_home()` 只回首页容器，顶部 Tab 停留在上次选择。
"AI"为短文案，OCR 命中顶部 Tab（y≈121）优先于页面内"AI 角色设置"（y≈737），实测稳定；
建议 codegen 用 region 限定顶部 Tab 行区域提高鲁棒性。

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 顶部 Tab 行 | `OCR"AI"`（region 限定顶栏）/ `SWAN_HOME_TAB_AI`（图，未选中态） | 静态 | click | 本页生效断言 | 已截 | 已验证 |
| AI 角色卡（惠威百科/小薇/惠声远） | OCR 角色名 | 动态 | ⛔ 不点（进 AI 对话 /ai/chat，本轮未探索） | — | 动态-不截图 | 草稿 |
| 角色卡左右翻页箭头 | 无无障碍键 无文案（图标） | 静态 | 未实测 | — | 待截 | 草稿 |
| 添加更多AI角色 | `OCR"添加更多AI角色"` / `SWAN_HOME_AI_ADD_ROLE`（图，整 pill） | 静态 | click | — | 已截 | 已验证 |
| AI 角色设置 | `SWAN_HOME_AI_ROLE_SETTINGS`（图，右 pill；⚠️ 实为图标按钮无文案，OCR 无文本） | 静态 | click（2026-09-10 实测：落地「所有角色」页，含系统角色列表+自定义区） | 落地页标题"所有角色" | 已截 | 已验证 |
| 历史对话记录标题 | `OCR"历史对话记录"` | 静态 | 只读断言 | — | 待截 | 草稿 |
| 历史对话空态 | `OCR"暂无对话记录"` | 动态 | 只读 | — | 动态-不截图 | 草稿 |
| 底部播放条 | `bottom_player`（resource-id） | 静态 | click | `[[swan_播放页]]` | 已有图 | 草稿 |
| 底部 4 tab | `tab_recommend` 等（resource-id） | 静态 | click | 对应 tab 页 | 已有图 | 草稿 |

### 元素截图（image/flutter）

### 元素截图（image/flutter，2026-09-10 aw-verify 真机走通复验通过，promote_image 已转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 添加更多AI角色（左 pill 含文案） | `SWAN_HOME_AI_ADD_ROLE` | image/flutter/swan_首页AITab_添加角色入口.png |
| AI 角色设置（右 pill 图标按钮，无文案） | `SWAN_HOME_AI_ROLE_SETTINGS` | image/flutter/swan_首页AITab_角色设置入口.png |
| 顶部 Tab「AI」（未选中态） | `SWAN_HOME_TAB_AI` | image/flutter/swan_首页_AITab按钮.png |

## 页面布局

- 顶栏：五顶 Tab 行（本 Tab 为"AI"）
- 内容区：
  - AI 角色卡横滑区（3 张卡可见，卡高约 264px，含角色形象/名称/问候语——问候语"你好，我是你的好朋友，小薇"随选中角色变化，动态）
  - 入口行：「添加更多AI角色」+「AI 角色设置」（同一行）
  - 「历史对话记录」区（列表或空态）
- 底栏：`bottom_player` + 底部 4 tab

## 功能关联

- 所属 feature：`[[feature_导航框架]]`（首页域）；AI 助手域（功能地图：AI 对话 /ai/chat、AI 历史 /ai/history、角色编辑 /ai/role/create、角色管理 /ai/role/manage、AI 平台管理 /ai/platform/manage、实时通话 /ai/realtime-call，均未探索）
- 上游：`[[swan_首页]]`
- 下游：`[[swan_AI对话页]]`（角色卡进入，2026-09-10 Wave2 实测；路由是否为 /ai/chat 待考古）、角色管理（未探索）、`[[swan_播放页]]`

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_导航框架.md | [[feature_导航框架]] |
| pages/swan_AI历史页.md | [[swan_AI历史页]] |
| pages/swan_AI对话页.md | [[swan_AI对话页]] |
| pages/swan_所有角色页.md | [[swan_所有角色页]] |
| pages/swan_角色编辑页.md | [[swan_角色编辑页]] |
| pages/swan_首页音乐Tab.md | [[swan_首页音乐Tab]] |

_自动生成于 2026-09-14 15:41_
<!-- backlinks:end -->