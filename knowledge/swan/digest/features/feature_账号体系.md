---
feature_id: feature_账号体系
name: "账号体系"
aliases: [登录, 会话]
status: draft
last_updated: 2026-09-10
domains: [会话与登录, 个人中心]
---

# 账号体系 (feature_账号体系)

## 功能定义

覆盖登录（短信验证码/密码）、登出、会话恢复、个人信息查看与编辑。token 三处存储、无 refresh 机制；登出有 4 个触发点并清空路由栈。

## 包含页面

| 页面 | 角色 | 状态 |
|---|---|---|
| `[[swan_验证码登录页]]` | 主入口（短信） | page |
| `[[swan_密码登入页]]` | 主入口（密码） | page |
| `[[swan_验证码输入页]]` | 登录流程中段 | page |
| `[[swan_个人信息页]]` | 登录后资料查看 | page |

缺口（见 digest/页面覆盖对照.md）：绑定手机页 `/login/bind-phone`、区号选择 `/login/area-code`、资料编辑族 `/me/edit-*`、账号解绑（⛔ 危险）。

## 包含 flow

- （待建）flow_登录_密码登录
- （待建）flow_登录_验证码登录 —— 依赖短信网关 192.168.12.166

## 边界与危险操作

- 账号解绑 `/me/account-unbind`：只断言入口，不点击确认。
- 第三方登录（微信/微博/Apple）：拉起外部 App，只断言按钮存在。
