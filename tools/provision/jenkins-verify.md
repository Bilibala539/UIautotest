# Jenkins 装后验证单(.166 新机备料,2026-09-21)

> 用途:jenkins-setup.md 完成后逐项打勾;全部通过才允许触发真构建。
> 凭据纪律:**新管理员密码/API token 只写 E:\uiautotest\.env.local,不进命令行明文/日志/git**。

## 1. API Token 生成

UI 路线:Manage Jenkins → Users → admin → Security → API Token → Add new Token(名称如 `platform-call`)→ Generate → **立即复制**(仅显示一次)。

curl 路线(等价):

```powershell
# 用管理员登录密码(需先取 crumb;2.5xx crumb 会话绑定,同会话内用)
# 推荐 UI 生成,免去 crumb 往返
```

写入 .env.local(编辑 E:\uiautotest\.env.local,更新以下键):

```ini
JENKINS_ADMIN_PASSWORD=<新管理员密码>
JENKINS_USER=admin
JENKINS_API_TOKEN=<新 token>
JENKINS_BASE_URL=http://127.0.0.1:8082
JENKINS_PUBLIC_URL=http://192.168.12.166:8082
```

## 2. 基础验证(token 冒烟)

```powershell
# 新开 PowerShell(API token basic auth 免 crumb)
$env:JK = "admin:<API_TOKEN>"   # 临时变量,别落历史之外的地方;或从 .env.local 读
$h = @{ Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($env:JK)) }
(Invoke-WebRequest -UseBasicParsing -Headers $h "http://127.0.0.1:8082/api/json").StatusCode          # 200
(Invoke-RestMethod -Headers $h "http://127.0.0.1:8082/pluginManager/api/json?tree=plugins[shortName]").plugins.shortName -contains "git"   # True
```

计划任务与端口:

```powershell
schtasks /Query /TN JenkinsLTS                       # Ready/Running
netstat -ano | findstr :8082                          # LISTENING(SYSTEM 进程)
```

## 3. 任务与参数核对(不触发构建)

```powershell
(Invoke-RestMethod -Headers $h "http://127.0.0.1:8082/job/swan-audio-build/api/json?tree=property[parameterDefinitions[name,defaultParameterValue[value]]]").property[0].parameterDefinitions | Format-Table name, defaultParameterValue
```

**期望 4 个参数且与平台参数字典键完全一致**(server.py /api/builds 拼装侧:BRANCH/SERVER_TYPE/COMMIT/NOTES):

| name | defaultValue |
|---|---|
| BRANCH | dev |
| SERVER_TYPE | test |
| COMMIT | (空) |
| NOTES | (空) |

SYSTEM 会话依赖预检(批处理运行环境,任一缺失先补):

```powershell
py -3 --version                          # 机器级 Python 3.12
py -3 -s -c "import pytest, yaml"        # -s 排除用户 site,等效 SYSTEM 视角(教训见打包构建档案)
git --version                            # 机器级 PATH
Test-Path E:\uiautotest\.env.local       # True;且含 GITLAB_BOT_USER/GITLAB_BOT_PASSWORD
```

## 4. 触发 dry-run(两档)

**档一:环境自检(推荐先做,不真打包)**——手工 Build with Parameters 触发一次 `BRANCH=dev & SERVER_TYPE=test`,盯控制台:
- 检出行出现 `checkout branch dev` + commit 号 → git/凭据 OK;
- `flutter build apk --profile` 命令行出现且**没有** "No Android SDK found"/"Failed to find target with hash string" → env 注入与 android-37 合成 OK;
- 看到以上两关即可 **Abort**(不浪费 5-14 分钟完整构建;残留半删除源码无碍——build_swan_apk 的 git 自证(坑 14)下次自动重建)。

**档二:完整链路(部署计划 §10.5)**——正常触发 `dev/test` 跑完:
1. 构建结果 SUCCESS(总耗时约 5-14 分钟,首跑含 pub get 更久);
2. `GET http://192.168.12.166:8080/api/apks?limit=5` 出现新行,`source=auto-build`、`flavor=profile`、`server_type=test`、`jenkins_job=swan-audio-build`、`jenkins_build=<构建号>`;
3. 包管理页新行可下载,「Jenkins 日志」按钮跳 http://192.168.12.166:8082/job/swan-audio-build/<构建号>/ 正常;
4. 平台页触发入口(POST /api/builds)同样成功——顺带验证注入封堵(坑 15)在新机生效(部署计划 §11)。

## 5. 常见失败对照

| 现象 | 根因方向 |
|---|---|
| 控制台 "No Android SDK found" | build_env env 未生效(脚本已自带 env 注入;若复现检查 C:\build-env\android 是否按 build-env.md 落位) |
| "Failed to find target with hash string 'android-37'" | android-37 未合成或 package.xml 未同步改(档案坑 12) |
| git 401/404 | .env.local GITLAB_BOT 两键缺失/错;日志 URL 应为脱敏形态(git.hivi.com/... 无凭据) |
| ModuleNotFoundError(py) | 依赖落了 admin 用户 site;按部署计划 §4 用 --ignore-installed 重装 |
| 任务参数与上表不符 | config.xml 版本不对;重新 createItem 前先删旧任务 |
| 8082 起不来 | 端口占用/Java 路径错;看 run-jenkins.cmd 直跑输出 |
