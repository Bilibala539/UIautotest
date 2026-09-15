# 模块卡片：login（登录/会话）

## 基线与范围

- 数据标签：`TEST-SYNTHETIC`；任务：`SWAN-20260907-001-login-archaeology`；角色：`archaeologist`。
- App 仓库：`E:\SwanApp\repos\flutter\HiVi-Network-FlutterApp`，`dev@4d1ed7b1d727f12906d6ac9fa9ed195966e464b3`（工作树有既有 `analysis_options.yaml` / `android/gradle.properties` / `pubspec.lock` 改动，未触碰）。
- Core 仓库：`E:\SwanApp\repos\flutter\hivi_network_flutter_core`，`dev@402853ab964f026761ba63130f495b9d213ea8b5`（工作树有既有 `analysis_options.yaml` / `pubspec.lock` 改动，未触碰）。
- 执行模式：只读考古；未设计/执行用例，未提 BUG，未修改源码，未提交推送，未写 02-用例库 / 03-BUG库。
- 范围：登录 UI 入口与路由、登录流程（短信/密码/第三方）、token 存储与会话失效、登出清理。绑定手机号、区号选择、扫码登录确认（pad）只记录入口与边界，不深挖。

## 架构归属（关键结论）

- **App 仓库是纯壳**：`lib/` 仅 `main.dart`、`main_ohos.dart`、`app_version_config.dart`，grep "login" 零命中。全部登录实现在 Core 仓；App 依赖 Core（相对路径）+ `swan_third_party_login`（`../hivi_network_flutter_core/packages/swan_third_party_login`，仅为读 iOS 集成契约而显式声明）。
- 登录是**启动状态机驱动**而非普通命名路由页面：首屏由 `AppStartupGate` 按 `AppStartupController.stage` 切换，`/login` 等命名路由只是深链别名。

## 入口与路由

- 启动链：App `lib/main.dart` → `AppBootstrap.run(pureFlutterStandalone: true)` → `AppStartupGate`（`LocaleAwareMaterialApp` 的 `home`）。
- 启动阶段（`app_startup_controller.dart:8-13`）：`initializing` → `privacyRequired`（登录页 + 隐私弹窗 overlay，`PopScope(canPop:false)`，不同意即 `AppSystemPort.exitApp()`）→ `loginRequired`（`PureFlutterLoginPage`）→ `authenticated`（`AppShell`）。
- token 恢复：`initialize()` 读隐私标记 → `storagePort.readAuthToken()`；token 存在则 `adoptToken` 直接进 `authenticated`，**不校验 token 有效性**（首屏不发校验请求，等业务接口业务码回来才判定失效）。
- 命名路由（`app_router.dart:6-8`，注册在 `pure_flutter_router.dart:678-686`）：`/login`、`/login/bind-phone`、`/login/area-code`（另有 `/me/scan/pad-login-confirm` 扫码登录确认，本轮不深挖）。
- 会话失效清栈：`AppStartupGate._clearRouteStackOnLogout`（`app_startup_gate.dart:150-168`）——`authenticated → loginRequired` 时 `PlatformCatalogNotifier.reset()` + 根 Navigator `popUntil(isFirst)`，否则用户会停留在 push 出来的二级页。

## 登录页（PureFlutterLoginPage，851 行）

- 两种模式：`_LoginMode.smsCode`（两步：手机号+协议 → 验证码）、`_LoginMode.password`（手机号+密码，`maxLength:16`，可切明文）。
- 短信流程：`_submitPhoneStep` → 同号且冷却中直接切验证码页（不再发码）；否则 `_requestSmsCode` 成功后 60s `ValueNotifier` 倒计时（仅内存，不落盘；返回手机号步保留，切模式才清）。
- 验证码自动提交：`_onSmsCodeChanged` 满 4 位即登录；`_smsLoginInFlight` 防并发；`_lastFailedSmsCode` 防 autofill 回填同一错误验证码重复提交（`pure_flutter_login_page.dart:499-506`）。
- 第三方：微信/微博/Apple，经 `SwanThirdPartyLogin.authorize` 取 credential 后仍走 `AppStartupController.loginWithThirdParty`（与短信共用收口）；`_thirdPartyLoginInFlight` 防重入；`ThirdPartyLoginException` 分 `isCancelled`（静默）/`isInProgress`（提示稍候）/其它。OHOS 由 `OhosRuntimeUiPolicy.hideThirdPartyLogin` 整块隐藏（兜住 Flutter-OH 误报 `Platform.isAndroid==true`）。
- 50015 分支：第三方登录返回 `code==50015`（未绑定手机号）→ 携 `BindPhoneRouteArgs(loginType, thirdPartyId, thirdPartyName)` push `/login/bind-phone`；绑定成功复用同一 token 收口。iOS Apple 首登 `includeThirdPartyName=false`（请求体不含 thirdPartyName），Android 微信/微博含昵称。
- 协议勾选：短信主按钮/密码主按钮/第三方图标均联动 `_agreementAccepted`；第三方图标「可见」由平台决定、「可点」仅由协议决定（授权中不置灰，避免微信中途返回后永久卡死）。

## 状态存储与 HTTP 契约（接口清单）

### 服务端 API（POST，base 由 `NetworkConfigFallbackStore.networkHost` 决定）

| 用途 | 路径 | 请求体 | 成功判定 | 响应 token |
|------|------|--------|----------|------------|
| 发送短信验证码 | `{base}/user/captcha` | `{area, tel}`（area 去 `+`、tel trim） | `success==true && code==200` | 无 |
| 登录/绑定 | `{base}/user/login` | 短信：`{area, tel, code, loginType:'0', password:''}`；密码：`{area, tel, code:'', loginType:'1', password}`；第三方：`{loginType, thirdPartyId, thirdPartyName?}`；绑定：短信 body + `thirdPartyId/thirdPartyName` | 同上且 `data.token` 非空 | `data.token` |
| 登出（服务端） | `{base}/user/logout` | `{}`（走 `PureFlutterMeUserPort.logout`，`pure_flutter_me_user_port.dart:202-203`） | `MeUserActionResult.success` | 无 |
| 日活上报 | `{base}/user/loginLog` | `{type:1}`（`DailyActiveReporter`，按 `HVDailyActiveLastReportDate` 自然日节流，先落盘再请求） | 失败仅记日志 | 无 |
| 区号列表（外部） | `https://www.mxnzp.com/api/phone_code/list`（`area_code_service.dart:29-32`，硬编码 app_id/app_secret，8s 超时） | — | 失败回退内置热门区号（中港澳门台） | — |

### token 存储位置（三处同步）

1. **持久层**：`SharedPreferences` key `auth_token`（`AppConstants.keyToken`，`storage_port.dart:62-75`）。写入前统一加 `Bearer ` 前缀（`AppStartupController._normalizeBearerToken`）。实现按平台：Android/iOS `SharedPreferencesStoragePort`；OHOS `OhosPreferencesStoragePort`（ArkTS ChannelKey）；测试/鸿蒙 POC `MemoryStoragePort`。**明文存储，无加密**。
2. **内存 fallback**：`NetworkConfigFallbackStore._httpToken`（静态，`network_config_port.dart:91-138`）——`adoptToken` 写入；`HttpClient` 每次请求经 `NetworkConfigPortScope.getHttpToken()` 同步到 `headerValue`，非空则 `headerKey='Authorization'` 注入 header（`http_client.dart:120-143`，对齐 Android `MyRetrofitManager`）。
3. **Dio 实例 header**：`HttpClient.instance.setToken/clearToken` + `PureFlutterAuthApi._dio.options.headers['Authorization']`。

### 环境与 base URL

- 默认 host（`network_config_port.dart:140-163`）：Release `https://network.hivi.com/api`；Debug/Profile `http://8.129.106.82/api`；`--dart-define=HIVI_API_BASE_URL=...` 显式覆盖；「关于我们」切服一次性写 API/AI HTTP/AI WebSocket 三地址。
- `PureFlutterAuthApi._baseUrl` 每次请求动态读取 fallback：切服登出后登录页无需重建即命中新环境（`pure_flutter_auth_api.dart:23-27`）。

## 会话失效与刷新

- **无 refresh token 机制**：全 Core 仓无 refreshToken 端点/逻辑；token 失效唯一出路是登出重登。
- 业务码事件（`business_code_event.dart:73-85`）：`30003`→loginTimeout、`30001`/`40006`→tokenInvalid、平台授权类、`50017`→unboundAllPlatforms。会话失效码集合 `{30003,30001,40006}`（`pure_flutter_business_code_handler.dart:16`），对齐 Android `outTimeLogin`。
- 分发链：`BusinessCodeInterceptor`（Dio 响应/错误拦截）与 `PureFlutterBusinessCodeHandler.handle` 共用 `BusinessCodeDispatcherScope`；HTTP 401/403 不走 Dio error（`validateStatus < 500`，`http_client.dart:64-66`），保证能从 body 解析业务码。
- `AppSessionInvalidationCoordinator`（`app_session_invalidation_coordinator.dart`）：**必须在 `runApp()` 前订阅**（否则首帧前返回 30003 时「收到 code 没人登出」）；仅 `isAuthenticated` 时才登出（手动登出后/停留登录页时在途回包不误报）；同一 code 2s 内去重；登出前置位 `_pendingSessionInvalidatedNotice`，由 `AppBusinessCodeListener` 消费并 Toast `loginStatusObsolete`（登录状态过时）。

## 登出清理路径

触发点 4 个：
1. 个人信息页「退出登入」（`person_info_page.dart:270-283`，testId `person_info_logout_button`）：`MeUserPort.logout()` 成功 → `AppStartupController.logout()`；失败仅 Toast 不清本地。无二次确认。
2. 取消账号（`person_info_page.dart:230-256`，`person_info_cancel_account_button`）：`requestAccountUnbind()` 成功 → logout。
3. 服务端会话失效：`logoutDueToSessionInvalidation()`（30003/30001/40006）。
4. 「关于我们」切换服务器（`about_detail_page.dart:208-211`）：**不请求旧服 logout，直接清本地 token** 回登录页（对齐 iOS）。

统一清理 `_clearSessionState`（`app_startup_controller.dart:175-189`）：
- `kvStorage.remove('lastUserInfoResponeBean')`（Me 用户信息缓存，对齐 Android outTimeLogin）；
- `SessionCollectionStateStore.qobuz.clearAll()`（Qobuz 收藏星标持久化缓存 `qobuz.detail_collection_state.v1`，防下个用户看到旧星标）；
- `storagePort.clearAuthToken()`；
- `authPort.logout()`（清 fallback token + Authorization header）；
- 随后 `AppStartupGate` 清路由栈 + `PlatformCatalogNotifier.reset()`。

## 错误处理路径

- UI 收敛：登录失败写 `AppStartupController.errorMessage` → `_LoginInlineError`（Selector 监听，不重建整页）→ `HttpUserMessageResolver.resolve` 转本地化文案；Dio 连接类错误不透出英文原文（`sanitizeApiFailureMessage` → networkNotConnected）。输入变化即清旧错误（`clearLoginError` / `_clearInlineError`）。
- `PureFlutterAuthApi._post` 捕获 `DioException`：响应体是 Map 则原样返回（业务码语义保留），否则包装 `{success:false, message:sanitized, code:statusCode}`。
- `_completeLogin`：失败或 token 不可用 → 仅置 errorMessage 返回原始结果（50015 由页面识别）；成功 → 写 token + adoptToken + 切 authenticated。busy 态由 `_setBusy` 管理。
- 兜底：`initialize()` 抛异常 → `_errorMessage` + 直接落 `loginRequired`（不白屏）。
- debug 预览：`app_bootstrap.dart:710-717` 注入 `MemoryStoragePort(authToken: 'Bearer debug-preview-token')`，仅 debug 平台，跳过自动 HTTP。

## 自动化定位（HiviTestIds + ValueKey）

- Semantics ID（`hivi_test_ids.dart:12-27,156-162`）：`privacy_dialog` / `privacy_agree_button` / `privacy_disagree_button` / `login_page` / `login_phone_field` / `login_area_code_button` / `login_agreement_checkbox` / `login_submit_button` / `login_code_field` / `login_password_field` / `login_use_password_button` / `login_use_sms_button` / `login_error_text` / `login_third_party_{wechat,weibo,apple}_button` / `me_page` / `me_user_profile_entry` / `person_info_page` / `person_info_logout_button` / `person_info_cancel_account_button`。
- Widget ValueKey（与 Semantics ID 并存，双轨维护）：`login-phone-field`、`login-area-code-button`、`login-submit-button`、`login-agreement-checkbox`、`login-code-field`、`login-password-field`、`login-resend-code-button`。
- 登录页 UI 度量按 Android 原生 `LoginActivity`/`LoginByPswActivity` 复刻（`auth_native_style.dart`）；隐私弹窗按 AppCompat AlertDialog 逐像素复刻（`app_startup_gate.dart:272-476`）。

## 与其它模块/已知问题的关联

- **module-17-search**：搜索走 `AuthApi.get`（`music_secondary_http_service.dart:27-90`）→ 同一业务码分发链，搜索在途响应带回 30003/30001/40006 同样触发全局登出清栈；`suppressGlobalPlatformAuthPrompt` 只抑制平台授权 Toast，不抑制会话失效。登录态是搜索入口前置（搜索入口全部位于 authenticated shell 内）。
- **ANR 候选 SWAN-BUG-20260904-004**：SWAN-20260904-005 复核时 hierarchy 已可达登录页（stage=loginRequired），登录页是 ANR 后验证「应用恢复可用」的第一落点；登录页自身的主线程敏感点（60s 倒计时 Timer、autofill 触发的自动登录提交、第三方 SDK 授权回调）是 ANR 复现任务需覆盖的观察面。
- **平台授权（QQ/网易/酷狗/Apple/Qobuz）**：与账号登录解耦，走 `BusinessCodeController` pendingAuthEvent Toast，本轮未深挖。

## 已知坑（考古发现，逆向用例粮草）

1. **区号列表是外部第三方依赖**：MXNZP 接口硬编码 app_id/app_secret 于 `area_code_service.dart:29-32`；外网不通时靠内置热门区号兜底，不阻断登录。
2. **环境隐式分支**：Debug 包默认打测试服 `http://8.129.106.82/api`、Release 默认线上；纯 Flutter 与 add-to-app 宿主环境可能不同，测试前必须确认实际 base URL。
3. **token 明文落 SharedPreferences** 且启动恢复不校验：手工改 `auth_token` 后冷启动会直接进 authenticated，首个业务请求才暴露失效。
4. **验证码倒计时不落盘**：杀进程重进冷却丢失；同号返回验证码页复用剩余时间，改号即清零（服务端「获取短信频繁」限制依赖客户端冷却）。
5. **验证码 4 位自动提交 + autofill 防重**：`_lastFailedSmsCode` 在用户修改输入前跳过重复提交——自动化重试同一错误码时页面会「无反应」，是设计行为非卡死。
6. **登录请求体带冗余字段**：短信登录固定上送 `password:''`、密码登录固定上送 `code:''`；绑定页参数 fallback `loginType:'2'`。
7. **切服登出不请求旧服 logout**：服务端会话残留属预期（对齐 iOS）。
8. **登出失败不清本地**：`/user/logout` 失败时 token 保留、停留原页（person_info），仅 Toast。
9. **隐私同意标记复用 `is_first_launch`（取反语义）**：`isPrivacyAccepted = !(getBool('is_first_launch') ?? true)`；OHOS 平台托管隐私声明时由 Flutter 侧直接写 true（双弹窗会被华为审核判体验问题）。
10. **会话失效去重窗口 2s**：同 code 2s 内重复事件被吞；登出后 `isAuthenticated=false` 会拦住后续在途失效码，避免误报。
11. **HiviTestIds 与 ValueKey 双轨**：黑盒自动化用 Semantics identifier（Appium ACCESSIBILITY_ID），widget test 用 ValueKey；两套必须同时维护。

## 未决问题（待确认，留给主对话）

- `AppStartupController.loginWithThirdParty` 在 AuthPort 非 `ThirdPartyAuthPort` 时返回 `const AuthLoginResult.failure()`（无 message 无 code）——实际运行路径是否存在该分支待确认。
- `40006` 具体出现在哪些服务端接口，源码中只有 Android 对齐注释，无出处，待接口侧确认。
- `OhosPreferencesStoragePort.readAuthToken` 的归一化回写分支（`ohos_preferences_storage_port.dart:49-60`）未逐行确认，OHOS 真机 token 行为待设备在环验证。
- 扫码登录确认（`pad_login_confirm_page.dart`、`scan_code_result_classifier.dart`）属扫码域，是否纳入 login 模块用例范围待主对话裁决。
- 密码登录 `loginType:'1'` 与旧原生版本服务端行为差异，需接口侧确认。

## 证据索引

- 逐条关键文件路径清单：`F:\SwanApp-Toolchain\results\SWAN-20260907-001-login-archaeology\evidence\key-files.md`（源机路径，本机只有知识库副本）
- 复用已有 ANR 证据：`F:\SwanApp-Toolchain\results\SWAN-20260904-005-search-execution\evidence\`（源机路径）

## 本机元素层校注（UIAutotest 真机实测 2026-09-08~09，与上文考古互补）

> 上文为源码考古结论（F 盘机器产出）；本节为 OPPO c0614b6a（Android 11, 720x1600）真机黑盒实测，事实来源 `knowledge/swan/pages/swan_验证码登录页.md`、`swan_验证码输入页.md`、`swan_密码登入页.md`。两视角冲突时以真机实测为准并登记。

- **Semantics key 实测可用**：`login_phone_field` / `login_submit_button` / `login_agreement_checkbox` / `login_use_password_button` / `login_use_sms_button` / `login_password_field` / `login_error_text` / `login_code_field` / `login_area_code_button` 均已在真机 dump 中验证存在，与上表 HiviTestIds 一致。
- **`SWAN_LOGIN_SUBMIT_BTN` 是置灰态模板**：图像模板只能做存在性断言；实际点击必须走 key `login_submit_button`。
- **坑 5（4 位自动提交）已由本机实现确认**：`SwanBusiness.login_by_sms()` 即利用"4 位填满自动提交"设计——网关取码后依次填入，无需手动点提交。
- **验证码获取走 otp-gateway**：真机测试不经外部 MXNZP（坑 1 与验证码下发无关）；路径 `https://testnetwork.hivi.com/api/user/captcha/mockCode?tel=`，网关部署在 .166:18080，pull 模式取码。
- **未登录态获取方式**：OPPO 无 `pm clear` 权限 → 拿未登录态**只能走登出流程** `logout_if_needed()`；登录态跨进程持久。
- **测试账号在 `.env.local`**（SWAN_PHONE / 密码），conftest 自动加载；与源机"任务卡按需下发"的凭据纪律等效，但登记于 credentials-registry.md。
- **密码登录端到端已通**：`test_swan_password_login.py` 走 `login_password_field` + `login_error_text` 断言，密码错误提示为常驻语义节点，可无障碍键断言（呼应"错误处理路径"节的 `_LoginInlineError`）。
