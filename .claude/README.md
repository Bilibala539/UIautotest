# UIAutotest 多 Agent 团队 — 接入与使用指南

> **这份文件写给两类读者**：
> 1. **新加入的开发者** —— 读完后知道怎么在本机把这套团队跑起来
> 2. **AI 助手（Claude / Cursor / Codex 等）** —— 读完后能自主验证环境、引导用户补全缺失步骤，直到团队可用为止
>
> 本文件**自包含**：读完这一份，不需要翻别的资料就能跑起来。AI 助手被要求遵守本文的"AI 操作清单"一节。

---

## 一、这是什么

`E:\UIAutotest` 是一个 Android UI 自动化测试工程。工程内置了一支 **6 人长期 AI 团队**，由 Claude Code 运行时实例化：

| 角色 | 职责 |
|---|---|
| **aw-orchestrator** | 总协调。接需求、分派、汇总（通常由主会话充当） |
| **aw-explorer** | App 探索，维护 `explorer_output/knowledge/` |
| **aw-element** | UI 元素截图，注册 `image/image_name_mapping.py` |
| **aw-codegen** | 写业务 AW、PPUser 便捷方法、pytest 用例 |
| **aw-verify** | 跑 pytest、诊断失败、图片转正 |
| **spec-keeper** | 维护 `openspec/` 下的提案与规范 |

### 架构层次

```
用户
  │
  ▼
主会话（orchestrator）  ← 你在这里下指令
  │
  ├── 按需派出 subagent（读 .claude/agents/<name>.md 作为人设）
  │     ├── aw-explorer    ┐
  │     ├── aw-element     │  5 个专业 agent，一次性/并发/串行调用
  │     ├── aw-codegen     │
  │     ├── aw-verify      │
  │     └── spec-keeper    ┘
  │
  └── 或 TeamCreate 实例化长期团队（/bootstrap-team）
        teammate 可以互发消息、共享 task list
```

### 工程内相关文件

```
E:\UIAutotest\
├── CLAUDE.md                              # 所有 agent 必读的项目约定
├── .claude\
│   ├── README.md                          # ← 本文
│   ├── agents\
│   │   ├── aw-orchestrator.md             # 角色蓝图：总协调
│   │   ├── aw-explorer.md                 # 角色蓝图：探索
│   │   ├── aw-element.md                  # 角色蓝图：截图
│   │   ├── aw-codegen.md                  # 角色蓝图：编码
│   │   ├── aw-verify.md                   # 角色蓝图：验证
│   │   └── spec-keeper.md                 # 角色蓝图：openspec
│   └── commands\
│       ├── bootstrap-team.md              # 一键组队
│       └── verify-team.md                 # 装配自检
├── .codemaker\
│   ├── rules\*.mdc                        # 项目硬性规则
│   └── skills\aw-*\SKILL.md               # 4 把原始 skill（agent 职责的详细描述）
├── docs\
│   ├── AW方法总结与复用指南.md            # 写代码前必读
│   └── UI元素截取与裁剪规范.md            # 截图前必读
├── explorer_output\knowledge\             # App 知识库
│   ├── app_map.json
│   ├── pages\*.md
│   └── digest\**                          # 功能摘要 + 跨页面流程
├── openspec\                              # 能力规范与提案
└── …                                      # 其余测试/工具代码
```

---

## 二、新机器接入：从零到团队可用

### 前置要求

| 项 | 要求 | 验证命令 |
|---|---|---|
| 操作系统 | Windows 10/11 或 macOS/Linux（推荐 Windows，与 MuMu 模拟器配套） | — |
| Claude Code CLI | 已安装 | `claude --version`（应输出 ≥ 2.0.0） |
| Claude 账号 | 已登录且有可用额度 | `claude` 启动后无鉴权报错 |
| Python | 3.10+（真要跑 pytest 时需要） | `python --version` |
| MuMu 模拟器 12 | 已装（**仅测试执行需要**；只用 AI 团队做代码级工作不强制） | — |

### 步骤 1：安装 Claude Code

**Windows**（任选其一）：
```powershell
# winget
winget install -e --id Anthropic.ClaudeCode --accept-source-agreements --accept-package-agreements

# 或者去官网下二进制
# https://claude.com/claude-code
```

**macOS / Linux**：
```bash
curl -fsSL https://claude.com/install.sh | sh
```

装完后：
```bash
claude --version
```

### 步骤 2：登录

```bash
claude
# 首次启动会提示登录。选 Anthropic 账号登录（推荐）或者粘 ANTHROPIC_API_KEY。
# 登录一次，凭据持久化在 ~/.claude/ 下。
```

### 步骤 3：在工程目录启动

**关键**：Claude Code 只加载"启动时所在工程"的 `.claude/` 配置。必须在 `E:\UIAutotest` 目录启动：

```bash
cd /e/UIAutotest      # Git Bash / WSL
# 或
cd E:\UIAutotest      # PowerShell / cmd

claude
```

### 步骤 4：拉起团队

在 Claude Code 会话里输入：
```
/bootstrap-team
```

会自动：
1. `TeamCreate` 实例化 `uiautotest-team`
2. 派出 5 个下游 teammate（explorer / element / codegen / verify / spec-keeper）
3. 让每个 teammate 读完自己蓝图里的"强制前置阅读"清单并汇报就绪
4. 给你一份团队就位简报

### 步骤 5（可选）：自检

```
/verify-team
```

对每个 agent 做 smoke test（读蓝图必读文件 + 回答职责三问），5~10 分钟跑完，确认整套装配无缺失。

---

## 三、核心使用模式

### 模式 A：按需派单个 agent（轻量、推荐日常）

不用组队，直接 `@` 或描述任务，主会话（orchestrator）会按 `CLAUDE.md` 里的分工路由：

```
> 帮我探索「群公告编辑页」的操作路径
   ↓ 主会话识别 → 派 aw-explorer

> 为刚才探索的页面截按钮元素
   ↓ 派 aw-element

> 帮我写一个「编辑群公告并保存」的 pytest 用例
   ↓ 派 aw-codegen

> 跑一下 tests/group/test_announcement.py
   ↓ 派 aw-verify
```

### 模式 B：组队长跑（大任务 / 多轮协作）

```
/bootstrap-team
> 帮我为「富文本编辑」功能做端到端覆盖：
  1. 探索所有相关页面
  2. 截齐元素
  3. 按矩阵生成 pytest 用例
  4. 跑通并转正图片
```

Team lead（主会话）会拆解任务、派活、串联串行流程、失败回退。

### 模式 C：并行独立审查

一次需要多个视角同时评审某块代码 / 文档时：

```
> 让 aw-verify 和 spec-keeper 并行审查 tests/group/ 里的新用例：
  - aw-verify 看测试逻辑、断言质量
  - spec-keeper 看是否需要补充 openspec/specs
```

---

## 四、AI 操作清单（给 AI 助手读）

**任何 AI 助手（Claude、Cursor、Codex 等）在本工程工作时，必须按顺序做以下事。**

### A. 会话启动时

1. **读 `CLAUDE.md`** —— 项目硬性约束
2. **读 `.claude/README.md`**（本文）—— 团队架构和使用方式
3. **识别任务类型** —— 参考下表路由到对应 agent：

| 任务特征 | 派给谁 | 对应蓝图 |
|---|---|---|
| 摸页面 / 知识库缺页面 | aw-explorer | `.claude/agents/aw-explorer.md` |
| 截 UI 元素 / 注册图片常量 | aw-element | `.claude/agents/aw-element.md` |
| 写业务 AW / PPUser / pytest | aw-codegen | `.claude/agents/aw-codegen.md` |
| 跑测试 / 诊断失败 / 图片转正 | aw-verify | `.claude/agents/aw-verify.md` |
| openspec 提案 / spec / tasks | spec-keeper | `.claude/agents/spec-keeper.md` |

4. **派 agent 时**：用 `Agent` 工具，`subagent_type` 设为对应文件名（不含 `.md`）

### B. 环境校验（新机器第一次用）

发现以下任一情况，停下来提示用户：

| 症状 | 可能原因 | 提示用户做什么 |
|---|---|---|
| `.claude/agents/` 目录不存在 | 工程未 clone 完整 / 不在正确目录 | 确认 `cd E:\UIAutotest` 后再启动 |
| Claude Code 启动报鉴权错误 | 未登录或 token 失效 | `claude auth login` 或设置 `ANTHROPIC_API_KEY` |
| Glob `explorer_output/knowledge/*` 为空 | 知识库未同步（可能 .gitignore 忽略了） | 提示用户先 pull 知识库分支或同步 `explorer_output/` |
| 调用 `TeamCreate` 报"experimental" | 未开启 agent teams env | 用户需在 `~/.claude/settings.json` 的 `env` 下加 `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"`，然后重启 Claude Code |
| `python` 是 3.9 或更低 | 虚拟环境没激活或 Python 版本过旧 | 提示用 Python 3.10+ |

### C. 禁止事项

- ❌ 绕过 `CLAUDE.md` 里的任何硬性规则
- ❌ 直接 ADB shell / Playwright / 自造设备调用（必须走 AWBase）
- ❌ 新元素不经 `image_ai/` 暂存直接进 `image/`
- ❌ 写测试只断言"没异常"、或用 try/except 吞掉失败
- ❌ 不读 AW 复用指南就开始写新 AW
- ❌ 不走 openspec 流程直接做大改动
- ❌ 给 teammate 派活时不读对应蓝图的"强制前置阅读"

### D. 每次给 teammate 派活时的样板

```
Agent(
  subagent_type="aw-explorer",  # 对应 .claude/agents/aw-explorer.md
  description="一句话说明任务",
  prompt="""
  你是 uiautotest-team 的 aw-explorer。
  先读完你蓝图里的"强制前置阅读"清单（10 份文件 + glob pages/ 和 digest/features/）。

  本次任务：<具体任务描述>

  产出要求：
  - <期望的交付物形态>

  不要做超出 explorer 职责的事（比如截图、写代码），有需要时回报给 orchestrator 重新分派。
  """
)
```

---

## 五、常见场景速查

### 场景 1：新人第一天接手，什么都没摸过

```
cd E:\UIAutotest
claude

> /bootstrap-team
> /verify-team          # 确认装配无问题
> 先给我一份工程画像：读 README.md + CLAUDE.md + openspec/project.md（如果存在），
  告诉我当前知识库覆盖了哪些功能，哪些还没覆盖
```

### 场景 2：给一个新功能做完整覆盖

```
> /bootstrap-team
> 我要为「会话置顶」功能做端到端覆盖：
  1. explorer 摸清路径（如果 knowledge/ 里没有）
  2. element 截齐按钮图
  3. codegen 写 AW + user 方法 + pytest 用例
  4. verify 跑通并转正
  全程用 @pytest.mark.parametrize 覆盖正/反向场景
```

### 场景 3：某个测试一直挂

```
> aw-verify 帮我诊断 tests/message/test_recall.py 为什么一直失败，
  按图片优先、代码其次的顺序排查，最后给我修复建议
```

### 场景 4：openspec 流程

```
> spec-keeper 帮我起草一个 change：
  "新增消息富文本下的代码块支持"
  读 .codemaker/skills/aw-codegen/SKILL.md 了解现有富文本处理，
  按 openspec/changes/ 现有模板输出 proposal.md / design.md / tasks.md
```

---

## 六、团队的"持久"与"记忆"

### 不会持久的

- 每个 teammate 的**对话上下文**（会话关闭即蒸发）
- teammate 之间的临时消息
- task list（除非显式保留；`TeamDelete` 会一起清）

### 会持久的

- `.claude/agents/*.md` —— 角色蓝图（git 可提交）
- `.claude/commands/*.md` —— 自定义命令
- `CLAUDE.md` —— 项目约定
- 代码改动、知识库更新、openspec 提案、文档

**结论**：团队的"集体记忆"沉在仓库文件里。每次新会话都重新装配，但靠同一套蓝图 + 同一份知识库，行为是**一致可复现**的。

---

## 七、故障排查

### Q1: `/bootstrap-team` 报 "team already exists"

已经有同名团队（可能是上次会话的幂等残留）。两种处理：
- 想复用 → 直接 SendMessage 给现有 teammate
- 想重建 → 先 `TeamDelete`，再 `/bootstrap-team`

### Q2: 派出去的 teammate 抱怨"没有 TaskList / SendMessage 工具"

原因：你用了 `Agent` 工具派 subagent，但类型选的是 `general-purpose`（或其他不带 team 工具的类型）。正确做法：`subagent_type` 一定要用本工程的角色名（`aw-explorer` / `aw-element` 等），这些蓝图才会继承 team 工具。

### Q3: Agent 不读蓝图直接开干

在 prompt 里**显式**要求："先读完你的蓝图文件（路径）里的'强制前置阅读'清单，报告哪些不存在"。

### Q4: 知识库 `app_map.json` 太大读不完

Read 用 `offset` + `limit` 分段，或者先 Grep 关键字定位到相关段。不要为了"完整读一遍"放弃。

### Q5: 多台机器协作时 `.claude/agents/` 不同步

`.claude/agents/` 必须 git commit。检查：
```bash
git status .claude/
git log --oneline .claude/agents/
```

### Q6: MuMu 模拟器端口号 / 窗口大小

ADB 端口 = `7555 + 实例序号`（主实例 7555）。窗口必须 540×960：
```bash
D:\MuMuPlayer\nx_main\MuMuManager.exe control -v <instance_id> layout_window -sw 540 -sh 960
```

---

## 八、扩展团队

要加新角色：
1. 在 `.claude/agents/` 新建 `<name>.md`
2. frontmatter 必含 `name` / `description` / `tools` / `model`
3. 正文是 system prompt，至少包含：
   - "强制前置阅读"清单
   - 职责边界（做什么 / 不做什么）
   - 产出规范
   - 禁止事项
4. 更新本文的 **二 · 团队表** 和 **四 · 路由表**
5. 更新 `bootstrap-team.md`、`verify-team.md`、`CLAUDE.md` 的相关表格

---

## 九、版本与元数据

- 文档版本：1.0
- 适配 Claude Code：2.0+
- 团队结构版本：6-agent（orchestrator + 4 aw + 1 spec）
- 对应开放 change：`openspec/changes/agent-team/`（工程化落地中）

维护者：团队集体维护，走 openspec 流程修改重大结构。
