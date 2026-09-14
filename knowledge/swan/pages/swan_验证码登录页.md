# swan_验证码登录页

> 状态：page（2026-09-08 真机 dump + verify 复验转正）
> 数据来源：`explorer_output/flutter_debug/20260908_121910/`（截图 + semantics.json + ocr.txt）

## 页面概述

Swan（com.swan.network v5.3.0）启动后的默认落地页。手机号 + 验证码登录入口；右上角可切换到密码登入。设备 720×1528。

## 进入方式

- 启动 App：`adb shell monkey -p com.swan.network -c android.intent.category.LAUNCHER 1`，约 5s 后落到本页
- 从密码登录页：点右上角"密码登入"的反向切换（key 待密码页 dump 后补充）

## 关键元素（来源：uiautomator dump，无障碍键）

| 无障碍键 | 文案/说明 | 可点击 | 备注 |
|---|---|---|---|
| `login_page` | 页面根节点 | ✅ | |
| `login_use_password_button` | 密码登入（右上角切换） | ✅ | 已固化 SwanBusiness.KEY_USE_PASSWORD_BUTTON |
| `login_area_code_button` | +86（区号选择） | ✅ | |
| `login_phone_field` | 手机号输入框（hint：请输入手机号） | ❌ | 点击后聚焦输入 |
| `login_submit_button` | 下一步 | ✅ | 未输手机号时置灰 |
| `login_agreement_checkbox` | 已经阅读并同意勾选框 | ✅ | |
| 《隐私政策》 | 文案链接（无无障碍键） | ✅ | OCR 文本定位 |
| 《使用政策》 | 文案链接（无无障碍键） | ✅ | OCR 文本定位 |
| `login_third_party_wechat_button` | 微信登录 | ✅ | |
| `login_third_party_weibo_button` | 微博登录 | ✅ | |

⚠️ 验证码输入框 / 获取验证码按钮不在此页——输入手机号点"下一步"后进入的页面待探索
（`SwanBusiness.KEY_CODE_FIELD = "login_code_field"` 为推断值，未验证）。


### 元素截图（image/flutter，2026-09-08 aw-element 采集 + verify 复验转正）

| 元素 | 常量（image/image_name_mapping.py） | 图片文件 |
|---|---|---|
| 《隐私政策》链接 | `SWAN_LOGIN_PRIVACY_POLICY_LINK` | image/flutter/swan_隐私政策链接.png |
| 《使用政策》链接 | `SWAN_LOGIN_USAGE_POLICY_LINK` | image/flutter/swan_使用政策链接.png |
| 「下一步」按钮（⚠️ 截图为未输手机号的置灰态） | `SWAN_LOGIN_SUBMIT_BTN` | image/flutter/swan_下一步按钮.png |
## 页面布局

```
┌────────────────────────┐
│              密码登入 → │  login_use_password_button
│        [Swan logo]      │
│   登入后就可畅享音乐世界  │
│ ┌────────────────────┐ │
│ │ +86 ▾ | 请输入手机号│ │  login_area_code_button / login_phone_field
│ └────────────────────┘ │
│ ┌────────────────────┐ │
│ │       下一步        │ │  login_submit_button
│ └────────────────────┘ │
│ ☐ 已经阅读并同意        │  login_agreement_checkbox
│   《隐私政策》和《使用政策》│
│      (微信)   (微博)    │  third_party buttons
└────────────────────────┘
```

## 关联

- [[swan_密码登入页]]（click login_use_password_button 切换，2026-09-08 已探索；反向 login_use_sms_button 切回）
- [[swan_验证码输入页]]（输手机号点下一步后，待探索）
- [[swan_首页]]（登录成功后，待探索）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_账号体系.md | [[feature_账号体系]] |
| digest/flows/flow_登录_验证码登录全链路.md | [[flow_登录_验证码登录全链路]] |
| pages/swan_个人信息页.md | [[swan_个人信息页]] |
| pages/swan_区号选择页.md | [[swan_区号选择页]] |
| pages/swan_密码登入页.md | [[swan_密码登入页]] |
| pages/swan_验证码输入页.md | [[swan_验证码输入页]] |

_自动生成于 2026-09-14 13:26_
<!-- backlinks:end -->