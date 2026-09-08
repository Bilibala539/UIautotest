# UIAutotest 平台与用例说明

## 给同事的结论

框架现在按 Web、Android 和 Flutter 三个平台隔离测试资源。Flutter 值得作为独立平台入口加入，但不需要重新实现一套点击、输入、截图和 OCR 驱动：Swan 的 Flutter 页面运行在 Android 设备上，因此复用 ADB 传输，由 `AWBase` 统一提供操作能力即可。

## 平台和目录

| 平台变量 | 项目 | 测试用例目录 | 图片目录 |
| --- | --- | --- | --- |
| `web` | TidyTree | `tests/web/` | `image/web/`、`image_ai/web/` |
| `android` | 智能音箱 | `tests/android/` | `image/android/`、`image_ai/android/` |
| `flutter` | Swan | `tests/flutter/` | `image/flutter/`、`image_ai/flutter/` |

`image_ai` 是新截图的草稿区，验证稳定后再通过 `promote_image()` 转入 `image`。不同平台不共享图片，避免分辨率和视觉样式差异造成误匹配。

## AW 复用方式

用例只调用 `user.aw`，不在测试文件中写坐标，也不重复实现 OCR。常用方法包括：

- `find_text_by_ocr` / `click_text`：定位固定中文文案；
- `accessibility_exists` / `click_accessibility`：定位 Flutter 语义节点的 `resource-id`；
- `input_text`、`press_back`、`take_screenshot`：输入、返回和证据截图。

`AndroidAdbDriver` 负责 ADB 设备通信和 UIAutomator bounds 解析；`FlutterAndroidDriver` 只改变平台名并继承该实现，所以资源自动落到 Flutter 目录。OCR 引擎、模板匹配和点击封装仍只有一份，后续修复会同时惠及三个平台。

## Swan 登录登出用例

真正的 pytest 用例位于 `tests/flutter/test_swan_login_logout.py`，流程是：启动 Swan → 判断当前状态 → 必要时退出 → 输入手机号和密码 → 同意协议并登录 → 进入首页 → 退出 → 校验回到登录页。

旧的 `scripts/swan_login_logout_opencv_ocr.py` 现在只保留录屏、UI 树转储、追踪日志等诊断能力。它的文字查找、文字点击、语义节点点击均委托给 `AWBase`，不再维护独立 OCR 算法；因此调试脚本和正式 pytest 用例使用同一套定位逻辑。

## 运行条件

先确认设备和依赖：

```powershell
E:\UIAutotest\venv\Scripts\python.exe -m py_compile tests/flutter/test_swan_login_logout.py
adb devices
```

设置测试账号后运行：

```powershell
$env:PLATFORM = "flutter"
$env:ANDROID_DEVICE_SERIAL = "c0614b6a"
$env:SWAN_PHONE = "测试手机号"
$env:SWAN_PASSWORD = "测试密码"
E:\UIAutotest\venv\Scripts\python.exe -m pytest tests/flutter/test_swan_login_logout.py -v
```

没有设置账号时，用例会安全跳过；没有设备或 ADB 未配置时，Flutter/Android fixture 会明确报错。执行中的失败截图和日志位于 `output/`，不会写入正式图片目录。

## 当前验证状态

已验证 Python 文件编译通过，OTP 服务测试已通过；Swan 在非 Flutter 平台或未配置账号时自动跳过。真实登录尚未执行，因为当前 ADB 设备已断开且仓库环境没有测试手机号和密码；上次确认的 Swan 包名为 `com.swan.network`。
