# Jenkins 安装清单 v2(master 167 + agent 节点 176,Linux,2026-09-21)

> 用途:双机口径——**Jenkins master 装在 167 平台机**(apt LTS),**构建节点 build-176 挂 176 构建机**
> (launch method SSH);swan-audio-build 任务钉 176,产物登记跨机 HTTP 回 167。
> 前置:两机按部署计划 §3/§4 就位(autotest 用户、/opt/uiautotest 克隆、.venv 就绪);
> 176 工具链按 build-env.md 完成(JDK17 在 /opt/build-env/jdk-17,节点 JVM 用它)。
> 凭据纪律:**管理员密码/API token 只写 167:/opt/uiautotest/.env.local,不进命令行明文/日志/git**。

## 1. master(167):apt 装 Jenkins LTS(TUNA 镜像)

```bash
sudo apt-get install -y openjdk-17-jdk-headless   # Jenkins LTS 运行时(master 不需要固定路径,apt 版即可)
curl -fsSL https://mirrors.tuna.tsinghua.edu.cn/jenkins/debian-stable/jenkins.io-2023.key \
  | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://mirrors.tuna.tsinghua.edu.cn/jenkins/debian-stable binary/" \
  | sudo tee /etc/apt/sources.list.d/jenkins.list
sudo apt-get update && sudo apt-get install -y jenkins
```

注:apt 装完服务自动以 jenkins 用户起在 8080——若 8080 已被 dashboard 占用,服务起不来
属预期,直接做第 2 步改端口后 restart。

## 2. master(167):/etc/default/jenkins 端口与服务用户

编辑 `/etc/default/jenkins`,确认/修改两行(其余默认):

```ini
HTTP_PORT=8082
JENKINS_USER=autotest
```

8080 是 dashboard,必须让位;服务用户统一 autotest(两机同名,部署计划布局约定)。
改属主并重启:

```bash
sudo chown -R autotest:autotest /var/lib/jenkins /var/log/jenkins /var/cache/jenkins
sudo systemctl restart jenkins
systemctl status jenkins --no-pager          # active (running)
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8082/login   # 200(首次初始化约 30-60s)
```

JENKINS_HOME 保持 apt 默认 `/var/lib/jenkins`(不额外迁移)。

## 3. agent 节点(176):SSH 密钥与目录预置

在 **167** 以 autotest 生成 master→176 专用 keypair:

```bash
sudo -u autotest ssh-keygen -t ed25519 -f ~autotest/.ssh/jenkins_agent_key -N ""
sudo cat ~autotest/.ssh/jenkins_agent_key.pub      # 内容下一步用
```

在 **176** 把上面公钥追加进 `~autotest/.ssh/authorized_keys`(700/600 权限);
并预建 agent 工作目录:

```bash
sudo mkdir -p /opt/jenkins-agent && sudo chown autotest:autotest /opt/jenkins-agent
```

回到 **167** 预热 known_hosts(避免首次连接卡 host key 确认):

```bash
sudo -u autotest ssh -i ~autotest/.ssh/jenkins_agent_key -o StrictHostKeyChecking=accept-new \
  autotest@192.168.12.176 true
```

## 4. master(167):管理员初始化

1. 浏览器开 http://192.168.12.167:8082(ssh 隧道 `ssh -L 8082:127.0.0.1:8082 192.168.12.167` 亦可)
2. 解锁密码:`sudo cat /var/lib/jenkins/secrets/initialAdminPassword`
3. 向导选「安装推荐插件」或「跳过」均可——**最小集必须 git + SSH Build Agents**(节点 SSH
   启动方式依赖),离线/慢时跳过向导,装完用第 5 步镜像源补装
4. 创建管理员:用户名 `admin`,密码自定——**记入 167:/opt/uiautotest/.env.local 的
   JENKINS_ADMIN_PASSWORD(不进日志/git)**
5. 实例 URL 填 http://192.168.12.167:8082

## 5. master(167):插件最小集(git + SSH Build Agents,依赖自动解析)

镜像加速:Manage Jenkins → Plugins → Advanced settings → Update Site 改为
`https://mirrors.tuna.tsinghua.edu.cn/jenkins/updates/update-center.json` → Save → Check now。

Available plugins 安装 **Git plugin** 与 **SSH Build Agents**(ssh-slaves),依赖由 Jenkins
自动勾选解析。两份 job 均为 shell freestyle,不需要 pipeline/workflow 插件。

## 6. master(167):建节点 build-176

Manage Jenkins → Nodes → New Node:

| 项 | 值 |
|---|---|
| Node name | build-176 |
| Number of executors | 1(重型构建,不并发) |
| Remote root directory | /opt/jenkins-agent |
| Labels | build-176 |
| Usage | Only build jobs with label expressions matching this node |
| Launch method | Launch agent via SSH |
| Host | 192.168.12.176 |
| Credentials | Add → SSH Username with private key:用户名 `autotest`,私钥选
  **Enter directly** 粘贴 `~autotest/.ssh/jenkins_agent_key` 内容(第 3 步生成) |
| Host Key Verification Strategy | Known hosts file Verification Strategy |
| **JavaPath(Advanced)** | `/opt/build-env/jdk-17/bin/java` ——**必填**:176 的 java
  在 /opt/build-env 下,agent 非登录 shell 拿不到 profile.d 注入的 PATH,不指绝对路径起不来 |

保存后节点应转在线(日志见 agent.jar 拉取与启动)。API 断言:

```bash
token=$(grep '^JENKINS_API_TOKEN=' /opt/uiautotest/.env.local | cut -d= -f2-)
curl -s -u "admin:$token" "http://127.0.0.1:8082/computer/build-176/api/json?tree=offline"   # {"offline":false}
```

## 7. master(167):建两份 job(createItem)

swan-audio-build 用备料的 `tools/provision/job-swan-audio-build.xml`(已钉 assignedNode=build-176):

```bash
token=$(grep '^JENKINS_API_TOKEN=' /opt/uiautotest/.env.local | cut -d= -f2-)
curl -s -u "admin:$token" -X POST -H "Content-Type: application/xml" \
  --data-binary "@/opt/uiautotest/tools/provision/job-swan-audio-build.xml" \
  "http://127.0.0.1:8082/createItem?name=swan-audio-build"
# 回显为空即成功(HTTP 200);重名会 400
curl -s -o /dev/null -w '%{http_code}\n' -u "admin:$token" \
  "http://127.0.0.1:8082/job/swan-audio-build/config.xml"   # 200
```

swan-autotest 任务同法 createItem,定义文件由流水线执行模块备料(不在本清单内)。

## 8. 部署注意事项

- **176 会话依赖预检**(构建实际运行视角,任一缺失先补):`/opt/uiautotest/.env.local` 含
  GITLAB_BOT 两键与 DASHBOARD_URL=http://192.168.12.167:8080;`git` 在 PATH;`/opt/uiautotest/.venv/bin/python`
  存在。验证单见 jenkins-verify.md。
- **PEP 668**:Ubuntu 24.04 系统 pip 被锁,一切 Python 调用走 `/opt/uiautotest/.venv/bin/python`
  (job XML 已按此写死,不要改回 python3)。
- **批处理→bash 移植差异**(job XML v2):Windows 版 `%EXTRA%` 整行替换语义下 notes 加字面引号;
  bash 变量展开**不做引号解释**,字面引号会进 argv,故 bash 版 notes 不加引号——NOTES 是
  URL 编码串(无空格无 shell 元字符,坑 15 黑名单过滤),`$EXTRA` 未引号展开的单词拆分安全;
  手工触发绕过平台时 notes 同样必须传 URL 编码值。COMMIT 传值修复口径延续(EXTRA 累加拼接,
  档案 2026-09-21 拍板)。
- **NOTES 参数与坑 15 的衔接**:平台 POST /api/builds 已做 branch 白名单/commit hex/notes 命令
  字符黑名单校验;job 对参数不加信任假设,若绕过平台手工触发,同样遵守"参数最少化"
  (部署计划 §12:后续优化方向为脚本文件投递+参数最少化,本次重建顺带评估落地)。
- **8080 冲突**:master 端口必须是 8082(dashboard 8080/nightly 不可占用);`ss -tlnp | grep 8082` 预检。
- swan-autotest 参数与触发语义由流水线执行模块验证,不在本验证单范围。
