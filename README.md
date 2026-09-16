# UIAutotest Web/Android/Flutter 自动化测试框架

基于 **pytest + Selenium WebDriver** 的 Web UI 自动化测试框架，使用图像识别（OpenCV）+ OCR（PaddleOCR）定位元素。

配备 **AI Agent 团队**自动探索 App、截取元素、生成用例，并通过**双层知识库**（Graph + Embedding）管理应用知识。

## 核心能力

- **图像识别定位**：OpenCV 模板匹配，540x960 统一分辨率
- **OCR 文字识别**：PaddleOCR，支持中文
- **平台驱动**：支持 Chrome、Edge、Firefox、Android ADB 实机与 Flutter（基于 Android ADB）
- **知识库驱动**：Graph（页面导航图谱）+ Embedding（语义检索）双层架构
- **AI Agent 团队**：explorer/element/codegen/verify/orchestrator 五角色协同
- **并行执行**：pytest-xdist 为每个 worker 创建独立浏览器会话

## 快速开始

### 环境要求
- Python 3.9+
- Chrome、Edge 或 Firefox 浏览器
- Windows 10/11

### 安装

```bash
git clone <repository-url>
cd UIAutotest
pip install -r requirements.txt
```

### 运行测试

```bash
# TidyTree Web 用例
$env:PLATFORM = "web"
pytest tests/web -v

# 全量并行
python run_parallel.py

# 指定数量
python run_parallel.py -n 2 -t 5
```

### 连接安卓实机

安卓实机通过系统 `adb` 连接，不依赖模拟器。手机开启“开发者选项”和“USB 调试”，首次连接时确认 RSA 授权，然后确认设备状态：

```powershell
adb devices
```

设备状态必须为 `device`（不是 `unauthorized` 或 `offline`）。多台设备时记录序列号，并切换平台运行：

```powershell
$env:PLATFORM = "android"
$env:ANDROID_DEVICE_SERIAL = "设备序列号"
# 如果 adb 不在 PATH：
# $env:ADB_PATH = "C:\Android\Sdk\platform-tools\adb.exe"
pytest tests/android -v
```

也可以直接修改 `.env` 中的 `PLATFORM`、`ANDROID_DEVICE_SERIAL` 和 `ADB_PATH`。无线调试设备先执行 `adb pair IP:配对端口` 和 `adb connect IP:端口`，再按上面的方式运行。Android 模式仍使用原有 `click_text`、`text_exists`、`click_image`、`input_text` 等 AW 方法，截图由 ADB 获取，OpenCV 与 PaddleOCR 逻辑不变。

### 运行 Swan Flutter 用例

Swan 是 Flutter 应用，但运行在 Android 设备中，因此复用 ADB 设备驱动和 AW 基础操作，同时隔离其用例和图片资产：

```powershell
$env:PLATFORM = "flutter"
$env:ANDROID_DEVICE_SERIAL = "设备序列号"
$env:SWAN_PHONE = "测试手机号"
$env:SWAN_PASSWORD = "测试密码"
pytest tests/flutter/test_swan_login_logout.py -v
```

测试会启动 `com.swan.network`，完成登录和登出，最终回到登录页。账号信息仅设置在本机环境变量或密钥管理系统中。

## 项目结构

```
UIAutotest/
├── conftest.py                    # pytest fixtures + 平台/用户管理
├── run_parallel.py                # 并行测试运行器
├── CLAUDE.md                      # AI Agent 项目规约（必读）
│
├── utils/
│   ├── aw/aw_base.py             # AWBase — 基础交互唯一入口
│   ├── aw/driver/web_driver.py   # Selenium 浏览器驱动适配器
│   ├── aw/driver/android_driver.py # 通用 ADB 安卓实机驱动
│   └── user.py                   # TTUser — 测试用户入口
│
├── tests/
│   ├── web/                       # TidyTree Web 用例
│   ├── android/                   # 智能音箱 Android 用例
│   └── flutter/                   # Swan Flutter 用例
│
├── image/web/                     # Web 正式元素图片
├── image/android/                 # Android 正式元素图片
├── image/flutter/                 # Flutter 正式元素图片
├── image_ai/web/                  # Web 图片草稿
├── image_ai/android/              # Android 图片草稿
├── image_ai/flutter/              # Flutter 图片草稿
├── image/image_name_mapping.py    # 平台路径与图片转正工具
│
├── explorer_output/knowledge/     # TidyTree Web 知识库（Obsidian vault）
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
└── docs/                          # 人读文档（完整索引见 docs/README.md）
    ├── UI元素截取与裁剪规范.md    # 元素截图规范
    ├── 待办与缺口清单.md          # 当前权威 plan
    ├── agents/                    # 各项目 agent 蓝图（swan/、web/）
    └── archive/                   # 已归档文档
```

## 知识库系统

采用 Graph + Embedding 双层架构，通过 MCP Server 供 agent 和人类使用：

| 层 | 用途 | 查询方式 |
|---|---|---|
| Graph（knowledge_graph） | 页面导航、反向链接、BFS 路径 | `get_navigation_path(from, to)` |
| Embedding（vector_kb） | 语义搜索、相似用例、上下文推荐 | `semantic_search("自然语言")` |

可用 Obsidian 分别打开 `explorer_output/knowledge/`（Web）或 `knowledge/android/`（Android）作为 vault；两个平台的页面和索引不混用。

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

    def test_basic_operation(self):
        self.userA.aw.click_text("登录")

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
| explorer | 连接目标平台探索页面，更新知识库 |
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

## 测试历史平台

仪表盘使用 Python 标准库和 SQLite，不需要额外的 Web 依赖。启动后可查看 Android/iOS 的执行历史、通过率、用例明细、日志、附件路径、开始/结束时间和耗时。

```powershell
# 在测试机或 Jenkins agent 上启动
python dashboard/server.py --host 0.0.0.0 --port 8080

# 浏览器访问
Start-Process http://127.0.0.1:8080

# 生成 Android/iOS 演示历史
python scripts/seed_dashboard_fake_data.py --url http://127.0.0.1:8080
```

测试执行时设置 `DASHBOARD_URL` 即可自动上报；插件会在 pytest 会话开始、每条用例完成和会话结束时分别提交数据：

```powershell
$env:DASHBOARD_URL = "http://127.0.0.1:8080"
$env:PLATFORM = "android"
pytest tests -v
```

Swan 登录/退出的视觉脚本使用语义树节点作为截图搜索区域提示，实际按钮坐标由 OpenCV 截图区域中的 PaddleOCR 结果计算；输入框和复选框使用对应 `bounds` 命中：

```powershell
$env:SWAN_PHONE = "测试手机号"
$env:SWAN_PASSWORD = "测试密码"
python scripts/swan_login_logout_opencv_ocr.py --serial "设备序列号"
```

脚本会保存过程截图到 `output/swan_vision/`，支持从已登录或已退出状态启动，最终保持退出状态。执行日志使用 50ms 追踪粒度（`--trace-interval-ms 50`），同时记录 UI 树、截图、OCR 扫描、语义 bounds 点击、OCR 点击、输入和等待阶段。录屏优先使用 Android `screenrecord`；设备不支持时自动用 ADB 截屏 + OpenCV 编码 MP4：

```powershell
python scripts/swan_login_logout_opencv_ocr.py `
  --serial "设备序列号" `
  --trace-interval-ms 50 `
  --trace-log output/swan_vision/run.log `
  --recording output/swan_vision/run.mp4
```

录屏默认 5 FPS，按真实经过时间补帧，覆盖完整执行过程；密码只用于运行时输入，不写入日志。

Linux Jenkins 节点部署时，将项目目录和虚拟环境放到节点后运行同样的 `dashboard/server.py` 命令，并在 Jenkins job 中将 `DASHBOARD_URL` 指向 `http://<节点地址>:8080`。生产环境建议使用专用低权限账户、SSH key/Jenkins Credentials，以及反向代理和访问控制。
