# swan_密码登入页

> 状态：page（2026-09-08 explorer 采集 + verify 复验 + codegen 密码流程实测）
> 数据来源：验证码登录页点右上角"密码登入"实机 dump + OCR；截图 explorer_output/screenshots/swan_explore2/swan_login_password_page.png
> 密码输入/提交流程已于 2026-09-08 由 codegen 实测打通（正确密码登录成功、错误密码拒绝均有用例）

## 页面概述

密码登入页。与验证码登录页同根 `login_page`（同一路由的两种形态），右上角互切。
比验证码页多密码输入框，提交按钮文案为"登录"（验证码页为"下一步"），无第三方登录入口。

## 进入方式

- [[swan_验证码登录页]] 点 `login_use_password_button`（右上角"密码登入"，key 已实测）

## 关键元素（来源：uiautomator dump）

| 无障碍键 | 文案/说明 | 可点击 | 备注 |
|---|---|---|---|
| `login_page` | 页面根节点 | ✅ | 页面判据（与验证码页共用） |
| `login_use_sms_button` | "验证码登入" | ✅ | **新采集**：切回验证码登录的反向入口（实测可用） |
| `login_area_code_button` | "+86" | ✅ | 区号选择 |
| `login_phone_field` | 占位"请输入手机号" | ❌（外层可点） | [230,632][650,724] |
| `login_password_field` | 占位"请输入密码" | ❌（外层可点） | [70,748][542,840] |
| `login_submit_button` | "登录" | ✅ | 置灰态；⛔ 禁止点击提交 |
| `login_agreement_checkbox` | 协议勾选框 | ✅ | [100,996][160,1056] |
| `login_error_text` | "密码错误，请重新输入！" | ❌ | **codegen 实测新发现**：错误提示是常驻语义节点而非 toast，可 key 断言 |

无无障碍键 元素（OCR）：密码可见性切换（眼睛图标，密码框右侧 ≈(595,794)，dump 无独立节点）；
《隐私政策》《使用政策》链接（⛔ 授权/外部页类，勿点）。

## KEY_PASSWORD_FIELD 验证结论（本次核心任务）

**`login_password_field` 真实存在，推断值正确**（2026-09-08 密码登入页全量 dump 实测，
无障碍_exists 返回 True）。`SwanBusiness.KEY_PASSWORD_FIELD` 无需改值；
代码中的注释"⚠️ 尚未实机验证"已过时，由 codegen 更新为 ✅。

页面全部 login* key（dump 实测）：
`login_page` / `login_use_sms_button` / `login_area_code_button` / `login_phone_field` /
`login_password_field` / `login_submit_button` / `login_agreement_checkbox`

## 页面布局

```
┌────────────────────────┐
│            验证码登入 →   │  ← login_use_sms_button（反向入口）
│         (Swan logo)     │
│   登入后就可畅享音乐世界    │
│ [+86 ▾][请输入手机号]      │
│ [请输入密码        (👁)]  │  ← login_password_field
│ [      登录（置灰）]       │  ← login_submit_button
│ ☐ 已经阅读并同意《隐私政策》  │
│    和《使用政策》。        │
└────────────────────────┘
```

## 探索过程记录

- 进入路径实测：登出后落在验证码登录页 → click `login_use_password_button` → 本页
- 反向切换实测：click `login_use_sms_button` → 回验证码登录页（password_field 消失、use_password_button 重现）
- 之后经 `login_by_sms('13555555555')` 重登成功，登录态已恢复

## 行为要点（codegen 实测）

- 密码页 `press_back` 只收键盘（不像验证码输入页会退出 App）
- 提交失败后**表单状态残留**（已填文本 + 协议已勾选），重跑需重启 App 重置（登录页无持久化，重启回全新验证码形态）
- 互斥形态判据：验证码页有 `login_use_password_button` 无 `login_password_field`；密码页反之

## 缺口

- `login_area_code_button` 点开后的区号列表未探索
- 本页无"忘记密码"入口；连续多次错误密码的锁定策略未验证（自动化只试 1 次）
- 无专属图片模板，形态断言靠 key 三重校验

## 关联

- [[swan_验证码登录页]]（双向互切）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_账号体系.md | [[feature_账号体系]] |
| pages/swan_验证码登录页.md | [[swan_验证码登录页]] |

_自动生成于 2026-09-14 13:26_
<!-- backlinks:end -->