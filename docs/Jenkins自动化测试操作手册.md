# Android UIAutotest 自动化测试 — 操作手册

## 1. 前置条件

### Jenkins Agent 启动

每次开机后需要手动启动 Jenkins Agent，使本机与 Jenkins 服务器保持连接。

**方式**：双击桌面快捷方式 **「Jenkins Agent」**

**确认连接**：打开 [http://10.220.28.153:8080/computer/Android-UIAutoTest/](http://10.220.28.153:8080/computer/Android-UIAutoTest/)，页面显示 **In sync** 即为连接成功。

> Agent 窗口必须保持打开状态，关闭窗口 = 断开连接 = 定时任务无法执行。

---

## 2. Jenkins Job

**Job 地址**：[http://10.220.28.153:8080/job/Android-UIAutotest-Checklist/](http://10.220.28.153:8080/job/Android-UIAutotest-Checklist/)

### 2.1 参数说明

| 参数 | 可选值 | 默认值 | 说明 |
|---|---|---|---|
| **EXECUTION_MODE** | 并行 / 串行 | 并行 | 并行 = 多台 MuMu 同时跑；串行 = 单台顺序跑 |
| **N_INSTANCES** | 1 / 2 / 3 / 4 | 4 | 并行实例数（串行时忽略）。⚠️ **建议设为 2~3，不要用 4**：4 实例会吃满 CPU 导致 ADB 截图超时大量 Error。想提升并行数需升级 CPU |
| **REINSTALL** | 是 / 否 | 是 | 是否重启 MuMu 并重装 POPO 客户端 |
| **BRANCH** | `latest_online` / 分支名 | `latest_online` | REINSTALL=是时生效；`latest_online` = 自动取正式服最新包 |
| **RUN_TESTS** | 是 / 否 | 是 | 是否执行 checklist 用例 |
| **TEST_DIR** | 目录或文件路径 | `tests/checklist` | RUN_TESTS=是时生效 |

### 2.2 常用组合

| 场景 | REINSTALL | BRANCH | RUN_TESTS |
|---|---|---|---|
| 正常夜间跑（自动拉最新包） | 是 | latest_online | 是 |
| 指定版本跑 | 是 | release_4.23.5 | 是 |
| 只重装不跑（验证安装） | 是 | latest_online | 否 |
| 不重装直接跑（快速验证） | 否 | 任意 | 是 |

### 2.3 手动触发

1. 打开 Job 页面 → 点击 **「Build with Parameters」**
2. 按需修改参数 → 点击 **「Build」**

---

## 3. 定时自动执行

**触发时间**：每天 **00:20**（自动使用默认参数）

**默认行为**：并行 4 台 → 重装正式服最新包 → 跑全量 checklist

### 跳过某天不跑

在 Job 页面点击 **「Disable Project」** 即可暂停定时任务，不影响 Job 配置和历史记录。恢复点 **「Enable」**。

---

## 4. 查看结果

### 4.1 POPO 群通知

跑完后自动发送到群 **3220461**，包含通过率和详情链接。

### 4.2 历史平台

**地址**：[http://10.220.28.125/reports/allure-report/history.html#](http://10.220.28.125/reports/allure-report/history.html#)

- 可查每次 session 的通过/失败/error 详情
- 失败用例有对应日志（仅失败用例，通过的不上传）

### 4.3 Jenkins 构建日志

Job 页面 → 点击构建编号 → **「Console Output」**，可查看实时执行输出。

---

## 5. 预计耗时参考

| 阶段 | 耗时 |
|---|---|
| MuMu 重启 + ADB 就绪 | ~3 分钟 |
| 下载 + 安装 APK（4台） | ~10 分钟 |
| 测试执行（4 台并行，136 个文件） | ~60 分钟 |
| 上传历史平台 + 发群 | ~2 分钟 |
| **总计** | **~75 分钟** |

---

## 6. 常见问题

### Agent 断开 / Job 无法执行

1. 检查 Agent 窗口是否还在，关闭了就双击桌面快捷方式重启
2. 打开 [http://10.220.28.153:8080/computer/Android-UIAutoTest/](http://10.220.28.153:8080/computer/Android-UIAutoTest/) 确认在线

### 实例 #3 APK 安装失败

偶现问题，安装 ADB 超时导致。触发方式：点「Build with Parameters」→ REINSTALL=是 → 重新触发即可。

### 通过率突然大幅下降

优先检查：
1. 是否刚发了新版本，某些图片元素有 UI 变化
2. 看失败日志里的截图，确认是图片匹配问题还是业务逻辑问题

### MuMu 窗口全黑 / 没有响应

重新触发一次 Job（REINSTALL=是），让框架重启 MuMu 并重装，通常可恢复。

---

## 7. 关键地址速查

| 资源 | 地址 |
|---|---|
| Jenkins | http://10.220.28.153:8080 |
| Job | http://10.220.28.153:8080/job/Android-UIAutotest-Checklist/ |
| Jenkins Agent 状态 | http://10.220.28.153:8080/computer/Android-UIAutoTest/ |
| 历史平台 | http://10.220.28.125/reports/allure-report/ |
| 包体下载平台 | http://10.220.28.152:8081/#/androidshow正式服 |
