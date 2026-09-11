---
flow_id: flow_导航_迷你播放器展开
name: "底栏迷你播放器展开为全屏播放页并收起（bottom_player → 播放页 → 收起回原页面）"
feature: "[[feature_导航框架]]"
status: 草稿
last_updated: 2026-09-10
automation: yes
risk: low
---

# 迷你播放器展开 (flow_导航_迷你播放器展开)

## 完成什么功能

在首页点击底栏迷你播放条（`bottom_player`）展开全屏播放页，断言播放页无任务态布局后，点左上收起按钮回到进入前的页面。验证播放器入口的展开/收起闭环。

## 前置条件

- 登录态：是
- 设备：真机已连接，App 停在 `[[swan_首页]]`（或任意可见 bottom_player 的页面）
- 账号数据：**无播放任务即可走通本 flow**（bottom_player 点击展开播放页不依赖播放任务；本 flow 的全部已知验证均基于无任务态）

## 步骤

| # | 页面 | 元素（locator） | 操作 | 预期 App 反应 |
|---|---|---|---|---|
| 1 | `[[swan_首页]]` | `bottom_player`（无障碍键，底部播放条） | click | 进入 `[[swan_播放页]]` |
| 2 | `[[swan_播放页]]` | `full_player_page`（无障碍键，页面根节点） | wait 断言 | 播放页生效断言通过（desc 含设备名+时间） |
| 3 | `[[swan_播放页]]` | `SWAN_PLAYER_DISMISS_BTN` / `SWAN_PLAYER_PLAY_PAUSE_BTN`（图） | `image_exists` 断言 | 顶栏收起按钮与五键控制条已渲染（无任务时播放钮为 ▶ 态）。⚠️ **risk**：五键控制（循环/上一首/播放暂停/下一首/队列）与音量为真实音箱安全约定，⛔ **只断言不点击** |
| 4 | `[[swan_播放页]]` | OCR"00:00" / OCR"扬声器" | 断言 | 无任务态进度占位与输出设备名可见。⚠️ **risk**：OCR"00:00" 仅无任务态有效，有任务时为动态时间，勿作固定断言 |
| 5 | `[[swan_播放页]]` | `player_dismiss_button`（无障碍键，左上收起） | click | 收起播放页，回到进入前的页面（`[[swan_首页]]`） |
| 6 | `[[swan_首页]]` | `tab_me`（无障碍键）/ `bottom_player`（无障碍键） | 断言 | 已回到首页，迷你播放条仍在底栏 |

## 断言点

| # | 类型 | 内容 |
|---|---|---|
| 1 | 无障碍键 | `wait_accessibility(full_player_page)` —— 进入播放页 |
| 2 | 图片 | `image_exists(SWAN_PLAYER_DISMISS_BTN)` —— 顶栏已渲染 |
| 3 | 图片 | `image_exists(SWAN_PLAYER_PLAY_PAUSE_BTN)` —— 播放钮（无任务 ▶ 态）存在，不点击 |
| 4 | OCR | "00:00"（无任务态进度占位） |
| 5 | 无障碍键 | 步骤 5 后 `tab_me` / `bottom_player` 重新可见（已收起回原页） |

## 风险与限制

- **risk（验证范围受限）**：全部已知验证（2026-09-08/10）基于**无播放任务**状态——本账号（13555555555）所有第三方平台未授权，无法建立任何播放任务（歌单/电台/AI 点歌三路均被授权弹层拦截）。有播放任务时的布局、队列 弹层、歌词视图**待已授权账号复验**（待验证）。
- **risk（图模板含动态区）**：`SWAN_BOTTOM_PLAYER_BAR` 截图含当前曲目名区，曲目变化时文字区会变（当前无任务恒为"扬声器 - -"）；作为 image_exists 断言可用，弱匹配阈值需留意。
- **risk（入口页面差异）**：bottom_player 并非全页面可见——`[[swan_搜索输入页]]` 等全屏独立路由无底栏；从搜索域页面不可直接展开。
- ⛔ `player_queue_button` 无播放任务时点击**无任何反应**（2026-09-10 实测），不要把"点队列"写进无任务态步骤。

## 对应用例

- `tests/flutter/test_swan_readonly_pages.py::test_player_open_close`
