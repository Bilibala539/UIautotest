# 设备池恢复清单(.166 新机备料,2026-09-21)

> 用途:.166 重装后恢复设备池与执行 agent 的运行条件,不允许现场摸索。
> 前置:部署计划 §1-§4 完成(系统基线/SSH/Git 仓/Python 机器级依赖);
> dashboard 计划任务 TestHistoryDashboard 已起(8080 监听)。
> 设备事实:荣耀 JDY-AN00,serial **AKFDCP4718425500**;手机 app 登录态 13555555555
> 存在手机本地,不受 .166 重装影响;受保护账号 18946151218 **永远不碰、不登出**。
> E: 存活时 devices 表历史行直接复用;本清单按"表空了怎么重建"写,防全盘重装情形。

## 1. adb 落位与 SYSTEM 可见性

conftest 设备注册/领取(`qa_platform/device_pool.py`)以 `["adb","devices","-l"]` 裸命令调 adb,
**只认 PATH**。Jenkins 构建以 SYSTEM 跑,所以 adb 必须在**系统级** PATH(不是用户 PATH)。

1. `C:\tools\scrcpy\` 放 adb 三件套(`adb.exe` + `AdbWinApi.dll` + `AdbWinUsbApi.dll`,
   取自 scrcpy 发行包,不需要完整 scrcpy);把 `C:\tools\scrcpy` 加入系统 PATH。
2. admin 会话验证:`adb version` 有版本;`adb devices -l` 有输出(未接手机时表头正常即可)。

SYSTEM 会话验证(一次性计划任务回显法,验证完即删):

```powershell
schtasks /Create /TN PoolAdbCheck /RU SYSTEM /SC ONCE /ST 23:59 /F `
  /TR "cmd /c adb devices -l > E:\uiautotest\output\logs\adb_system_check.txt 2>&1"
schtasks /Run /TN PoolAdbCheck
Start-Sleep 3; Get-Content E:\uiautotest\output\logs\adb_system_check.txt
schtasks /Delete /TN PoolAdbCheck /F
```

**adb server 归属坑**:RSA 授权密钥由**先启动 adb server(5037 端口)的账户**持有
(`C:\Users\<账户>\.android\adbkey`)。若 SYSTEM 先起 server,手机会弹授权,必须到手机屏幕
点"一律允许";省事做法——先在 admin/RDP 会话跑一次 `adb devices` 完成授权,SYSTEM 之后作为
client 连接同一 server 即可看到设备。

## 2. 荣耀驱动与手机设置

- 驱动:Win10/11 一般自动装好(HDB Interface)。设备管理器有叹号、或 `adb devices`
  列表空/设备显示 unauthorized → 装 HiSuite(或荣耀官方 USB 驱动)后重插。
- 手机侧设置(重装后手机本身不用动,查一遍即可):
  1. 开发者选项:设置 → 关于手机 → 版本号连点 7 次解锁;
  2. **USB 调试**开;
  3. **"仅充电模式下允许 ADB 调试"开**(荣耀特有开关,必开,否则仅充电模式连不上);
  4. "充电时屏幕不休眠"(保持唤醒)开——无人值守 nightly 必需;
  5. 首次连接 RSA 弹窗:勾"一律允许"再确定;误拒后 手机端撤销 USB 调试授权 → 重插重来。
- `adb devices` 显示 offline → 换线/换口(建议主机后置 USB)/重启手机。
- 纪律:自动化登录态是 13555555555(OTP 白名单内测试账号);**任何登出/注销操作禁止**
  (手机上另有受保护的 18946151218,自动化永不触达)。

## 3. devices 表注册(表空重建 / E 盘存活时的核对)

**正常路径零手工**:conftest 每次会话开始自动调 `register_local_devices()` 把本机 adb
在线设备全部注册进平台池——首次冒烟即自愈,什么都不用做。

手动重建(全盘重装表空后,或想让平台页提前看到设备):POST `/api/devices/register`,
payload 与代码 `register_local_devices()` 逐键一致:

```powershell
# serial/model 取自 adb devices -l:第一列 serial;model: 字段去前缀
$serial = "AKFDCP4718425500"
$model  = "JDY-AN00"    # 以 adb devices -l 实际输出的 model: 为准
Invoke-RestMethod -Method Post -Uri "http://192.168.12.166:8080/api/devices/register" `
  -ContentType "application/json; charset=utf-8" `
  -Body (@{ device_id=$serial; name=$model; platform="flutter"; model=$model;
            metadata=@{ host=$env:COMPUTERNAME } } | ConvertTo-Json)
```

核对:`GET /api/devices` 返回 `{"items":[...]}`,该设备 `status=online_idle`、
`platform=flutter`、`metadata.host=1BG-IT-00060`(新机计算机名)。

幂等性(重复执行安全):offline → 复活为 online_idle 并清占用;busy/disabled 设备
状态与占用**原样不动**,不会误伤执行中任务。

数据口径:
- E: 存活 → 旧设备行还在,serial 相同直接复用,last_assigned_at 历史保留(公平分配延续);
- 全盘重装丢行 → 按上法重建,公平分配"最久未用优先"从头计时(单设备无感)。

## 4. 领取机制自检(acquire/release 往返)

conftest 启用设备池的四个条件(conftest.py:115-121,缺一即静默不启用):

```
PLATFORM ∈ {flutter, android}  且  DASHBOARD_URL 非空
且  DEVICE_POOL 不在 {0,false,off}  且  ANDROID_DEVICE_SERIAL 未设置
```

agent 执行链自动满足全部四个;手动跑 pytest 前先自查这四个环境变量。

API 往返演练(不跑 pytest,验证平台侧调度语义):

```powershell
$run = "pool-verify-{0:yyyyMMddHHmmss}" -f (Get-Date)
$d = Invoke-RestMethod -Method Post -Uri "http://192.168.12.166:8080/api/devices/acquire" `
  -ContentType "application/json; charset=utf-8" `
  -Body (@{ run_id=$run; platform="flutter"; prefer=@() } | ConvertTo-Json)
$d.device_id        # 期望返回 serial;平台页该设备转 busy(current_run=$run)
Invoke-RestMethod -Method Post -Uri "http://192.168.12.166:8080/api/devices/$($d.device_id)/release" `
  -ContentType "application/json; charset=utf-8" `
  -Body (@{ run_id=$run } | ConvertTo-Json)
# 再 GET /api/devices:回 online_idle,current_run 清空,last_assigned_at 已刷新
```

- acquire 返回 **503** = 无空闲设备(全部 busy/offline/disabled)→ conftest 里
  `pytest.exit(3)` → 任务判 env_blocked(环境问题按 bug 处理,不计用例失败)。
- 语义速记(重装后如有疑议以此为准):
  busy→idle 拒绝(占用保护);busy→offline/disabled 允许(拔线自愈/人工下线,清占用);
  busy 超 4h 且无 idle 可领时平台自愈回收;release 前 adb 复查,失联设备置 offline,
  重插后 register 复活。另有 running 任务 1h 超时兜底(RUNNING_TIMEOUT_HOURS,server 端),
  与设备 4h 自愈相互独立。

## 5. pipeline_agent 依赖清单(SYSTEM 视角)

| 依赖 | 要求 | 验证 |
|---|---|---|
| 代码仓 | E:\uiautotest(git 克隆,部署计划 §3) | 目录存在 |
| Python | 机器级 py -3(C:\Program Files\Python312);agent 本体零三方依赖(urllib) | `py -3 scripts\pipeline_agent.py --help` |
| 依赖包 | `py -3 -m pip install --ignore-installed -r requirements.txt`(admin 用户级安装 SYSTEM 看不到——老坑) | `py -3 -s -c "import pytest,cv2,paddleocr,yaml"`(-s 排除用户 site,等效 SYSTEM 视角) |
| .env.local | E:\uiautotest\.env.local(SWAN_PHONE=13555555555 等测试侧键;agent 自读) | 文件存在 |
| adb | 系统 PATH,SYSTEM 可见 | 本文 §1 |
| 日志目录 | output\logs 可写(agent 把 pytest 输出重定向到 output\logs\pipeline_pipe-<job_id>.log,无控制台场景必须落文件) | 冒烟后文件生成 |
| pytest cache | 仓根 .pytest_cache 可写(--lf 失败重跑依赖) | 冒烟后目录生成 |
| PaddleOCR 模型 | 模型缓存按用户目录隔离;SYSTEM 首跑会现下载(慢非卡)。可先 admin 预热,再以 SYSTEM 跑一次确认 | 冒烟日志无下载超时 |

**.166 不放常驻 PipelineAgent 计划任务**:Jenkins 定向通道(--job-id)是 .166 的执行方式;
轮询兜底 agent(PipelineAgent,`pythonw --loop 60`)在 1BG-IT-01796 本机,不随 .166 重装
受影响。若主会话想把兜底也挪到 .166,另行拍板,默认不放。

触发通道(同链路,主会话二选一,不属设备池):
A. 旧通道——计划任务 NightlyPipelineTrigger(每日 01:33)调
   `py -3 E:\uiautotest\scripts\nightly_trigger.py --legacy-trigger`
   (**注意必须带 --legacy-trigger**:新版脚本缺省动作已改为 bootstrap 建配置,不是直触发);
B. M5 调度器——`nightly_trigger.py`(无参)bootstrap 建套件+配置 → 白天 `--run-now` 验证 →
   `--enable` 切换 + 常驻 `pipeline_scheduler.py`。是否切换、切换时机由主会话按该脚本文档头
   的步骤拍板。
