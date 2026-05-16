# UIAutotest Agent Teams 配置包 — 安装指南

这个压缩包是 **UIAutotest 项目的 6 人长期 AI 团队**完整配置。给另一台电脑使用时，按下面步骤操作即可还原一致的 agent teams 行为。

---

## 一、包内容

| 路径 | 数量 | 作用 |
|---|---|---|
| `CLAUDE.md` | 1 | 项目顶层硬性规则（所有 agent 必读） |
| `.claude/agents/*.md` | 6 | 6 个 agent 角色蓝图（aw-orchestrator / aw-explorer / aw-element / aw-codegen / aw-verify / spec-keeper） |
| `.claude/commands/*.md` | 2 | 自定义命令 `/bootstrap-team` 和 `/verify-team` |
| `.claude/README.md` | 1 | 团队接入指南（人 + AI 都看） |
| `.codemaker/rules/*.mdc` | 3 | 项目硬性规则集（rules / ai_workflow / aw_architecture） |
| `.codemaker/skills/**/SKILL.md` | 8 | 4 个 mobile skill + 4 个 pc skill 的详细操作手册 |
| `.codemaker/readme.md` | 1 | `.codemaker/` 目录说明 |
| `docs/AW方法总结与复用指南.md` | 1 | AW 复用清单（agent 强制前置阅读） |
| `docs/UI元素截取与裁剪规范.md` | 1 | 截图规范（agent 强制前置阅读） |
| `openspec/config.yaml` | 1 | openspec 配置 |
| `openspec/changes/agent-team/` | 4 | 当前未归档的 change 提案（proposal/design/tasks/.openspec.yaml） |

总计 **29 个配置文件 + 本 SETUP.md**。

---

## 二、前置要求（在新电脑上必须先具备）

### 1. UIAutotest 工程代码已存在

这套 agent teams 配置**依赖**项目业务代码（`utils/aw/`、`tests/mumu/`、`image/`、`conftest.py`、`explorer_output/knowledge/` 等）。如果新电脑上还没有 UIAutotest 工程：

```bash
git clone <UIAutotest 仓库地址> E:\UIAutotest    # 或任意路径
```

agent 蓝图里所有"强制前置阅读"清单都引用了这些工程内文件，否则 agent 启动后会报"文件不存在"。

### 2. Claude Code CLI 已安装并登录

```bash
# Windows
winget install -e --id Anthropic.ClaudeCode --accept-source-agreements --accept-package-agreements

# 或下载二进制：https://claude.com/claude-code

# macOS / Linux
curl -fsSL https://claude.com/install.sh | sh

# 登录（任选一种）
claude  # 首次启动按提示走 Anthropic 账号登录
# 或者
export ANTHROPIC_API_KEY=sk-ant-...
```

要求：`claude --version` ≥ 2.0.0

### 3. **必须**开启 agent teams 实验功能

在 `~/.claude/settings.json` 的 `env` 段加：

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

加完**重启 Claude Code**，否则 `TeamCreate` / `/bootstrap-team` 会报 "experimental"。

---

## 三、安装步骤（拷给新电脑上的 AI 看）

### 给 AI 助手的指令

> 你拿到了一个名为 `agent-teams-config.zip` 的压缩包。请按以下步骤把它解压并装配到本机的 UIAutotest 工程上。

#### Step 1：定位 UIAutotest 工程根目录

询问用户工程根目录绝对路径（如 `E:\UIAutotest` 或 `/Users/xx/UIAutotest`）。如果没有，提示用户先 clone。

#### Step 2：解压到工程根目录

把压缩包内**所有文件**按相对路径解压到工程根目录。压缩包内的相对路径已经按工程结构组织好，直接覆盖式解压即可。

```bash
# Windows PowerShell
Expand-Archive -Path "agent-teams-config.zip" -DestinationPath "E:\UIAutotest" -Force

# Bash
unzip -o agent-teams-config.zip -d /path/to/UIAutotest
```

#### Step 3：处理冲突

如果工程里已存在同名文件（比如 `CLAUDE.md`、`docs/AW方法总结与复用指南.md` 已被项目维护），询问用户：

- **覆盖**（推荐）：用包内版本覆盖。这套配置是协同维护的，应该保持各机器一致
- **保留**：跳过冲突文件，但要警告用户可能导致 agent 行为不一致

如果工程里 `.claude/agents/`、`.codemaker/rules/`、`.codemaker/skills/` 不存在，直接创建并写入。

#### Step 4：核对前置依赖

读取 `.claude/agents/aw-explorer.md`（或任意一个 agent 蓝图）末尾的"强制前置阅读"清单，逐项检查工程内文件是否存在。常见的前置依赖：

- `utils/aw/aw_base.py`
- `utils/aw/business/mumu.py`
- `utils/user.py`
- `conftest.py`
- `explorer_output/knowledge/app_map.json`（如果不存在，告诉用户：知识库可能在另一个分支或被 .gitignore 忽略，需要单独同步）
- `image/image_name_mapping.py`

如果有缺失，在最终报告里列出，让用户决定怎么补齐。

#### Step 5：开启 agent teams 实验功能

检查 `~/.claude/settings.json` 是否包含：

```json
"env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" }
```

没有就加上，告诉用户**重启 Claude Code 后才生效**。

#### Step 6：验证

让用户在工程根目录启动 Claude Code：

```bash
cd E:\UIAutotest      # 或对应路径
claude
```

然后在 Claude Code 里输入：

```
/bootstrap-team
```

期望结果：

- 创建团队 `uiautotest-team`
- 派出 5 个下游 teammate（explorer / element / codegen / verify / spec-keeper）
- 每个 teammate 自我汇报"我已就绪，职责是 XX"
- 主会话作为 orchestrator 给团队发开工令牌

如果 `/bootstrap-team` 报 "team already exists"，说明上次 session 留了同名团队，让用户先 `TeamDelete` 再重跑。

#### Step 7（可选）：装配自检

```
/verify-team
```

会对每个 agent 做 smoke test（读蓝图必读文件 + 回答职责三问），5~10 分钟跑完。

---

## 四、常见问题

| 现象 | 原因 | 解决 |
|---|---|---|
| `/bootstrap-team` 报 "TeamCreate not available" | 没开 experimental | 加 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 后重启 |
| agent 抱怨"找不到 docs/AW方法总结与复用指南.md" | 工程目录错了 / 没启动在工程根目录 | 必须 `cd` 到工程根目录后再启 `claude` |
| agent 抱怨"找不到 utils/aw/business/mumu.py" | UIAutotest 业务代码缺失 | 单独 clone 业务代码到工程根 |
| agent 抱怨"app_map.json 太大读不完" | 正常 | agent 会自己用 offset/limit 分段读，不阻塞 |
| 团队里某个 teammate 报"没有 TaskList / SendMessage 工具" | `subagent_type` 选错了 | `subagent_type` 必须用本工程的角色名（`aw-explorer` / `aw-element` 等） |

---

## 五、版本与维护

- 配置版本：与压缩包生成时的 git 工作树一致
- 适配 Claude Code：2.0+
- 团队结构：6-agent（orchestrator + 4 aw + 1 spec-keeper）
- 维护方式：源仓库内的 `.claude/`、`.codemaker/`、`CLAUDE.md` 是 source of truth，修改后请重新打包分发

---

## 六、附：文件清单（供新电脑 AI 校验）

包内文件路径（相对工程根）一览：

```
CLAUDE.md
.claude/README.md
.claude/agents/aw-codegen.md
.claude/agents/aw-element.md
.claude/agents/aw-explorer.md
.claude/agents/aw-orchestrator.md
.claude/agents/aw-verify.md
.claude/agents/spec-keeper.md
.claude/commands/bootstrap-team.md
.claude/commands/verify-team.md
.codemaker/readme.md
.codemaker/rules/ai_workflow.mdc
.codemaker/rules/aw_architecture.mdc
.codemaker/rules/rules.mdc
.codemaker/skills/aw-codegen/SKILL.md
.codemaker/skills/aw-codegen-pc/SKILL.md
.codemaker/skills/aw-element/SKILL.md
.codemaker/skills/aw-element-pc/SKILL.md
.codemaker/skills/aw-explorer/SKILL.md
.codemaker/skills/aw-explorer-pc/SKILL.md
.codemaker/skills/aw-verify/SKILL.md
.codemaker/skills/aw-verify-pc/SKILL.md
docs/AW方法总结与复用指南.md
docs/UI元素截取与裁剪规范.md
openspec/config.yaml
openspec/changes/agent-team/.openspec.yaml
openspec/changes/agent-team/design.md
openspec/changes/agent-team/proposal.md
openspec/changes/agent-team/tasks.md
SETUP.md  ← 本文件
```

总计 30 个文件。
