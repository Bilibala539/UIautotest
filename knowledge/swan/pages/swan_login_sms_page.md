# swan_login_sms_page（验证码登录页）

> 状态：draft（2026-09-08 真机 dump 验证，待 verify 导航走通后转正）
> 数据来源：`explorer_output/flutter_debug/20260908_121910/`（截图 + semantics.json + ocr.txt）

## 页面概述

Swan（com.swan.network v5.3.0）启动后的默认落地页。手机号 + 验证码登录入口；右上角可切换到密码登入。设备 720×1528。

## 进入方式

- 启动 App：`adb shell monkey -p com.swan.network -c android.intent.category.LAUNCHER 1`，约 5s 后落到本页
- 从密码登录页：点右上角"密码登入"的反向切换（key 待密码页 dump 后补充）

## 关键元素（来源：uiautomator dump，accessibility key）

| key | 文案/说明 | clickable | 备注 |
|---|---|---|---|
| `login_page` | 页面根节点 | ✅ | |
| `login_use_password_button` | 密码登入（右上角切换） | ✅ | 已固化 SwanBusiness.KEY_USE_PASSWORD_BUTTON |
| `login_area_code_button` | +86（区号选择） | ✅ | |
| `login_phone_field` | 手机号输入框（hint：请输入手机号） | ❌ | 点击后聚焦输入 |
| `login_submit_button` | 下一步 | ✅ | 未输手机号时置灰 |
| `login_agreement_checkbox` | 已经阅读并同意勾选框 | ✅ | |
| 《隐私政策》 | 文案链接（无 key） | ✅ | OCR 文本定位 |
| 《使用政策》 | 文案链接（无 key） | ✅ | OCR 文本定位 |
| `login_third_party_wechat_button` | 微信登录 | ✅ | |
| `login_third_party_weibo_button` | 微博登录 | ✅ | |

⚠️ 验证码输入框 / 获取验证码按钮不在此页——输入手机号点"下一步"后进入的页面待探索
（`SwanBusiness.KEY_CODE_FIELD = "login_code_field"` 为推断值，未验证）。

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

- [[swan_login_password_page]]（密码登入切换后）
- [[swan_login_code_page]]（输手机号点下一步后，待探索）
- [[swan_home_page]]（登录成功后，待探索）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| pages/swan_login_code_page.md | [[swan_login_code_page]] |
| pages/swan_person_info_page.md | [[swan_person_info_page]] |

_自动生成于 2026-09-08 15:00_
<!-- backlinks:end -->