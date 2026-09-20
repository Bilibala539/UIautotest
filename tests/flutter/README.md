# Swan Flutter 用例

本目录存放 Swan Flutter 用例及其 OTP 登录服务配套测试。Flutter 当前复用 Android ADB 传输和 `AWBase`，运行时设置 `PLATFORM=flutter`。

## 登录 AW

通过 `user.login()` 调用 `SwanBusiness.login`，默认使用环境变量 `SWAN_PHONE`、`SWAN_PASSWORD` 进行密码登录；也可显式传入 `user.login(phone, password)`。验证码登录使用 `user.login(phone, method="sms", wait_code=60)`，复用已有验证码平台配置。

调用前需打开 App 并停在登录页或显示底部导航的已登录页面。已登录时复用当前会话并回首页，不验证当前账号是否与传入手机号一致，也不自动切换账号；需要切号时先调用 `user.logout_if_needed()`。未登录时先验证凭据，再重启 App 清除残留输入和协议勾选状态，最后登录并确认首页。包名可通过 `SWAN_PACKAGE` 配置，默认 `com.swan.network`。显式空凭据会报错，密码中的首尾空格保留；登录或页面等待失败直接抛出。

纯单元测试不连接设备、不请求验证码服务，可在项目根目录执行：

```powershell
.\venv\Scripts\python.exe -m unittest tests.flutter.test_swan_login_aw -v
```
