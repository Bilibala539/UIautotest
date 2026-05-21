# UIAutotest — 网易 POPO Android UI 自动化测试框架

基于 **pytest + MuMu 模拟器 + ADB** 的安卓 UI 自动化测试框架，使用图像识别（OpenCV）+ OCR（PaddleOCR）定位元素。

配备 **AI Agent 团队**自动探索 App、截取元素、生成用例，并通过**双层知识库**（Graph + Embedding）管理应用知识。

## 核心能力

- **图像识别定位**：OpenCV 模板匹配，540x960 统一分辨率
- **OCR 文字识别**：PaddleOCR，支持中文
- **MuMu 模拟器**：原生 ADB 控制，支持多实例并行
- **知识库驱动**：Graph（页面导航图谱）+ Embedding（语义检索）双层架构
- **AI Agent 团队**：explorer/element/codegen/verify/orchestrator 五角色协同
- **并行执行**：多 MuMu 实例分片跑测试，效率提升 3x

## 快速开始

### 环境要求
- Python 3.9+
- 网易 MuMu 模拟器 12
- Windows 10/11

### 安装

```bash
git clone <repository-url>
cd UIAutotest
pip install -r requirements.txt
```

### 运行测试

```bash
# 单文件
pytest tests/mumu/checklist/test_发送P2P消息.py -v

# 全量并行（3个MuMu实例）
python run_parallel.py

# 指定数量
python run_parallel.py -n 2 -t 5
```

## 项目结构

```
UIAutotest/
├── conftest.py                    # pytest fixtures + 设备/用户管理
├── run_parallel.py                # 并行测试运行器
├── CLAUDE.md                      # AI Agent 项目规约（必读）
│
├── utils/
│   ├── aw/aw_base.py             # AWBase — 设备交互唯一入口
│   ├── aw/business/mumu.py       # 业务 AW 方法层
│   └── user.py                   # PPUser — 测试用例便捷方法
│
├── tests/mumu/
│   ├── checklist/                 # 主力用例（按功能分文件）
│   ├── add/                       # 新增用例（待合并）
│   └── workhub/                   # WorkHub 专项
│
├── image/                         # 正式元素图片（验证通过后）
├── image_ai/                      # 暂存元素图片（新截的）
├── image/image_name_mapping.py    # 图片常量注册表
│
├── explorer_output/knowledge/     # App 知识库（Obsidian vault）
│   ├── app_map.json              # 导航图谱（页面+路径+type）
│   ├── pages/                    # 页面文档（含[[双向链接]]）
│   ├── draft/                    # 草稿区（验证前）
│   ├── digest/                   # 功能摘要 + 跨页面索引
│   └── backlinks.json            # 反向链接索引（自动生成）
│
├── mcp_servers/                   # MCP Server（知识库查询服务）
│   ├── knowledge_graph/          # 图谱层：导航路径/反向链接/搜索
│   └── vector_kb/                # 语义层：embedding 相似度检索
│
├── scripts/knowledge/             # 知识库维护脚本
│   ├── backlinks_generator.py    # 反向链接生成
│   ├── embedding_pipeline.py     # 向量索引构建
│   ├── promote_knowledge.py      # 草稿转正
│   └── auto_update.py            # 自动更新（git hook 触发）
│
├── .mcp.json                      # MCP Server 注册配置
├── .chroma_db/                    # 向量数据库（本地，不入 git）
│
├── .claude/agents/                # AI Agent 团队配置
│   ├── aw-orchestrator.md        # 总协调
│   ├── aw-explorer.md            # App 探索员
│   ├── aw-element.md             # 元素截图员
│   ├── aw-codegen.md             # 代码生成员
│   └── aw-verify.md              # 验证员
│
└── docs/                          # 人读文档
    ├── AW方法总结与复用指南.md
    ├── UI元素截取与裁剪规范.md
    ├── 并行测试执行指南.md
    └── 编排流程与失败处理.md
```

## 知识库系统

采用 Graph + Embedding 双层架构，通过 MCP Server 供 agent 和人类使用：

| 层 | 用途 | 查询方式 |
|---|---|---|
| Graph（knowledge_graph） | 页面导航、反向链接、BFS 路径 | `get_navigation_path(from, to)` |
| Embedding（vector_kb） | 语义搜索、相似用例、上下文推荐 | `semantic_search("自然语言")` |

可用 Obsidian 打开 `explorer_output/knowledge/` 作为 vault 查看交互式图谱（`Ctrl+G`）。

### 知识更新流程

```
explorer 探索 → draft/*.md → promote 验证 → pages/*.md → git commit → 自动重建索引
```

## 编写测试用例

```python
from conftest import BaseTest

class TestExample(BaseTest):
    def setup(self):
        self.userA = self.users("userA")

    def test_send_message(self):
        self.userA.send_message(recipient="wangying43", message="测试消息", isback=True)

    def teardown(self):
        pass
```

### 关键规则
- 元素定位用 `click_image` / `click_text`，禁止 `tap(x, y)`
- 断言优先级：图片断言 > OCR 文字断言
- 新元素先进 `image_ai/`，验证通过后转正到 `image/`
- 写新 AW 前必查 `docs/AW方法总结与复用指南.md`

## AI Agent 团队

| Agent | 职责 |
|---|---|
| orchestrator | 拆解需求、调度、汇总 |
| explorer | 连接模拟器探索 App 页面，更新知识库 |
| element | 从截图中截取 UI 元素并注册 |
| codegen | 写业务 AW + pytest 用例 |
| verify | 跑测试、诊断失败、转正图片和知识 |

一键拉起团队：在 Claude Code 中使用 `/bootstrap-team`

## 并行测试

```bash
python run_parallel.py          # 3 实例全量
python run_parallel.py -n 2     # 2 实例
```

账号自动映射，避免多设备登录互踢。详见 `docs/并行测试执行指南.md`。

## License

MIT
