---
flow_id: flow_登录_验证码登录全链路
name: "验证码登录全链路：登录页输手机号 → 验证码输入 → 网关取码 → 自动提交 → 首页成功断言"
feature: "[[feature_账号体系]]"
status: 草稿
last_updated: 2026-09-10
automation: yes
risk: low
---

# 验证码登录全链路 (flow_登录_验证码登录全链路)

## 完成什么功能

未登录态下用测试手机号走完短信验证码登录：登录页输入手机号并勾选协议 → 点"下一步"由 App 自动发送验证码 → 从验证码网关取码填入 → 4 位填满自动提交 → 落地首页，`tab_me` 出现即登录成功。

## 前置条件

- 登录态：否（**未登录态是硬前置**）。获取未登录态唯一途径：我的 → 个人信息 → 退出登入（杀进程无效、OPPO 禁 pm clear，见 docs/runtime_experience.md）。
- 设备：真机已连接，App com.swan.network 可冷启动。
- 账号：测试手机号来自环境变量 `SWAN_PHONE`（当前 13555555555）。
- 网络：内网可达验证码网关 `SWAN_OTP_GATEWAY`（默认 `http://192.168.12.166:18080`，中心机）。

## 步骤

| # | 页面 | 元素（locator） | 操作 | 预期 App 反应 |
|---|---|---|---|---|
| 1 | `[[swan_验证码登录页]]` | 页面根节点 `login_page` | 冷启动 App（`adb shell monkey -p com.swan.network -c android.intent.category.LAUNCHER 1`），约 5s | 落到验证码登录页，`login_page` 出现 |
| 2 | `[[swan_验证码登录页]]` | `login_phone_field`（无障碍键，hint"请输入手机号"） | click 聚焦后 `input_text(SWAN_PHONE)` | 框内出现手机号 |
| 3 | `[[swan_验证码登录页]]` | `login_agreement_checkbox`（无障碍键） | click | 勾选"已经阅读并同意" |
| 4 | `[[swan_验证码登录页]]` | `login_submit_button`（无障碍键） | click | App **自动发送**验证码（页面无"获取验证码"按钮），进入 `[[swan_验证码输入页]]`。⚠️ **risk**：点击必须走无障碍键 `login_submit_button`，`SWAN_LOGIN_SUBMIT_BTN` 图是置灰态模板，仅作存在性断言，禁止 click_image |
| 5 | （App 外）验证码网关 | `GET <SWAN_OTP_GATEWAY>/api/test/otp/latest?phone=<SWAN_PHONE>` | `OtpClient.get_code(phone)` 轮询（默认 60s / 2s 间隔），返回记录 `code` 字段 | 拿到 4 位验证码。⚠️ **risk**：网关为内网 pull 模式（首次请求触发开发接口 `https://testnetwork.hivi.com/api/user/captcha/mockCode` 取码），需轮询等待；网关不可达时整条链路 BLOCKED |
| 6 | `[[swan_验证码输入页]]` | `login_code_field`（无障碍键，4 格输入框） | click 后 `input_text(code)` | **填满第 4 位自动提交**，无需点任何按钮 |
| 7 | `[[swan_首页]]` | `tab_me`（无障碍键，底部 tab 栏） | wait（轮询等待） | `tab_me` 出现 = 登录成功，落在首页推荐 Tab |

## 断言点

| # | 类型 | 内容 |
|---|---|---|
| 1 | 图片 | 步骤 4 后 `image_exists(SWAN_LOGIN_CODE_FIELD_BOX)` —— 验证码输入页 4 格输入框（空态）已出现 |
| 2 | OCR | 步骤 4 后出现"验证码已经发送至+86 <SWAN_PHONE>"（发送成功提示） |
| 3 | 无障碍键 | 步骤 7 后 `tab_me` 可见（登录态判据，首页文档定义） |
| 4 | OCR | 首页出现"最近播放"（首页内容区已渲染；两种布局轮换态下均存在，见 flow_导航_四tab切换 risk） |

## 风险与限制

- **risk（环境）**：验证码网关地址依赖内网中心机 192.168.12.166:18080（环境变量 `SWAN_OTP_GATEWAY` 可覆盖）；换网络/机房需确认可达。
- **risk（时序）**：验证码有效期 5 分钟（网关 expireAt），步骤 5-6 间不应插入长等待；网关 pull 模式首次请求可能延迟出码。
- **risk（前置）**：登录态持久（跨进程重启），用例前必须显式走"退出登入"，不能假设冷启动即未登录。
- 未消费的验证码可调 `OtpClient.consume(otp_id)` 使其立即失效（失败不影响用例）。

## 对应用例

- `tests/flutter/test_swan_login_logout.py::test_sms_login_success`
- `tests/flutter/test_swan_login_logout.py::test_sms_login_logout_roundtrip`
- `tests/flutter/test_otp_gateway.py` / `tests/flutter/test_otp_client.py`（网关/客户端单测）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_账号体系.md | [[feature_账号体系]] |

_自动生成于 2026-09-14 13:26_
<!-- backlinks:end -->