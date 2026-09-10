# swan_验证码输入页

> 状态：page（2026-09-08 真机 dump + verify 复验转正）
> 数据来源：实机操作 dump（输入手机号点"下一步"后的页面）

## 页面概述

输入手机号点"下一步"后进入。App **自动发送**验证码（无"获取验证码"按钮），顶部提示
"验证码已经发送至+86 13555555555"，下方"重新发送(54s)"倒计时。验证码 4 位，
**填满第 4 位自动提交**，成功直接进首页。

## 进入方式

登录页输入手机号 → 勾选协议 → 点 `login_submit_button`（下一步）

## 关键元素（来源：uiautomator dump）

| key | 文案/说明 | clickable | 备注 |
|---|---|---|---|
| `login_page` | 页面根节点（与登录页同根） | ✅ | |
| `login_code_field` | 验证码输入框 | ❌（内层节点可点） | 已固化 KEY_CODE_FIELD |
| 重新发送(54s) | 重发倒计时（OCR 文本，无 key） | ✅ | 倒计时结束才可点 |


### 元素截图（image/flutter，2026-09-08 aw-element 采集 + verify 复验转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 验证码输入框（4 格整体，空态） | `SWAN_LOGIN_CODE_FIELD_BOX` | image/flutter/swan_验证码输入框.png |
## 行为要点

- 验证码自动提交：`input_text(code)` 后无需点任何按钮，等 `tab_me` 出现即登录成功
- 验证码有效期 5 分钟（网关 expireAt）
- 从本页回退（press_back）回到登录页

## 关联

- [[swan_验证码登录页]]（上一步）
- [[swan_首页]]（成功后落地）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_账号体系.md | [[feature_账号体系]] |
| pages/swan_首页.md | [[swan_首页]] |
| pages/swan_验证码登录页.md | [[swan_验证码登录页]] |

_自动生成于 2026-09-10 14:19_
<!-- backlinks:end -->