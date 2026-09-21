# Jenkins LTS 安装清单(.166 新机备料,2026-09-21)

> 用途:.166 重装后重建 Jenkins(旧 JENKINS_HOME 随 C: 丢失,全部重建)。
> 前置:build-env.md 已完成(jdk-17 就位);E:\uiautotest 仓已克隆;Python 3.12 机器级依赖已装(部署计划 §4)。
> 执行身份:admin PowerShell;每步验证后再下一步。端口 8082(与 .env.local 的 JENKINS_BASE_URL=http://127.0.0.1:8082 约定一致)。

## 1. jenkins.war 下载与落位

```powershell
# LTS war,TUNA 镜像(官网 https://www.jenkins.io/download/changelog-stable/ 选当前 LTS 版本号代入):
# https://mirrors.tuna.tsinghua.edu.cn/jenkins/war-stable/<版本号>/jenkins.war
# 示例:https://mirrors.tuna.tsinghua.edu.cn/jenkins/war-stable/2.504.3/jenkins.war
Move-Item ~\Downloads\jenkins.war C:\build-env\jenkins\jenkins.war
```

## 2. 启动脚本(携带 JENKINS_HOME,计划任务直接调它)

创建 `C:\build-env\jenkins\run-jenkins.cmd`,全文如下:

```bat
@echo off
rem Jenkins LTS 启动(SYSTEM 会话执行;JENKINS_HOME 必须在此显式 set,
rem schtasks /TR 无法传环境变量;JDK 用绝对路径避免依赖机器 PATH)
set JENKINS_HOME=C:\build-env\jenkins\home
"C:\build-env\jdk-17\bin\java.exe" -Djava.awt.headless=true -jar C:\build-env\jenkins\jenkins.war --httpPort=8082
```

## 3. 计划任务 JenkinsLTS(SYSTEM)

```powershell
schtasks /Create /TN JenkinsLTS /RU SYSTEM /SC ONSTART /TR "C:\build-env\jenkins\run-jenkins.cmd" /F
schtasks /Run /TN JenkinsLTS
```

验证(首次启动要初始化,日志看进度):

```powershell
schtasks /Query /TN JenkinsLTS
Get-Content C:\build-env\jenkins\home\logs\*.log -ErrorAction SilentlyContinue
# 更直接:等 30-60s 后
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8082/login).StatusCode   # 200
```

## 4. 管理员初始化

1. 浏览器开 http://127.0.0.1:8082(RDP 到 .166 操作,或临时端口转发)
2. 解锁密码:`Get-Content C:\build-env\jenkins\home\secrets\initialAdminPassword`
3. 选「安装推荐插件」或「选择插件」均可——但**最小集只必须 git**(批处理 freestyle 不需要 pipeline);离线/慢时可跳过向导插件步骤,装完用步骤 5 的镜像源补装
4. 创建管理员:用户名 `admin`,密码自定——**记入 E:\uiautotest\.env.local 的 JENKINS_ADMIN_PASSWORD(不进日志/git)**
5. 实例 URL 填 http://192.168.12.166:8082

## 5. 插件最小集(git + 依赖自动解析)

镜像加速:Manage Jenkins → Plugins → Advanced → Update Site 改为
`https://mirrors.tuna.tsinghua.edu.cn/jenkins/updates/update-center.json` → Save → Check now。

然后 Available plugins 搜索安装 **Git plugin**(依赖由 Jenkins 自动勾选解析)。批处理 freestyle job 不需要 pipeline/workflow 插件。

验证:

```powershell
$cred = "admin:<API_TOKEN>"   # token 见 jenkins-verify.md 步骤 1
(Invoke-RestMethod -UseBasicParsing -Headers @{Authorization="Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($cred)))"} `
  "http://127.0.0.1:8082/pluginManager/api/json?tree=plugins[shortName]").plugins.shortName -contains "git"   # True
```

## 6. 建 swan-audio-build 任务

用备料的 job 定义仓库文件 `tools/provision/job-swan-audio-build.xml`:

```powershell
# API token 走 basic auth 免 crumb(旧机实测;密码 basic auth 需 crumb)
$token = (Get-Content E:\uiautotest\.env.local | Where-Object { $_ -like "JENKINS_API_TOKEN=*" }) -replace "^JENKINS_API_TOKEN=", ""
curl.exe -s -u "admin:$token" -X POST -H "Content-Type: application/xml" `
  --data-binary "@E:\uiautotest\tools\provision\job-swan-audio-build.xml" `
  "http://127.0.0.1:8082/createItem?name=swan-audio-build"
# 回显为空即成功(HTTP 200);重名会 400
(Invoke-WebRequest -UseBasicParsing -Headers @{Authorization="Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:$token")))"} `
  "http://127.0.0.1:8082/job/swan-audio-build/config.xml").StatusCode   # 200
```

swan-autotest 任务由流水线模块备料(同法 createItem),不在本清单内。

## 7. 部署注意事项

- **SYSTEM 会话预检**:计划任务以 SYSTEM 跑,批处理依赖 ① `py -3`(机器级 Python,部署计划 §4)② `git`(机器级 PATH,Git for Windows 安装器默认)③ `E:\uiautotest\.env.local`(GITLAB_BOT 两键)。三者缺一,构建直接失败——验证单见 jenkins-verify.md。
- **端口冲突预检**:`netstat -ano | findstr :8082` 应为空(8080 平台/8081 mesh/18080 otp-gateway 不可占用)。
- **NOTES 参数与坑 15 的衔接**:平台 POST /api/builds 已做 branch 白名单/commit hex/notes 命令字符黑名单校验,job 批处理收到的是净化后的参数;但 job 本身对参数不加信任假设,若日后绕过平台手工触发,同样要遵守"参数最少化"(部署计划 §12:后续优化方向为脚本文件投递+参数最少化)。
- **批处理 COMMIT 修复已采纳(2026-09-21 主会话拍板)**:计划文档 §6 逐字还原版 `set EXTRA= --commit` 丢 commit 值——仅传 COMMIT(不传 NOTES)时 argparse 报 "expected one argument" 退出 2;COMMIT 与 NOTES 同传时 COMMIT 被覆盖丢失(静默按分支最新构建)。job-swan-audio-build.xml 已按修复版落位:第 3、4 行均改 `%EXTRA%` 前缀累加拼接(`if not "%COMMIT%" == "" set EXTRA=%EXTRA% --commit %COMMIT%`),XML 内注释标注与还原版的差异;部署计划 §6 已同步为修复版。安全性依据:COMMIT 经平台注入封堵(坑 15)后必为 1-40 位十六进制,批处理插值无注入面;NOTES 经黑名单过滤禁 `& | < > ^ " %`。
