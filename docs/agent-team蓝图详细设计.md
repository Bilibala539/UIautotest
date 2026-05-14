# agent-team 蓝图详细设计

> 本文档详细解释 `openspec/changes/agent-team/` 下的工程化蓝图。
> 目标：将当前 4 个对话驱动的 Markdown Skill 封装为 4 个代码驱动的 Python Agent 类，
> 用状态机引擎自动串联，实现 `python -m agent_team "任务描述"` 一句话跑完整条流水线。

---

## 一、名字解释

在深入设计之前，先把蓝图中反复出现的核心名字逐一解释清楚。

### 1.1 Agent（智能体）

**Agent** 在蓝图中指一个可以独立执行特定任务的 Python 对象。每个 Agent 封装了一个技能（Skill）的全部操作逻辑，对外暴露统一接口 `execute(ctx) -> ctx`。蓝图中有 4 个具体 Agent：

| Agent | 对应 Skill | 一句话职责 |
|-------|-----------|----------|
| ExplorerAgent | aw-explorer | 连接模拟器，探索 App 页面，产出地图 |
| ElementAgent | aw-element | 从截图中裁切 UI 元素，注册到图片库 |
| CodegenAgent | aw-codegen | 根据地图和元素写业务代码和测试用例 |
| VerifyAgent | aw-verify | 跑测试，分析失败，把图片转正 |

Agent 之间不直接对话，全部通过共享上下文传递信息。

### 1.2 Orchestrator（编排器 / 调度器）

**Orchestrator** 是整条流水线的总指挥。它维护一个"阶段 → Agent"的映射表，根据当前阶段选择对应的 Agent 执行，管理重试和回退策略。类比乐团指挥（orchestra conductor）——他不演奏任何乐器，但决定谁在什么时候演奏。

### 1.3 TeamContext（团队上下文）

**TeamContext** 是一个 `@dataclass` 数据容器，是 Agent 之间传递信息的唯一媒介。所有 Agent 都读写同一个 TeamContext 对象，不需要文件系统或消息队列中转。

可以把它理解为**工单传递单**：每个工位（Agent）从工单上读取上一工位填写的信息，做完自己的活后把结果写回工单，传给下一工位。

包含的核心字段：
- 任务描述（要测什么）
- 当前阶段（流水线走到了哪一步）
- 知识库（探索发现了哪些页面和元素）
- 元素列表（截了哪些图）
- 生成文件路径（写了哪些代码）
- 验证结果（测试通过了没有，没过的话回退到哪）
- 重试计数（已经重试了几次）

### 1.4 Phase（阶段 / 流水线节点）

**Phase** 是一个枚举类型，定义了流水线的 6 个状态节点：

```
EXPLORE → ELEMENT → CODEGEN → VERIFY → DONE
                                  ├→ EXPLORE / ELEMENT / CODEGEN（回退）
                                  └→ FAILED（超过最大重试次数，放弃）
```

流水线按箭头方向正向流转，验证失败时反向回退，超过最大重试次数后进入 FAILED 终态。

### 1.5 Skill（技能）

**Skill** 指 `.codemaker/skills/` 下的 Markdown 文件，每个文件是一份给 AI 助手阅读的指令文档，描述如何完成某项工作（如如何截取 UI 元素）。蓝图**不删除**这些 Skill 文件，而是让 Agent 把 Skill 中描述的步骤**翻译成可执行的 Python 代码**。Skill 继续保留作为 AI 助手的参考文档。

简单理解：**Skill = 菜谱（给人看的），Agent = 厨师（真正做菜的）**。

### 1.6 ElementInfo（元素信息条目）

**ElementInfo** 是描述一个 UI 元素图片的数据结构，包含 4 个字段：
- `name`：元素中文名，如"消息设置页-开关按钮"
- `image_path`：图片在磁盘上的路径
- `constant_name`：在 `image_name_mapping.py` 中注册的常量名，如 `MSG_SETTING_SWITCH`
- `is_verified`：该图片是否已通过测试验证（未通过为 `test_path` 暂存状态，通过后转正为 `path`）

### 1.7 VerifyResult（验证结果）

**VerifyResult** 是验证阶段结束后产出的诊断报告，包含 4 个字段：
- `success`：bool，全部测试是否通过
- `test_output`：pytest 的完整命令行输出
- `failure_reasons`：失败原因的列表（可能多条）
- `suggested_phase`：建议回退到哪个阶段（ELEMENT / CODEGEN / EXPLORE）

### 1.8 回退（Rollback / Retry）

**回退**指验证失败后，流水线不是直接报错退出，而是跳回之前的某个阶段重新执行。蓝图的回退策略是**递增回退**：

| 重试次数 | 回退到 | 理由 |
|---------|--------|------|
| 第 1 次 | ELEMENT | 多半是元素图片截得不好，重新截图 |
| 第 2 次 | CODEGEN | 图没问题，可能是代码逻辑写错了 |
| 第 3 次 | EXPLORE | 代码也对，可能是页面路径变了，重新探索 |
| 第 4 次 | — | 三次都修不好，标记 FAILED，输出完整诊断 |

---

## 二、为什么要做这个蓝图

### 当前的问题

现在的流程是**人 + AI 半自动**：

```
用户说"帮我覆盖消息设置功能"
  → orchestrator agent（对话中）拆解意图
  → SendMessage 派给 aw-explorer agent → 探索页面
  → SendMessage 派给 aw-element agent  → 截取元素
  → SendMessage 派给 aw-codegen agent  → 写代码
  → SendMessage 派给 aw-verify agent   → 跑验证
```

每一步都需要 orchestator 在对话中**手动派发**，产物（探索记录、元素列表、代码路径）靠**对话上下文**传递。一个功能从探索到验证通过通常要来回操作 10+ 次。

### 蓝图要解决的核心问题

**把对话驱动的流程变成代码驱动的状态机**。用一句话概括蓝图的野心：

> `python -m agent_team "测试消息设置功能"` —— 回车之后，全流程自动跑完，人不需要参与。

---

## 三、整体架构

```
┌────────────────────────────────────────────────────────────┐
│                      CLI 入口                              │
│              python -m agent_team "任务描述"                │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                    Orchestrator（调度器）                    │
│                                                            │
│   while phase not in (DONE, FAILED):                       │
│       agent = phase_map[phase]                             │
│       agent.validate_input(ctx)                            │
│       ctx = agent.execute(ctx)                             │
│       if 需要重试 and retry_count < max_retries: 继续        │
│                                                            │
│   Phase → Agent 映射表:                                     │
│     EXPLORE → ExplorerAgent                                │
│     ELEMENT → ElementAgent                                 │
│     CODEGEN → CodegenAgent                                 │
│     VERIFY  → VerifyAgent                                  │
└────┬──────────┬──────────┬──────────┬──────────────────────┘
     │          │          │          │
     ▼          ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Explorer │ │Element  │ │Codegen  │ │Verify   │
│Agent    │ │Agent    │ │Agent    │ │Agent    │
│         │ │         │ │         │ │         │
│探索App  │ │截元素图  │ │写AW/用例│ │跑验证   │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │          │          │          │
     └──────────┴──────────┴──────────┘
                    │
                    ▼
            ┌──────────────┐
            │ TeamContext  │  ← 所有 Agent 共读共写的数据容器
            │  (dataclass) │
            └──────────────┘
```

---

## 四、目录结构

```
E:\UIAutotest\
└── agent_team/                     # ← 新增目录，蓝图的核心产物
    ├── __init__.py                 # 模块导出，from agent_team import ...
    ├── __main__.py                 # 支持 python -m agent_team 启动
    ├── run.py                     # CLI 入口，封装启动逻辑
    ├── config.py                  # 配置常量（MAX_RETRIES / LOG_DIR 等）
    ├── context.py                 # TeamContext + Phase + ElementInfo + VerifyResult
    ├── base_agent.py              # BaseAgent 抽象基类
    ├── orchestrator.py            # 状态机调度器
    └── agents/                    # 4 个具体 Agent 实现
        ├── __init__.py
        ├── explorer_agent.py      # 探索 Agent
        ├── element_agent.py       # 截图 Agent
        ├── codegen_agent.py       # 编码 Agent
        └── verify_agent.py        # 验证 Agent
```

---

## 五、核心数据结构设计

### 5.1 Phase 阶段枚举

```python
from enum import Enum

class Phase(Enum):
    """流水线的 6 个状态节点"""
    EXPLORE  = "explore"    # 探索 App 页面
    ELEMENT  = "element"    # 截取 UI 元素图片
    CODEGEN  = "codegen"    # 生成 AW 代码和测试用例
    VERIFY   = "verify"     # 运行测试并验证
    DONE     = "done"       # 终态：全部通过
    FAILED   = "failed"     # 终态：超过最大重试，放弃
```

**流转规则**：

```
正常流程: EXPLORE → ELEMENT → CODEGEN → VERIFY → DONE

失败回退: VERIFY ──→ ELEMENT  (重试1)
                ──→ CODEGEN  (重试2)
                ──→ EXPLORE  (重试3)
                ──→ FAILED   (超过上限)
```

### 5.2 TeamContext 团队上下文

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

@dataclass
class TeamContext:
    """
    所有 Agent 之间传递信息的唯一载体。

    类比工单传递单：每个工位从工单上读上一工位填写的信息，
    做完活后把结果写回工单，传给下一工位。
    """

    # ── 任务信息 ──
    task_description: str
    """任务描述文本，例如"测试消息设置页面的开关功能" """

    # ── 阶段控制 ──
    current_phase: Phase = Phase.EXPLORE
    """当前所处的流水线阶段，初始为 EXPLORE"""

    retry_count: int = 0
    """已经重试的次数，初始为 0"""

    max_retries: int = 3
    """允许的最大重试次数，默认 3"""

    # ── 探索阶段产出 ──
    knowledge_base: dict = field(default_factory=dict)
    """
    探索 Agent 产出的知识库数据。
    格式兼容 explorer_output/knowledge/app_map.json 结构。
    包含 pages（页面字典）和 elements（元素字典）。
    """

    discovered_pages: List[str] = field(default_factory=list)
    """探索发现的页面 ID 列表，如 ["message_page", "settings_page"]"""

    # ── 截图阶段产出 ──
    elements: List["ElementInfo"] = field(default_factory=list)
    """截取的 UI 元素图片信息列表，每项是一个 ElementInfo"""

    # ── 编码阶段产出 ──
    generated_files: dict = field(default_factory=dict)
    """
    生成的文件路径映射:
    {
        "aw_file": "utils/aw/business/mumu.py",
        "user_file": "utils/user.py",
        "test_file": "tests/mumu/checklist/test_msg_setting.py"
    }
    """

    # ── 验证阶段产出 ──
    verify_result: Optional["VerifyResult"] = None
    """验证 Agent 的执行结果，包含成功/失败/回退建议"""

    # ── 执行记录 ──
    logs: List[str] = field(default_factory=list)
    """执行过程中的日志记录，供报告使用"""
```

### 5.3 ElementInfo 元素信息

```python
@dataclass
class ElementInfo:
    """描述截取的一个 UI 元素图片"""

    name: str
    """元素中文名，如 "消息设置页-开关按钮" """

    image_path: str
    """图片在磁盘上的路径，如 "image_ai/消息设置页-开关按钮.png" """

    constant_name: str
    """在 image_name_mapping.py 中的常量名，如 "MSG_SETTING_SWITCH" """

    is_verified: bool = False
    """是否已通过测试验证。初始为 False，转正后变为 True"""
```

### 5.4 VerifyResult 验证结果

```python
@dataclass
class VerifyResult:
    """验证 Agent 执行后产出的诊断报告"""

    success: bool
    """全部测试是否通过"""

    test_output: str
    """pytest 命令行的完整输出文本"""

    failure_reasons: List[str] = field(default_factory=list)
    """
    失败原因列表，可能包含多条。示例:
    - "图片匹配失败: image_ai/消息设置页-开关按钮.png 阈值 0.75 < 0.8"
    - "ImportError: cannot import name 'toggle_notification'"
    """

    suggested_phase: Optional["Phase"] = None
    """
    失败时建议回退的阶段:
    - 图片匹配失败 → Phase.ELEMENT
    - 代码错误     → Phase.CODEGEN
    - 设备问题     → Phase.EXPLORE
    成功时为 None
    """
```

---

## 六、BaseAgent 抽象基类

这是所有 4 个 Agent 的公共骨架，定义了统一的接口契约。

```python
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Agent 抽象基类，所有具体 Agent 必须继承此类"""

    # ══════════════════════════════════════════════════════
    # 抽象属性：子类必须覆盖
    # ══════════════════════════════════════════════════════

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Agent 的名称标识，用于日志输出。
        例如 "ExplorerAgent"、"ElementAgent"
        """
        ...

    @property
    @abstractmethod
    def phase(self) -> Phase:
        """
        Agent 负责的流水线阶段。
        例如 Phase.EXPLORE、Phase.VERIFY
        """
        ...

    # ══════════════════════════════════════════════════════
    # 抽象方法：子类必须实现
    # ══════════════════════════════════════════════════════

    @abstractmethod
    def execute(self, ctx: TeamContext) -> TeamContext:
        """
        执行 Agent 的核心逻辑。

        执行契约（子类必须遵守）：
        1. 从 ctx 读取本阶段需要的输入字段
        2. 执行操作（探索 / 截图 / 编码 / 验证）
        3. 将本阶段产出写入 ctx 的对应字段
        4. 设置 ctx.current_phase 为下一个阶段
        5. 返回修改后的 ctx

        异常处理：
        执行过程中的异常 SHALL 自然向上抛出，不在此方法内捕获。
        由 Orchestrator 统一处理。

        Args:
            ctx: 团队上下文（包含前置阶段的产出）

        Returns:
            修改后的 TeamContext（本阶段产出已写入）
        """
        ...

    @abstractmethod
    def validate_input(self, ctx: TeamContext) -> None:
        """
        校验前置条件是否满足。

        不同 Agent 的校验规则：
        - ExplorerAgent: ctx.task_description 不能为空
        - ElementAgent:  ctx.discovered_pages 不能为空
        - CodegenAgent:  ctx.elements 和 ctx.knowledge_base 都不能为空
        - VerifyAgent:   ctx.generated_files 必须包含 "test_file" 键

        校验失败时抛出 ValueError，附带明确的错误信息。

        例如: raise ValueError("任务描述不能为空，请先设置 ctx.task_description")

        Args:
            ctx: 待校验的团队上下文

        Raises:
            ValueError: 前置条件不满足
        """
        ...

    # ══════════════════════════════════════════════════════
    # 默认方法：子类可以覆盖
    # ══════════════════════════════════════════════════════

    def report(self, ctx: TeamContext) -> str:
        """
        生成本 Agent 的执行摘要。

        默认实现返回基本信息（Agent 名 + 阶段）。
        子类可以覆盖此方法，追加本阶段特有的统计信息。

        Returns:
            单行或简短多行的执行摘要文本
        """
        return f"[{self.name}] 阶段 {self.phase.value} 执行完成"
```

**为什么用抽象基类而不是普通类？**

因为每个 Agent 的 `execute` 逻辑完全不同（探索 ≠ 截图 ≠ 编码 ≠ 验证），但接口契约相同。抽象基类强制子类实现所有方法，如果漏掉了某个方法，Python 在实例化时就会报 `TypeError`，而不是运行时才暴露问题。

---

## 七、四个 Agent 详解

### 7.1 ExplorerAgent —— 探索员

```
┌─────────────── ExplorerAgent ───────────────┐
│                                              │
│  输入: ctx.task_description                  │
│        ctx.knowledge_base（可能有已有数据）   │
│                                              │
│  执行:                                       │
│   1. 通过 utils/devices 连接 MuMu 模拟器      │
│   2. 启动 POPO 应用                          │
│   3. 根据任务描述导航到目标功能区域           │
│   4. 逐页面截图 + OCR 识别可交互元素          │
│   5. 记录页面跳转关系和操作路径               │
│                                              │
│  输出: ctx.knowledge_base（兼容 app_map.json）│
│        ctx.discovered_pages                  │
│        ctx.current_phase = Phase.ELEMENT     │
│                                              │
│  校验: task_description 不能为空              │
│                                              │
└──────────────────────────────────────────────┘
```

**关键设计点**：

- **不绕过 AWBase**：探索过程中的截图、OCR、点击全部走 `AWBase` 方法，严禁直接 ADB shell。这跟当前 aw-explorer skill 的规则完全一致。
- **知识库格式向后兼容**：产出的 `ctx.knowledge_base` 数据结构必须能直接序列化为现有的 `app_map.json` 格式，保证后续 ElementAgent 和 CodegenAgent 可以无感切换。
- **完整性校验**：执行完成后自检 —— `discovered_pages` 至少包含 1 个页面，`knowledge_base` 必须包含 `pages` 和 `elements` 两个顶层键。不满足则抛出异常。
- **设备连接失败时明确报错**：`adb_connect` 失败时抛出 `ConnectionError`，日志中输出设备端口和错误信息，不静默失败。

---

### 7.2 ElementAgent —— 截图员

```
┌─────────────── ElementAgent ────────────────┐
│                                              │
│  输入: ctx.knowledge_base                    │
│        ctx.discovered_pages                  │
│                                              │
│  执行:                                       │
│   1. 遍历 knowledge_base 中每个页面的元素     │
│   2. 从探索截图中裁切每个 UI 元素             │
│   3. 质量检查（灰度/尺寸/角标检测）           │
│   4. 保存到 image_ai/ 目录                   │
│   5. 在 image_name_mapping.py 注册常量        │
│                                              │
│  输出: ctx.elements（List[ElementInfo]）      │
│        ctx.current_phase = Phase.CODEGEN     │
│                                              │
│  校验: discovered_pages 不能为空              │
│                                              │
└──────────────────────────────────────────────┘
```

**关键设计点**：

- **截取规范完全复用现有规则**：
  - 分辨率 540×960
  - 紧贴元素边缘（留 1~2px）
  - 每张图只包含 1 个元素
  - 避开红色角标（R>200, G<160, R-G>40）、头像、时间戳
  - 避开窗口边缘阴影（底部 y>935、顶部 y<40）
- **质量检查**：灰度标准差 > 5（不是空白）、均值 5~250（不是全黑/全白）、最小 10×10 像素。不合格的元素重试截取最多 2 次，还不行抛出异常。
- **常量注册用 test_path**：新截图片全部进 `image_ai/` 暂存目录，映射中用 `test_path`。只有通过验证后才由 VerifyAgent 转正。
- **ElementInfo 的 is_verified 初始全为 False**：表示所有元素都处于"待验证"状态。

---

### 7.3 CodegenAgent —— 代码生成员

```
┌────────────── CodegenAgent ─────────────────┐
│                                              │
│  输入: ctx.knowledge_base（操作流程）         │
│        ctx.elements（图片常量列表）           │
│                                              │
│  执行:                                       │
│   1. 根据操作流程生成 AW 业务方法              │
│   2. 追加到 utils/aw/business/mumu.py        │
│   3. 在 utils/user.py PPUser 中加代理方法     │
│   4. 生成 pytest 用例文件到 tests/mumu/       │
│                                              │
│  输出: ctx.generated_files                   │
│        ctx.current_phase = Phase.VERIFY      │
│                                              │
│  校验: ctx.elements 和 knowledge_base 都非空  │
│                                              │
└──────────────────────────────────────────────┘
```

**关键设计点**：

- **AW 方法编码铁律**：
  - 禁止 `self.tap(x, y)` 硬编码坐标
  - 优先 `self.click_image()`，次选 `self.click_text()`
  - 断言优先 `self.image_exists()`
  - 引用元素时用常量名而非字符串路径
- **PPUser 代理方法**：简单委托 `self.aw.xxx()`，不写业务逻辑。
- **测试用例模板**：继承 `BaseTest`，包含 `setup()` 和 `teardown()`，一个功能一个文件，同功能不同参数用 `@pytest.mark.parametrize` 合并。
- **生成文件路径全部记录**：`ctx.generated_files` 包含三个键 —— `aw_file`、`user_file`、`test_file`，方便 VerifyAgent 找到要跑的测试文件。

---

### 7.4 VerifyAgent —— 验证员

```
┌─────────────── VerifyAgent ─────────────────┐
│                                              │
│  输入: ctx.generated_files["test_file"]      │
│        ctx.elements                          │
│                                              │
│  执行:                                       │
│   1. subprocess.run 调用 pytest 运行用例      │
│   2. 解析 pytest 输出，判断成功/失败          │
│   3a. 成功 → 图片转正 image_ai/ → image/     │
│             更新 is_verified = True          │
│             current_phase = DONE             │
│   3b. 失败 → 分析失败原因，给回退建议         │
│             retry_count += 1                 │
│             current_phase = 建议回退阶段      │
│                                              │
│  输出: ctx.verify_result                     │
│        ctx.current_phase（DONE 或回退阶段）   │
│                                              │
│  校验: generated_files 含 "test_file" 键      │
│                                              │
└──────────────────────────────────────────────┘
```

**关键设计点**：

- **运行方式**：通过 `subprocess.run` 调用 `pytest {test_file} -v`，不通过 pytest API 编程调用。这样能复用现有的 conftest.py 配置和所有 fixture。
- **失败分类逻辑**（按优先级匹配）：
  1. 输出含"未找到图片" / "image_exists 超时" → 推断为图片匹配问题 → 建议回退 ELEMENT
  2. 输出含 `ImportError` / `NameError` / `AttributeError` → 推断为代码问题 → 建议回退 CODEGEN
  3. 输出含 `AssertionError` → 推断为业务逻辑断言失败 → 建议回退 CODEGEN
  4. 输出含 ADB 连接错误 → 推断为设备问题 → 建议回退 EXPLORE
  5. 无法识别 → 默认建议回退 CODEGEN
- **图片转正**：
  - 测试全部通过后，遍历 `ctx.elements` 中 `is_verified=False` 的元素
  - 将 `image_ai/{name}.png` 移动到 `image/{name}.png`
  - 在 `image_name_mapping.py` 中将 `test_path` 替换为 `path`
  - 标记 `is_verified = True`
- **递增回退**：VerifyAgent 不直接实现递增逻辑（那是 Orchestrator 的职责），它只负责分析失败并给出本次建议。Orchestrator 根据 `retry_count` 决定是否要进一步回退。

---

## 八、Orchestrator 状态机引擎

这是整条流水线的"大脑"，负责驱动阶段流转、管理重试、输出日志和报告。

```python
class Orchestrator:
    """
    状态机调度器。

    职责：
    1. 维护 Phase → Agent 的映射表
    2. 根据 ctx.current_phase 选择对应 Agent 执行
    3. 管理重试逻辑和递增回退
    4. 输出阶段日志和执行报告
    """

    def __init__(self):
        self._agents = {
            Phase.EXPLORE: ExplorerAgent(),
            Phase.ELEMENT: ElementAgent(),
            Phase.CODEGEN: CodegenAgent(),
            Phase.VERIFY:  VerifyAgent(),
        }

    def run(self, task: str, max_retries: int = 3) -> TeamContext:
        """
        启动流水线并驱动完整状态机循环。

        伪代码:
        ┌─────────────────────────────────────────┐
        │ ctx = TeamContext(task_description=task) │
        │ ctx.max_retries = max_retries            │
        │                                          │
        │ while ctx.current_phase not in (DONE, FAILED): │
        │     agent = self._agents[ctx.current_phase]    │
        │     agent.validate_input(ctx)            │  ← 校验前置条件
        │     log("🤖 [阶段名] Agent名 开始执行")   │
        │     ctx = agent.execute(ctx)             │  ← 执行核心逻辑
        │     log("✅ [阶段名] 完成 → 下一阶段")    │
        │                                          │
        │     if ctx.current_phase == DONE:        │
        │         break  # 成功，退出循环           │
        │                                          │
        │     # 走到这里说明是回退                  │
        │     ctx.retry_count += 1                 │
        │     if ctx.retry_count > ctx.max_retries:│
        │         ctx.current_phase = FAILED       │
        │         log("❌ 超过最大重试次数")        │
        │     else:                                │
        │         log("⚠️ 重试 N/M")               │
        │                                          │
        │ return ctx                               │
        └─────────────────────────────────────────┘
        """

    def _generate_report(self, ctx: TeamContext) -> str:
        """生成最终执行报告，输出总耗时、各阶段状态、重试次数、最终结果"""
```

**关键设计点**：

- **主循环是 while + phase 跳转**：不预设具体执行几次，由 `ctx.current_phase` 的值驱动下一轮循环选择哪个 Agent。这比硬编码"执行 4 次"灵活得多——回退多少次都能处理。
- **重试不设内部计数器**：Orchestrator 不维护 `retry_count`（这个字段在 TeamContext 中），只负责判断是否超限。VerifyAgent 每次失败时自增 `retry_count`。
- **FAILED 报告的含金量**：不止说"失败了"，还包含各阶段的执行状态、每次重试的原因、最终失败根因分析，能直接交给用户决策。
- **日志风格**：沿用项目习惯的表情符号格式（🤖 ✅ ❌ ⚠️），和现有 AW 代码风格一致。

---

## 九、CLI 命令行入口

### 使用方式

```bash
# 基本启动
python -m agent_team "消息设置功能测试"

# 指定最大重试次数为 5 次
python -m agent_team "消息设置功能测试" --max-retries 5

# 使用 YAML 配置文件
python -m agent_team --config task_config.yaml

# 无参数启动 → 显示帮助
python -m agent_team
```

### YAML 配置文件格式

```yaml
# task_config.yaml
task: "测试消息设置页面的通知开关功能"
max_retries: 3
start_phase: "explore"          # explore / element / codegen / verify
device_instance_id: 0           # MuMu 模拟器实例 ID
```

配置文件中 `start_phase` 支持指定起始阶段，这样可以从中间阶段开始执行（比如探索已经完成，直接从截图开始）。这是蓝图中标记为"Phase 2"的功能。

### 执行完成后的输出

**终端摘要**（简洁，适合快速判断）：

```
═══════════════════════════════════════════
✅ Agent Team 执行完成

任务: 消息设置功能测试
状态: 成功
耗时: 5 分 32 秒
重试: 1 次
生成文件:
  - AW 方法: utils/aw/business/mumu.py (新增 toggle_notification)
  - PPUser:   utils/user.py (新增 toggle_notification)
  - 测试用例: tests/mumu/checklist/test_msg_setting.py
  - 元素图片: 3 张（已转正）
═══════════════════════════════════════════
```

**详细报告**（保存到 `logs/agent_team/{timestamp}_report.md`）：包含每个阶段的开始时间、结束时间、执行状态、错误详情（如有）、重试历史等完整信息，用于事后排查。

---

## 十、完整执行流程示例

以一个具体任务为例，展示 TeamContext 在流水线中如何一步步被填充：

```
═══════════════════════════════════════════════════════════════
初始状态
═══════════════════════════════════════════════════════════════
TeamContext(
    task_description = "测试消息设置页面的连续播放语音消息开关",
    current_phase    = Phase.EXPLORE,
    retry_count      = 0,
    max_retries      = 3,
    knowledge_base   = {},       # 空，待填充
    discovered_pages = [],       # 空，待填充
    elements         = [],       # 空，待填充
    generated_files  = {},       # 空，待填充
    verify_result    = None,     # 空，待填充
)

═══════════════════════════════════════════════════════════════
第 1 轮：ExplorerAgent 执行
═══════════════════════════════════════════════════════════════
→ adb_connect → 启动 POPO → 导航到消息设置页
→ 截图 + OCR 识别页面元素
→ 记录跳转路径: message_page → sidebar → settings_page → message_settings_page

执行后 ctx 变化:
  knowledge_base = {
      "pages": {
          "message_settings_page": {
              "name": "消息设置页面",
              "elements": ["连续播放语音消息", "通知开关", "消息预览"],
              "screenshot": "screenshots/msg_settings.png"
          }
      },
      "elements": { ... }
  }
  discovered_pages = ["message_page", "sidebar", "settings_page", "message_settings_page"]
  current_phase = Phase.ELEMENT

═══════════════════════════════════════════════════════════════
第 2 轮：ElementAgent 执行
═══════════════════════════════════════════════════════════════
→ 遍历 knowledge_base 中的元素
→ 从截图中裁切"连续播放语音消息"开关按钮
→ 质量检查通过 → 保存到 image_ai/消息设置页-连续播放语音开关.png
→ 注册常量 MSG_SETTING_AUTO_PLAY_SWITCH

执行后 ctx 变化:
  elements = [
      ElementInfo(
          name="消息设置页-连续播放语音开关",
          image_path="image_ai/消息设置页-连续播放语音开关.png",
          constant_name="MSG_SETTING_AUTO_PLAY_SWITCH",
          is_verified=False
      )
  ]
  current_phase = Phase.CODEGEN

═══════════════════════════════════════════════════════════════
第 3 轮：CodegenAgent 执行
═══════════════════════════════════════════════════════════════
→ 在 mumu.py 中追加 toggle_auto_play_voice() 方法
→ 在 user.py PPUser 中追加代理方法
→ 生成 tests/mumu/checklist/test_msg_setting.py

执行后 ctx 变化:
  generated_files = {
      "aw_file":   "utils/aw/business/mumu.py",
      "user_file": "utils/user.py",
      "test_file": "tests/mumu/checklist/test_msg_setting.py"
  }
  current_phase = Phase.VERIFY

═══════════════════════════════════════════════════════════════
第 4 轮：VerifyAgent 执行（场景 A：成功）
═══════════════════════════════════════════════════════════════
→ pytest tests/mumu/checklist/test_msg_setting.py -v
→ 输出: 1 passed in 12.34s
→ 图片转正: image_ai/→image/，test_path→path，is_verified=True

执行后 ctx 变化:
  verify_result = VerifyResult(success=True, test_output="1 passed...", ...)
  elements[0].is_verified = True
  current_phase = Phase.DONE

→ 循环结束，输出成功报告。

═══════════════════════════════════════════════════════════════
第 4 轮：VerifyAgent 执行（场景 B：失败 → 回退）
═══════════════════════════════════════════════════════════════
→ pytest tests/mumu/checklist/test_msg_setting.py -v
→ 输出: FAILED - 未找到图片 MSG_SETTING_AUTO_PLAY_SWITCH

执行后 ctx 变化:
  verify_result = VerifyResult(
      success=False,
      test_output="...FAILED...",
      failure_reasons=["图片匹配失败: MSG_SETTING_AUTO_PLAY_SWITCH 匹配阈值 0.65 < 0.8"],
      suggested_phase=Phase.ELEMENT  # ← 建议回退到截图阶段
  )
  retry_count = 1
  current_phase = Phase.ELEMENT

→ Orchestrator 检查: retry_count(1) < max_retries(3)，继续循环
→ 第 5 轮：ElementAgent 重新执行（重新截取该元素）
→ 第 6 轮：CodegenAgent 重新执行（可能不需要改代码，但按流程走）
→ 第 7 轮：VerifyAgent 重新执行 → 假设通过 → DONE
```

---

## 十一、设计决策背后的原因

### 为什么用状态机而不是 Multi-Agent 框架？

工作流本身是**确定的串行流程**——探索完才能截图，截完图才能写代码，写完代码才能跑验证。不存在"Agent A 和 Agent B 协商决定下一步做什么"这种需求。引入 LangChain/CrewAI 只会增加依赖和复杂度，而状态机的核心代码不到 500 行。

### 为什么 Agent 不捕获异常？

遵循项目 CLAUDE.md 中的规则："尽量不使用 try-catch，让错误自然暴露"。Agent 内部出了问题由 Orchestrator 统一捕获处理，这样错误现场不会被吞掉。

### 为什么不用并行执行？

探索 → 截图 → 编码 → 验证 每个阶段都**依赖**上一阶段的输出，无法并行。但蓝图留下了 Phase 2 的扩展空间：如果未来支持批量任务（如同时探索多个不相关的功能），可以在 Orchestrator 层面并行调度多组流水线。

### 为什么 TeamContext 可以序列化？

支持**断点续跑**。如果验证阶段失败，整个 TeamContext 可以序列化为 JSON 保存到磁盘，修改后重新加载从中间阶段继续。这个功能标记为 Phase 2 实现。

---

## 十二、与现有体系的关系

```
                    ┌──────────────────┐
                    │  蓝图（agent-team） │
                    │  代码驱动的状态机   │
                    │                    │
                    │  python -m         │
                    │  agent_team "任务"  │
                    └────────┬───────────┘
                             │ 调用
                             ▼
              ┌──────────────────────────┐
              │  现有模块（保持不变）      │
              │                          │
              │  utils/aw/aw_base.py     │
              │  utils/aw/business/      │
              │  utils/user.py (PPUser)  │
              │  utils/devices.py        │
              │  image/image_name_mapping│
              │  conftest.py             │
              │  tests/mumu/             │
              └──────────────────────────┘
                             │ 参考
                             ▼
              ┌──────────────────────────┐
              │  现有 Skill（保持不变）    │
              │                          │
              │  .codemaker/skills/      │
              │  aw-explorer/SKILL.md    │
              │  aw-element/SKILL.md     │
              │  aw-codegen/SKILL.md     │
              │  aw-verify/SKILL.md      │
              └──────────────────────────┘
```

- Agent **不替换** Skill，Skill 继续作为 AI 助手的参考文档
- Agent **不替换** 现有 `utils/` 模块，而是作为新的调用层覆盖其上
- Agent Team 是**新增能力**，不影响现有测试用例的执行

---

## 十三、未包含在此蓝图中的内容（Non-Goals）

蓝图的 scope 是有意收敛的，以下内容明确**不在**范围内：

| 不做的 | 原因 |
|--------|------|
| Agent 之间的自然语言对话/协商 | 流水线是确定性的，不需要多 Agent 谈判 |
| 并行 Agent 执行 | 阶段有严格前后依赖，无法并行 |
| Web UI 或可视化面板 | 保持 CLI 工具的轻量定位 |
| 修改或替换 .codemaker/skills/ | Skill 文件继续保留，Agent 是新增层 |
| 引入外部 Agent 框架（CrewAI 等） | 零外部依赖，纯 Python 标准库 + 已有模块 |

---

## 十四、未来扩展方向

蓝图标记了三个未来 Phase：

- **Phase 2**：支持从中间阶段开始执行（断点续跑）、TeamContext 持久化到磁盘
- **Phase 3**：接入 LLM 做智能决策（如自动分析失败原因并选择最优回退策略），但目前状态机 + 规则匹配已经够用

---

## 附录：相关文件索引

| 文件 | 内容 |
|------|------|
| `openspec/changes/agent-team/proposal.md` | 提案总纲：Why / What / Impact |
| `openspec/changes/agent-team/design.md` | 设计文档：决策理由、风险、架构图 |
| `openspec/changes/agent-team/tasks.md` | 84 项实现任务清单（55 项详细 + 扩展） |
| `openspec/changes/agent-team/specs/team-context/spec.md` | TeamContext / Phase / ElementInfo / VerifyResult 规格 |
| `openspec/changes/agent-team/specs/agent-base/spec.md` | BaseAgent 抽象基类规格 |
| `openspec/changes/agent-team/specs/explorer-agent/spec.md` | ExplorerAgent 规格 |
| `openspec/changes/agent-team/specs/element-agent/spec.md` | ElementAgent 规格 |
| `openspec/changes/agent-team/specs/codegen-agent/spec.md` | CodegenAgent 规格 |
| `openspec/changes/agent-team/specs/verify-agent/spec.md` | VerifyAgent 规格 |
| `openspec/changes/agent-team/specs/orchestrator/spec.md` | Orchestrator 调度器规格 |
| `openspec/changes/agent-team/specs/team-cli/spec.md` | CLI 命令行入口规格 |
