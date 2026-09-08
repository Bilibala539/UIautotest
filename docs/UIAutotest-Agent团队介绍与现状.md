# UIAutotest Agent 团队介绍与现状

> 面向对象：参与 TidyTree 自动化测试、知识库维护或 AI 协作的同事  
> 更新时间：2026-09-07

## 一句话说明

UIAutotest 计划将 UI 自动化测试拆分为一支由 Claude Code 驱动的 AI 团队：协调者负责拆解和调度，其他角色分别负责页面探索、元素处理、代码生成、测试验证和规格维护。

这不是一个独立运行的 Python 多智能体服务，而是一套以 `.claude/agents/*.md` 为角色蓝图、由 Claude Code 在会话中按需实例化的协作规范。

## 团队结构

```text
需求 / 文字用例 / 失败日志
             │
             ▼
  aw-orchestrator（主会话，负责调度）
     ├── aw-explorer     探索页面、维护知识库
     ├── aw-element      定位与管理 UI 元素素材
     ├── aw-codegen      生成测试代码
     ├── aw-verify       执行测试、诊断和验证
     └── spec-keeper     维护规格与变更记录
```

| 角色 | 核心职责 | 主要交付物 |
| --- | --- | --- |
| `aw-orchestrator` | 判断需求类型、拆分任务、注入上下文、跟踪进度、汇总结果 | 调度计划、最终交付报告 |
| `aw-explorer` | 探索页面和导航路径，记录可复用的页面事实 | `knowledge/**/pages/*.md`、`app_map.json` |
| `aw-element` | 截取并校验稳定的 UI 元素素材 | `image_ai/<platform>/`、图片映射 |
| `aw-codegen` | 基于知识库和已有能力生成 AW 封装及 pytest 用例 | `utils/`、`tests/` |
| `aw-verify` | 运行 pytest，定位失败根因，验证素材和测试结果 | pytest 输出、失败归因、转正记录 |
| `spec-keeper` | 用 OpenSpec 管理需求、设计、任务和归档 | `openspec/changes/`、`openspec/specs/` |

其中，`explorer` 与 `spec-keeper` 设计为长驻协作者，适合连续积累上下文；`element`、`codegen`、`verify` 设计为一次性子 Agent，每次任务使用干净上下文。

## 三类业务流程

### 1. 文字用例转自动化（`convert-cases`）

适用于“覆盖某功能”“把 Excel/文字用例转成自动化”等需求。

```text
文字用例
  → 检查知识库是否已有目标页面
  → explorer 补齐页面与导航事实（如需要）
  → element 准备稳定元素素材（如需要）
  → codegen 生成业务封装和 pytest 用例
  → verify 实际运行并给出结果
```

在代码生成前，协调者需检查：目标页面已记录、目标元素已准备、测试数据可清理、清理后可回到首页，以及相似场景是否应合并为参数化用例。

### 2. 知识库丰富与巡检（`enrich-kb`）

适用于“探索某页面”“页面改版了”“检查知识库是否准确”等需求。

- 新页面：先由 `explorer` 写入 `draft/`，再审核和实测，最后转正为 `pages/`。
- 页面更新：以旧记录为基准做差异核对，并评估对导航、元素和下游用例的影响。
- 跨页面功能：补充功能摘要、操作流和页面关系。
- 知识库巡检：按页面逐一验证导航路径、页面签名和关键元素，再输出通过、部分异常和失败清单。

### 3. 批量修复失败用例（`fix-batch`）

适用于“测试失败了”“修复这批红色用例”等需求。

```text
失败日志
  → 按共享前置、导航、元素定位、操作逻辑、测试数据、环境偶发聚类
  → verify 复现并判定根因
  → element / codegen / explorer 按根因修复
  → verify 重跑
  → 汇总通过率、改动和遗留问题
```

原则是先修影响多个用例的公共根因；图片匹配失败先检查素材质量，不应直接以坐标点击作为回退方案。

## 共同约束

- 测试交互统一经由 `AWBase` 和平台 Driver；不应在业务用例中绕过该抽象层。
- 新素材先进草稿目录，验证通过后再转正，避免未验证图片污染正式资产。
- 测试必须有可验证断言，不能用吞异常或“未报错”代替验证。
- 测试中产生的群组、消息、状态修改等痕迹应具备清理逻辑。
- 新增或修改知识库后，应同步页面文档、图谱索引与向量索引。
- 调度者只负责协调，代码、探索、截图和测试分别交给专职角色完成。

## 知识库与工具支撑

项目为 Agent 提供两层知识检索能力：

| 层级 | 作用 | 当前入口 |
| --- | --- | --- |
| Graph | 精确查询页面、关联关系和最短导航路径 | `mcp_servers/knowledge_graph/server.py` |
| Embedding | 语义检索相关页面、相似用例和经验 | `mcp_servers/vector_kb/server.py` |

Web 与 Android 知识库分开维护，避免将浏览器 DOM 定位器、Android 设备信息或坐标混用：

- Web：`explorer_output/knowledge/`
- Android：`knowledge/android/`

当前 Web 知识库已有“登录页”和只读“Agents 列表”两个已验证页面；Android 知识库完成了目录与规则初始化，尚未录入已验证页面。

## 当前状态与注意事项

项目目前正在从旧的 POPO/MuMu Android 自动化工程迁移到 TidyTree Web，并补充 Android ADB 支持。因此，团队蓝图的设计方向和仓库实际结构尚未完全同步：

| 项目项 | 当前情况 |
| --- | --- |
| Web 测试基础 | 已有 Selenium、`AWBase`、Web Driver、pytest fixture 和 Web 知识库 |
| Android 测试基础 | 已有 ADB Driver 和独立知识库骨架，但没有已验证页面或完整用例 |
| 图谱 MCP | 可用，可查询现有页面及 `login_page → agents_page` 路径 |
| 向量 MCP | 当前不可用：缺少 `chromadb`、`sentence-transformers` 依赖及向量索引目录 |
| Agent 蓝图 | 大量内容仍引用旧 POPO、MuMu、`mumu.py`、`utils/devices.py` 和旧 AW 文档；这些资产在当前工程中已不存在 |
| OpenSpec | 蓝图预期使用，但当前仓库未初始化 `openspec/` |

此外，当前工作区存在大量未提交的迁移改动。旧蓝图中的自动提交、`git reset --hard` 等流程在迁移完成前不应直接启用，以免覆盖同事正在进行的工作。

## 给同事的使用建议

在当前状态下，可把这套 Agent 团队理解为“已经完成角色设计、等待适配现有项目的协作框架”。建议按以下顺序推进：

1. 先完成现有 TidyTree Web 测试、知识库和目录的稳定化。
2. 将 6 个 Agent 蓝图迁移到 Web/Android 的真实入口、文件路径、定位策略和清理规则。
3. 安装向量检索依赖并构建索引，使协调者能够按任务注入相关上下文。
4. 初始化 OpenSpec，或从蓝图中移除暂时不用的 OpenSpec 流程。
5. 清理并提交当前迁移改动后，再启用 `/bootstrap-team` 进行团队装配和 smoke test。

在适配完成前，建议将 Agent 用于文档梳理、知识库补充和代码审阅；涉及真实 UI 探索、生成测试或执行修复时，应先核对蓝图中引用的路径和运行环境。

## 参考位置

- 角色蓝图：`.claude/agents/`
- 团队接入说明：`.claude/README.md`
- 编排设计：`docs/编排流程详细设计.md`
- 全局约束：`CLAUDE.md`
- 图谱 MCP：`mcp_servers/knowledge_graph/server.py`
- 向量 MCP：`mcp_servers/vector_kb/server.py`
- Web 知识库：`explorer_output/knowledge/`
- Android 知识库：`knowledge/android/`
