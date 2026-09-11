---
flow_id: flow_<功能>_<路径名>
name: "一条端到端操作路径的中文描述"
feature: "[[feature_xxx]]"     # 所属功能域
status: 草稿                   # 草稿 → 已验证（pytest 跑通后）
last_updated: null
automation: yes                # yes | no（no = 只描述不自动化，说明原因）
risk: none                     # none | low | high（high = 破坏性操作，只断言不点击）
---

# 路径名 (flow_xxx)

## 完成什么功能

一句话：这条路径走完后，用户达成了什么。

## 前置条件

- 登录态：是/否
- 设备状态、网络、账号数据等

## 步骤

| # | 页面 | 元素（locator） | 操作 | 预期 App 反应 |
|---|---|---|---|---|
| 1 | `[[swan_我的页]]` | `tab_me`（无障碍键） | click | 我的页生效断言通过 |
| 2 | `[[swan_收藏页]]` | OCR"SWAN收藏" | click | 收藏页生效断言通过 |

## 断言点

| # | 类型 | 内容 |
|---|---|---|
| 1 | 图片 | `image_exists(SWAN_ME_FAVORITES_ROW)` |
| 2 | OCR | "我的家庭" 出现在收藏页 |

## 对应用例

- `tests/flutter/test_swan_xxx.py::test_xxx`
