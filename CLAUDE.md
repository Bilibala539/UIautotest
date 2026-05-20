# UIAutotest 项目约定

> 这份文件是所有 AI 助手（我本人 + `.claude/agents/` 下所有子 agent）每次开工前的第一份必读。
> 变更请慎重，因为它影响整个团队的行为。

## 项目一句话

基于 **pytest + MuMu 模拟器 + ADB** 的安卓 UI 自动化测试框架，针对网易 **POPO** App。图像识别（OpenCV 模板匹配）+ OCR（PaddleOCR）定位。

## 关键路径速查

| 路径 | 用途 |
|---|---|
| `conftest.py` | pytest 全局 fixture |
| `utils/aw/aw_base.py` | AWBase —— 设备交互唯一入口 |
| `utils/aw/business/mumu.py` | 业务 AW 方法层 |
| `utils/user.py` | PPUser —— 暴露给测试用例的便捷方法 |
| `tests/mumu/` | pytest 用例 |
| `image/` | **正式**元素图片（跑通后才进） |
| `image_ai/` | **暂存**元素图片（新截的） |
| `image/image_name_mapping.py` | 所有图片常量 |
| `explorer_output/knowledge/` | App 知识库（app_map.json + pages/*.md + digest/） |
| `explorer_output/knowledge/digest/` | 功能摘要 + 跨页面流程 |
| `docs/AW方法总结与复用指南.md` | 已封装业务 AW 清单 —— 写新代码前必查 |
| `docs/UI元素截取与裁剪规范.md` | 元素截图规范 |
| `docs/并行测试执行指南.md` | 多 MuMu 实例并行跑测试 —— 换机器必读 |
| `run_parallel.py` | 并行测试运行器入口 |
| `.codemaker/rules/` | 项目硬性规则（ai_workflow / aw_architecture / rules） |
| `.codemaker/skills/` | 4 把 aw-* skill 原始定义 |
| `openspec/changes/` | 开放提案 |
| `openspec/specs/` | 已归档的能力规范 |

## 硬性规则（任何 agent 都必须遵守）

### 1. 设备交互必须走 AWBase

**严禁**直接 ADB shell、Playwright、浏览器实例、或任何非 AWBase 的工具操作设备。如果 AWBase 没封装某个操作，先在 AWBase 加方法，再调用。

### 2. 禁止 tap 坐标

元素定位一律用 `click_image` 或 `click_text`。坐标会因分辨率、窗口位置变化而失效。

### 3. 分辨率统一 540×960

截图、元素库、测试运行三者的窗口大小必须一致。

### 4. 图片流转：暂存 → 正式

- 新截元素先进 `image_ai/`，`image_name_mapping.py` 里用 `test_path` 常量
- 测试通过后由 aw-verify 转正：文件 `image_ai/ → image/`，mapping 里 `test_path → path`

### 5. 复用优先

写新 AW / 用例前必须先读 `docs/AW方法总结与复用指南.md`。常用便捷方法：
- `user.send_message(recipient, message, isback=False)` —— 进会话发消息
- `user.search(tab, text, isclose=False)` —— 搜索
- `user.open_sidebar()` / `user.open_settings()` —— 打开侧边栏/设置

### 6. 断言优先级

图片断言 > OCR 文字断言。尽量使用截图图像识别，尽量不用 OCR。**禁止"只断言没异常"**。禁止 `try/except` 让失败测试看起来通过。

### 7. 失败归因顺序

`image_exists` / `click_image` 失败时：**先查图片质量，再查代码逻辑**。不要在图片有问题的情况下反复改代码。

### 8. 测试合并

同功能不同参数合并成一个 py 文件用 `@pytest.mark.parametrize`；不要一条文字用例对应一个 py 文件。

## 团队分工

本项目在 `.claude/agents/` 下定义了长期团队角色。主会话作为 **orchestrator** 对接用户；遇到具体任务派给对应 agent：

| 任务特征 | 派给谁 |
|---|---|
| 摸清某个页面怎么走 / 知识库缺页面 | `aw-explorer` |
| 截 UI 元素并注册常量 | `aw-element` |
| 写业务 AW / PPUser 方法 / pytest 用例 | `aw-codegen` |
| 跑 pytest / 诊断失败 / 图片转正 | `aw-verify` |
| openspec 提案 / spec / tasks 维护 | `spec-keeper` |

要一键拉起整个团队：`/bootstrap-team`。

## openspec 流程

涉及新能力或大改动：
1. 走 `openspec-propose`（或 `spec-keeper` agent）生成 change
2. 实现时用 `openspec-apply-change` 推进
3. 完成后 `openspec-archive-change` 归档

当前开放 change：`openspec/changes/agent-team/`（把 4 个 skill 封装成 Python Agent 类的状态机工程化落地）。

## 并行测试执行

checklist 下 138 个用例可用 `run_parallel.py` 并行跑，缩短到约 1/3 耗时。

**机制**：预启动 N 个 MuMu 实例 → 测试文件均匀分片 → N 个独立 pytest 进程各管一个实例（`INSTANCE_ID` 绑定端口 + 账号）。

**账号自动映射**（避免同一账号多设备登录互踢）：
```
INSTANCE_ID=0 → userA (grp.popoqa67)   端口 16384
INSTANCE_ID=1 → userB (grp.popoqa73)   端口 16416
INSTANCE_ID=2 → userC (grp.popoqa74)   端口 16448
INSTANCE_ID=3 → userD (grp.popoqa75)   端口 16480
```
用例无需改动，仍写 `self.users("userA")`，框架按 INSTANCE_ID 自动映射。

**用法**：
```bash
python run_parallel.py                    # 3 实例全量
python run_parallel.py -n 2 -t 5          # 2 实例跑 5 个文件（验证用）
```

**串行模式不受影响**：不设 `INSTANCE_ID` 时 `_device_index` 默认 0，`_user_key_map` 为空，行为不变。

详细原理、换机器检查清单、故障排查见 `docs/并行测试执行指南.md`。

## 禁止事项速查

- ❌ 直接 ADB shell / 绕过 AWBase
- ❌ `tap(x, y)` 坐标点击
- ❌ 截图时窗口不是 540×960
- ❌ 截入动态元素（角标/时间/头像/在线状态）
- ❌ 新元素直接进 `image/`（必须先 `image_ai/`）
- ❌ 不读 AW 复用指南就开始写代码
- ❌ `try/except` 吞掉测试失败
- ❌ 只断言"没异常"
- ❌ 一条用例一个 py 文件（应合并）
- ❌ 不走 openspec 流程直接做大改动

## 运行时经验（踩坑积累，所有 agent 必知）

| 场景 | 正确做法 |
|------|----------|
| MuMu 开关控件点击 | 点 x=450-480, y=555；不要用模板匹配图片 |
| 管理标签页：删除自定义标签页 | 点右侧三点按钮（x≈510）→ 底部弹窗 → 选删除；左侧 icon 只是切换展示/隐藏，不是删除 |
| Python 多行命令 | 走 PowerShell 执行；避免 CodeMaker Hub 路径校验报错 |
