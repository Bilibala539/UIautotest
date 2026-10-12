# Swan Flutter 用例

本目录只放用例文件。Flutter 当前复用 Android ADB 传输和 `AWBase`，运行时设置 `PLATFORM=flutter`。

## 目录结构

- **`test_*.py`（中文命名）：全部用例**——一用例一文件一 test 方法（CLAUDE.md 规则 8 铁律），文件名 = 用例名，`test_` 前缀是 pytest 收集 + run_parallel 匹配的硬约束；同一场景的数据变体用 `@pytest.mark.parametrize` 挂在该方法上
  - 回归域 14 个（用例 11-72，见 docs/Swan回归用例AW实现方案.md §4 清单）
  - 登录域/只读页 12 个（验证码登录、登录态重启持久化、登出回登录页、登录登出闭环、登录页形态互切、密码登录成功、错误密码拒绝、首页/平台页/设备页只读断言、播放页开关、收藏分组详情；2026-10-12 从 3 个多方法存量文件拆分，key 定位迁移待拍板）
- `test_case_driver.py`：YAML 用例执行载体（**平台执行链依赖**——pipeline_agent 默认 target、dashboard YAML 用例映射的 node id 都指向它；规则 8 唯一例外，勿删勿改名）
- 用例间共用的前置/清理编排不在本目录，位于 `utils/aw/business/swan_regression.py`（三个 mixin：播放器域 SwanPlayerRegressionMixin / 内容域 SwanContentRegressionMixin / 登录域 SwanLoginRegressionMixin）

## 登录 AW

通过 `user.login()` 调用 `SwanBusiness.login`，默认使用环境变量 `SWAN_PHONE`、`SWAN_PASSWORD` 进行密码登录；也可显式传入 `user.login(phone, password)`。验证码登录使用 `user.login(phone, method="sms", wait_code=60)`，复用已有验证码平台配置。

调用前需打开 App 并停在登录页或显示底部导航的已登录页面。已登录时复用当前会话并回首页，不验证当前账号是否与传入手机号一致，也不自动切换账号；需要切号时先调用 `user.logout_if_needed()`。未登录时先验证凭据，再重启 App 清除残留输入和协议勾选状态，最后登录并确认首页。包名可通过 `SWAN_PACKAGE` 配置，默认 `com.swan.network`。显式空凭据会报错，密码中的首尾空格保留；登录或页面等待失败直接抛出。
