# 构建工具链安装清单(.166 新机备料,2026-09-21)

> 用途:.166 重装系统后,主会话照本清单逐步执行重建 C:\build-env。
> 执行身份:admin PowerShell(每条命令可整段照抄);**每步验证输出无误再进行下一步**。
> 目录名必须精确:`C:\build-env\{jdk-17, jdk-21, android, flutter}`——build_swan_apk.py 的 DEFAULTS 与全部档案文档写死这些路径。
> 参考档案:docs/agent模块档案/打包构建.md(SDK 布局、坑 12 android-37 合成、坑 11 env 显式注入)。

## 0. 目录骨架

```powershell
New-Item -ItemType Directory -Force -Path C:\build-env\jenkins, C:\tools\scrcpy | Out-Null
```

## 1. JDK 17 Temurin(17.0.20.1)+ JDK 21

下载 zip 版(便携,不写注册表不污染 PATH)。国内镜像优先:

```powershell
# JDK17(TUNA 镜像,选 17.0.20+8 或最近的 17.0.2x;官网 https://adoptium.net/temurin/releases/?version=17 为准)
# https://mirrors.tuna.tsinghua.edu.cn/Adoptium/17/jdk/x64/windows/
# JDK21 同法:https://mirrors.tuna.tsinghua.edu.cn/Adoptium/21/jdk/x64/windows/
```

解压后**目录改名**(Adoptium zip 解出形如 jdk-17.0.2x+y,必须规整):

```powershell
Expand-Archive ~\Downloads\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_8.zip -DestinationPath C:\build-env\_tmp
Move-Item C:\build-env\_tmp\jdk-17.0.20.1+8 C:\build-env\jdk-17; Remove-Item -Recurse C:\build-env\_tmp
# JDK21 同法解压规整为 C:\build-env\jdk-21
```

验证:

```powershell
C:\build-env\jdk-17\bin\java.exe -version   # openjdk version "17.0.20.1"(或 17.0.2x)
C:\build-env\jdk-21\bin\java.exe -version   # openjdk version "21.x"
```

## 2. env.ps1(环境汇总注入,会话级不污染全局)

创建 `C:\build-env\env.ps1`,全文如下:

```powershell
# C:\build-env\env.ps1 —— 构建环境汇总注入(点源进当前会话,不改机器级 PATH)
$env:JAVA_HOME    = "C:\build-env\jdk-17"
$env:ANDROID_HOME = "C:\build-env\android"
$env:FLUTTER_HOME = "C:\build-env\flutter"
$env:FLUTTER_STORAGE_BASE_URL = "https://storage.flutter-io.cn"
$env:PUB_HOSTED_URL           = "https://pub.flutter-io.cn"
$env:PATH = "$env:FLUTTER_HOME\bin;$env:JAVA_HOME\bin;$env:ANDROID_HOME\platform-tools;$env:PATH"
```

用法与验证(每个新 PowerShell 窗口执行后续步骤前先点源):

```powershell
. C:\build-env\env.ps1
echo $env:JAVA_HOME   # C:\build-env\jdk-17
```

注:Jenkins SYSTEM 会话**不需要** env.ps1——build_swan_apk.py 的 build_env() 自行组装 env(坑 11 修复);此文件供交互式执行 sdkmanager/flutter 用。

## 3. Android SDK

### 3.1 cmdline-tools

下载 commandlinetools-win-<build>_latest.zip(官网 https://developer.android.com/studio#command-line-tools-only ;旧机用的是 11076708 版,可沿用):

```powershell
Expand-Archive ~\Downloads\commandlinetools-win-11076708_latest.zip -DestinationPath C:\build-env\android
# 官方 zip 解出 cmdline-tools\ 目录,SDK 目录布局要求其位于 cmdline-tools\latest\:
Move-Item C:\build-env\android\cmdline-tools\cmdline-tools C:\build-env\android\cmdline-tools\latest
```

### 3.2 装包(需 JAVA_HOME;分步执行分步验证)

```powershell
. C:\build-env\env.ps1
$sdkman = "C:\build-env\android\cmdline-tools\latest\bin\sdkmanager.bat"
& $sdkman "platform-tools"
& $sdkman "platforms;android-34" "platforms;android-36"
& $sdkman "platforms;android-37.0" "platforms;android-37.1" "platforms;android-37.2"
& $sdkman "build-tools;34.0.0" "build-tools;36.0.0"
# license 全部接受(出现 y/N 一律 y;或 yes | 一键管道)
& $sdkman --licenses
```

验证:`& $sdkman --list_installed` 列出以上全部包,无 Warning。

### 3.3 android-37 手工合成(Google 已停发 base 37,App 仓 AGP 8.13 要 'android-37';档案坑 12)

创建 `C:\build-env\fix-android37.py`,全文如下(改两个文件;**包身份以 package.xml 为准**,只改 source.properties 会报 inconsistent location):

```python
"""android-37 合成:拷贝 android-37.0 → android-37,同步改 source.properties 与 package.xml。"""
import shutil
from pathlib import Path

sdk = Path(r"C:\build-env\android\platforms")
src, dst = sdk / "android-37.0", sdk / "android-37"
if not src.is_dir():
    raise SystemExit("android-37.0 不存在,先按 3.2 安装")
if dst.exists():
    raise SystemExit("android-37 已存在,跳过")
shutil.copytree(src, dst)
# ① source.properties:ApiLevel 37.0 → 37
sp = dst / "source.properties"
sp.write_text(sp.read_text(encoding="utf-8").replace("AndroidVersion.ApiLevel=37.0",
                                                     "AndroidVersion.ApiLevel=37"),
              encoding="utf-8")
# ② package.xml(关键):localPackage path / api-level / display-name 三处 37.0 → 37
px = dst / "package.xml"
px.write_text(px.read_text(encoding="utf-8").replace("37.0", "37"), encoding="utf-8")
print("合成完成:", dst)
```

执行与验证:

```powershell
py -3 C:\build-env\fix-android37.py
. C:\build-env\env.ps1; & "C:\build-env\android\cmdline-tools\latest\bin\sdkmanager.bat" --list_installed
```

**验证标准**:`platforms;android-37` 与 `platforms;android-37.0` 同时列出,且**无** "Observed package id 'platforms;android-37.0' in inconsistent location" 警告。

## 4. Flutter 3.47.4 stable

```powershell
# 国内镜像直达(官网 https://docs.flutter.dev/release/archive 为准):
# https://storage.flutter-io.cn/flutter_infra_release/releases/stable/windows/flutter_windows_3.47.4-stable.zip
Expand-Archive ~\Downloads\flutter_windows_3.47.4-stable.zip -DestinationPath C:\build-env
# zip 内含顶层 flutter\ 目录,落位 C:\build-env\flutter
. C:\build-env\env.ps1   # 先注入镜像变量再首跑
flutter --version        # 首跑下载 Dart SDK(走 storage.flutter-io.cn)
flutter doctor
```

验证:`flutter --version` 显示 Flutter 3.47.4 stable;`flutter doctor` 无 Android toolchain 缺失项(android-37 合成生效后 SDK licenses 已接受)。

## 5. adb(C:\tools\scrcpy\adb.exe,机器级 PATH,SYSTEM 会话可见)

```powershell
# 方式一(推荐,含 scrcpy):GitHub https://github.com/Genymobile/scrcpy/releases 下载 scrcpy-win64-v*.zip
Expand-Archive ~\Downloads\scrcpy-win64-v*.zip -DestinationPath C:\tools\scrcpy
# 方式二(仅 adb):https://dl.google.com/android/repository/platform-tools-latest-windows.zip
#   解出后把 adb.exe(及依赖 dll)放进 C:\tools\scrcpy\
```

机器级 PATH 追加(**勿用 setx /M PATH**,有 1024 字符截断风险):

```powershell
$old = [Environment]::GetEnvironmentVariable("PATH", "Machine")
if ($old -notlike "*C:\tools\scrcpy*") {
  [Environment]::SetEnvironmentVariable("PATH", "$old;C:\tools\scrcpy", "Machine")
}
```

验证(新开 PowerShell,模拟 SYSTEM 可见性):

```powershell
adb version   # Android Debug Bridge version 1.x.x 来自 C:\tools\scrcpy\adb.exe
```

注:测试手机 USB 驱动(荣耀)见部署计划 §8 设备池;`adb devices` 出设备后该步才算闭环。

## 6. 终验清单(全部通过才算工具链就绪)

| 命令 | 期望 |
|---|---|
| `C:\build-env\jdk-17\bin\java.exe -version` | 17.0.20.1(或 17.0.2x) |
| `C:\build-env\jdk-21\bin\java.exe -version` | 21.x |
| `. C:\build-env\env.ps1; echo $env:FLUTTER_STORAGE_BASE_URL` | https://storage.flutter-io.cn |
| `sdkmanager --list_installed` | platform-tools、platforms 34/36/37.0/37.1/37.2/**37(合成)**、build-tools 34.0.0/36.0.0,无 inconsistent 警告 |
| `flutter --version` | Flutter 3.47.4 stable |
| `flutter doctor` | 无 ✗ 项(USB 插设备后 devices 项自动消) |
| `adb version` | C:\tools\scrcpy\adb.exe |
| `C:\build-env\env.ps1` 存在且五变量齐全 | — |

全部通过后回填部署计划 §10 验证清单第 5 步前置条件,并交由 jenkins-setup.md 继续 Jenkins 侧。
