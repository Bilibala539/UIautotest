# BUG 报告：SWAN-BUG-20260910-001

- 任务：`SWAN-20260910-001-feature-boundary`（B 线片 2，U6 复核单元）
- 分类：`crash`（致命候选，未定级未提单）
- 模块：`com.swan.network` 登录页 / 第三方登录（微博）
- 基线：App `dev@4d1ed7b` / Core `dev@402853a`；APK v5.3.0（versionCode 32，2026-09-04 安装）
- 现象：登录页点击微博第三方登录按钮，进程立即崩溃退桌面。崩溃链：`SwanThirdPartyLoginPlugin.startWeiboAuthorization:119 → UMShareAPI → 新浪微博 SDK WeiboSsoSdk 类初始化 → System.loadLibrary`，`UnsatisfiedLinkError: dlopen failed: library "libwind.so" not found`。库缺失类，疑似 100% 复现。
- 对照组：微信按钮不崩（未装微信仅行内报错"未安装微信客户端"）——缺陷限于微博 SDK 链路。
- 勘误：片 1 记录的 O-5"微博按钮无响应"实为首次崩溃瞬间，已撤销并并入本条。
- 证据：`results\SWAN-20260910-001-feature-boundary\executor\evidence\crash-weibo-fatal-stack.txt`（完整栈）+ dropbox `data_app_crash` 归档 + `states-matrix.md` §12（U6 轻量复核单元）
- 结论：证据齐备的致命候选。待 qa-reporter 定级、主对话复核后方可经禅道提单。
- 后续：①修复验证需出包含原生库的新包；②逆向用例从应加"第三方 SDK 库缺失容错"维度（见模式库 P-004）。
