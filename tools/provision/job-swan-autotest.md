# swan-autotest Jenkins 任务定义(.166 新机备料,2026-09-21)

> 用途:.166 重装后重建 Jenkins 测试执行任务 swan-autotest(旧 JENKINS_HOME 随 C: 丢失)。
> 前置:jenkins-setup.md 步骤 1-5 完成(Jenkins 起、admin/token 就绪、git 插件装好);
> jenkins-verify.md 步骤 1 完成(.env.local 的 JENKINS_* 四键已更新)。
> 本定义按平台触发侧代码契约重建(dashboard/jenkins_client.py + server.py try_jenkins_dispatch),
> 与旧机手工配置在行为上等价,不逐字节还原。
> 任务结果以平台 pipeline_jobs/runs 为准,构建号只是派发回执。

## 1. 触发契约(平台发什么,逐键对齐)

| 项 | 值 | 出处 |
|---|---|---|
| 目标 job 名 | `swan-autotest`(平台 env `JENKINS_TEST_JOB` 可覆盖,**严禁配成打包 job**——防环) | server.py:137 |
| 请求 | `POST {JENKINS_BASE_URL}/job/swan-autotest/buildWithParameters` | jenkins_client.py trigger() |
| 编码 | form 表单(`application/x-www-form-urlencoded; charset=utf-8`) | 同上 |
| 参数 | **仅 `JOB_ID` 一个键**,值 = pipeline_jobs.job_id 原值 | server.py:141 |
| 鉴权 | Basic(`JENKINS_USER:JENKINS_API_TOKEN`,API token 免 crumb) | jenkins_client.py _auth_header |
| 成功判据 | HTTP 201 + 响应头 `Location: .../queue/item/<id>/` | trigger() |
| 派发后 | 平台轮询队列 3 次 x 1s 取 build 号,回填任务行 `jenkins_job`/`jenkins_build` | server.py try_jenkins_dispatch |
| 失败行为 | 201 前任何失败 → 任务留 pending(result_json.jenkins_trigger_failed),本地 PipelineAgent(1BG-IT-01796)轮询兜底 | server.py:135 |
| 已知残留风险 | 201 之后平台进程崩溃 → 任务永远 pending(轮询通道按设计跳过 Jenkins 派发的任务),需人工重触发 | 流水线执行档案 规则14 |

因此本任务必须满足:**参数化,且唯一参数名为 `JOB_ID`**;构建体只做定向认领执行,不回调任何触发。

> 为什么 JOB_ID 必须显式定义:平台只传 JOB_ID。若 job 未参数化,`%JOB_ID%` 展开为空,
> agent `--job-id ""` 会退回轮询分支,误领任意 pending 任务——契约被静默破坏。

## 2. 环境变量契约

构建步骤**不需要手工 set 任何环境变量**:

- agent 启动即自读 `E:\uiautotest\.env.local`(_load_dotenv_local,已存在的外层环境变量优先):
  SWAN_PHONE(测试侧)、JENKINS_*(平台侧)、GITLAB_BOT 等;
- pytest 子进程环境由 agent 统一注入:PLATFORM / DASHBOARD_URL / DASHBOARD_RUN_ID /
  PREFLIGHT=1 / EVIDENCE=1 / DEVICE_POOL=1 / SWAN_APK_ID(任务指定包体时);
- DASHBOARD_URL 缺省 `http://192.168.12.166:8080`,在新机本机跑同样正确,无需设置。
  (可选优化:job 级 env 设 `DASHBOARD_URL=http://127.0.0.1:8080` 走本机回环,非必需。)

SYSTEM 会话三件套(py -3 / git / .env.local)核对见 jenkins-setup.md §7;adb 可见性见 device-pool.md。

## 3. 建任务(createItem)

任务定义仓库文件:`tools/provision/job-swan-autotest.xml`。

```powershell
$token = (Get-Content E:\uiautotest\.env.local | Where-Object { $_ -like "JENKINS_API_TOKEN=*" }) -replace "^JENKINS_API_TOKEN=", ""
curl.exe -s -u "admin:$token" -X POST -H "Content-Type: application/xml" `
  --data-binary "@E:\uiautotest\tools\provision\job-swan-autotest.xml" `
  "http://127.0.0.1:8082/createItem?name=swan-autotest"
# 回显为空即成功(HTTP 200);重名会 400
(Invoke-WebRequest -UseBasicParsing -Headers @{Authorization="Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:$token")))"} `
  "http://127.0.0.1:8082/job/swan-autotest/api/json").StatusCode   # 200
```

与 swan-audio-build 的差异:
- `JOB_ID` 一个字符串参数(默认空);
- **执行并发构建 = 允许**(concurrentBuild=true),多个冒烟触发可并行入构建;
- 无 SCM(NullSCM),批处理 `cd /d E:\uiautotest` 落仓根,依赖该目录的 .env.local 与 scripts。

并发说明:单手机环境下两个构建并行时,后到的 pytest 会因设备池无空闲走 env_blocked
(环境问题按 bug 处理,不计用例失败)。若不接受这种噪音,把 concurrentBuild 改为 false
让构建在 Jenkins 排队串行——由主会话拍板,默认按 M3 契约允许并发。

## 4. 任务自检(不占设备、不产生任务/run)

Build with Parameters 手工触发,`JOB_ID` 填不存在的值(如 `selftest-20260921`):

- 期望:构建**绿**,控制台出现
  `[pipeline-agent ...] job selftest-20260921 不可认领(不存在/已被认领/非 pending),按空跑退出`;
- 不产生任何 pipeline_jobs 行、不跑 pytest、不碰 adb。

构建红常见原因:① `py -3` 不存在 → 部署计划 §4 未完成;② ModuleNotFoundError → 机器级依赖
漏装(pip 落到用户 site 的老坑,重装一律 `--ignore-installed`);③ 仓路径不对(**E:\uiautotest**,小写 to)。

## 5. 防环三闸门(重建后逐条确认)

1. 平台 `.env.local` 的 `JENKINS_TEST_JOB` 只允许指测试 job(缺省即 swan-autotest,不设也对;
   **绝不能设成 swan-audio-build**);
2. 本构建体只跑 `pipeline_agent --job-id`,不回调 trigger / trigger_smoke(防环由结构保证);
3. 打包→冒烟联动(M5)若启用:swan-audio-build 批处理在打包成功后调
   `py -3 scripts\trigger_smoke.py --suite SMKE --apk-id <apk_id> || echo [WARN] smoke trigger failed`
   (失败只告警不影响构建结果)。该改造属 swan-audio-build job(打包模块所有,其备料 xml
   当前未含此行),是否加上由主会话拍板;联动语义见 scripts/trigger_smoke.py 文档头与
   流水线执行档案规则 16。

## 6. 平台侧收尾核对

- TestHistoryDashboard 计划任务就位后,`GET /api/apks` 能返回历史数据(E: 库存活被读到);
- 用一条真实任务实测派发链路:见 pipeline-verify.md 第 5-6 步;
- 任务行能看到 jenkins_build 号,页面 Jenkins 日志按钮可跳转(JENKINS_PUBLIC_URL 生效)。
