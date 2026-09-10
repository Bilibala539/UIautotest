# swan_个人信息页（个人信息修改）

> 状态：page（2026-09-08 真机 dump + verify 复验转正）

## 页面概述

头像/昵称/密码/手机号资料页，底部有注销账号与退出登入。**注销账号按钮就在退出登入上方，
自动化操作时严禁误点**。

## 进入方式

我的页点 `me_user_profile_entry`

## 关键元素（来源：uiautomator dump）

| key | 文案/说明 | clickable | 备注 |
|---|---|---|---|
| `person_info_page` | 页面根节点 | ✅ | |
| `person_info_cancel_account_button` | 注销账号 | ✅ | ⚠️ 危险操作，禁止在自动化中点击 |
| `person_info_logout_button` | 退出登入 | ✅ | 登出清理用 |

无 key：头像、昵称（惠威2b11）、密码（******）、手机号（13555555555）行。

## 行为要点

- 点退出登入后回到登录页（`login_page` 出现），已实测
- 登录态跨进程重启持久化：杀 App 重启仍在登录态；OPPO 设备 `pm clear` 无权限，
  自动化拿未登录状态的唯一途径是走登出流程

## 关联

- [[swan_我的页]]（上一级）
- [[swan_验证码登录页]]（登出后落地）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_账号体系.md | [[feature_账号体系]] |
| pages/swan_我的页.md | [[swan_我的页]] |
| pages/swan_资料编辑页.md | [[swan_资料编辑页]] |

_自动生成于 2026-09-10 14:19_
<!-- backlinks:end -->