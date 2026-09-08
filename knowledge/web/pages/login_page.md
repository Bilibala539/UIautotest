---
page_id: login_page
name: "登录页"
aliases:
  - 登录
  - Sign in
status: verified
last_updated: 2026-09-01
signature:
  - TidyTree
  - Sign in to your workspace
  - Password sign-in
type: route_state
route: /agents?view=agents
auth_state: anonymous
---

# 登录页 (login_page)

## 页面概述

访问受保护路由时展示的 TidyTree 密码登录状态。登录成功后回到目标路由的 Agents 列表。

## 进入方式

| 来源页面 | 操作 | 验证 |
|---|---|---|
| 未登录浏览器 | 访问 `/agents?view=agents` | 显示 “Sign in to your workspace” |
| 会话失效 | 刷新受保护路由 | 重新显示登录表单 |

## 退出方式

| 目标页面 | 操作 | 验证 |
|---|---|---|
| [[agents_page]] | 使用环境变量中的测试账号提交登录表单 | `m8-agents-page` 可见 |

## 页面布局

```
┌─────────────────────────────┐
│ TidyTree                    │
│ Sign in to your workspace   │
│ [Name                    ]  │
│ [Password                ]  │
│ [Sign in]                   │
│ Third-party sign-in         │
└─────────────────────────────┘
```

## 关键元素

| 元素 | 稳定定位器 | 操作 | 验证状态 |
|---|---|---|---|
| 用户名输入框 | `input[placeholder='Name']` | `send_keys` | 已实测 |
| 密码输入框 | `input[placeholder='Password']` | `send_keys` | 已实测 |
| 登录按钮 | role=button, name=`Sign in` | `click` | 已实测 |
| 企业微信登录 | aria-label=`Sign in with WeCom (scan QR code)` | 不纳入首批自动化 | 已实测 |

## 测试数据与安全

1. 账号和密码只从 `TIDYTREE_USERNAME`、`TIDYTREE_PASSWORD` 环境变量读取，禁止写入文档、代码或日志。
2. 登录用例只验证会话建立；修改密码、找回密码和第三方登录需单独建模。
3. 测试结束应清理浏览器 Cookie 与 localStorage，避免会话串用。

## 关联

| 关联页面 | 关系类型 | 说明 |
|---|---|---|
| [[agents_page]] | navigates_to | 登录成功后的目标页面 |

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/flows/agent_list_read_only.md | [[agent_list_read_only]] |
| pages/agents_page.md | [[agents_page]] |
| digest/platform_profile.md | [[platform_profile]] |

_自动生成于 2026-09-01 10:16_
<!-- backlinks:end -->