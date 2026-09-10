# Wave 3 环境阻塞日志（2026-09-10）

## 结论

**目标设备 vivo X200 Pro（serial 10AF8A2U1Z006F0）未连接到本机，USB 与 adb 均不可见，
Wave 3 设备域探索无法执行。**

## 诊断过程（全部实测）

| # | 检查项 | 结果 |
|---|--------|------|
| 1 | `C:\platform-tools\adb.exe devices`（多次，含 kill/start-server 重启） | 空，无任何设备 |
| 2 | `adb -s 10AF8A2U1Z006F0 get-state` | error: device not found |
| 3 | Windows PnP USB 设备枚举（Get-PnpDevice） | 无 VID_2D95（vivo）设备；仅有：华为 BTK-W00 复合设备（VID_12D1&PID_107D，含 ADB Interface + Linux File-CD Gadget + 大容量存储，疑似智能音箱显示系统项目设备）、键盘鼠标、Realtek 蓝牙适配器 |
| 4 | adb 版本 | 37.0.0-14910828（C:\platform-tools\adb.exe，进程 9888 正常运行） |
| 5 | BTK-W00 的 ADB Interface 驱动 | WinUSB 绑定正常（Status OK），但 adb devices 不列出（该设备非本任务目标，其 adbd 未响应；且 pnputil restart-device 需管理员权限被拒） |
| 6 | `adb mdns services`（无线调试发现） | 无发现的服务 |
| 7 | 后台轮询 adb devices | 首轮 9 分钟（55×10s）无设备；延长轮询 15 分钟结果见下 |
| 8 | PnP 非 OK 状态设备 | 无（无未知设备/驱动错误） |
| 9 | Swan APK / 源码仓（备选静态分析） | 本机不存在：E:\SwanApp 目录不存在；全盘未找到 .apk；功能地图.md（E:\UIAutotest\功能地图.md）为另一台机器生成的静态测绘，仅含路由级信息 |

## 已完成的准备工作（设备接上即可继续）

- `E:\uiautotest\explorer_output\wave3\explore.py`：Wave 3 探索 runner（基于 wave2 脚本改造）
  - `ADB_PATH=C:\platform-tools\adb.exe`、`ANDROID_DEVICE_SERIAL=10AF8A2U1Z006F0`
  - 输出目录 wave3/dumps/ + screenshots/wave3/
  - 按本波红线**裁掉了 tap 坐标 / input 坐标命令**；新增 `ckp` 前缀匹配命令（设备卡 UUID 动态 key 用）
  - 已验证：导入链全通（为此向 venv 补装了 selenium——driver 包 __init__ 硬依赖），
    无设备时按预期在 `RuntimeError: ADB 设备不可用: 10AF8A2U1Z006F0` 快速失败
- venv 补装 selenium（环境依赖补充，未改任何仓库代码）

## 静态参考（来自 E:\UIAutotest\功能地图.md，未真机验证，不作为页面事实）

- 添加设备 `/device/add`（BLE/WiFi 双卡片）：add_device_page.dart:78
- BLE 配网 `/device/ble-provisioning`、WiFi 配网 `/device/wifi-provisioning`
- 兼容机型 `/device/compatible-model`：setting/compatible_model_page.dart
- 远程控制面板/侧栏：device_remote_control_sheet.dart
- 设备设置族：/device/setting、/device/network、/device/params、/device/voice、/device/name-edit（setting/ 目录）
- 固件升级、RCHIVE DSP `/device/rchive-dsp`、AW 耳机 `/device/aw-earphone`、低音炮 `/device/subwoofer/*`
