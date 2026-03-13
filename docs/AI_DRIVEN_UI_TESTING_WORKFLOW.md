# AI驱动的UI自动化测试工作流

## 概述

本文档描述了一套完整的AI辅助UI自动化测试方法论，包含三个核心阶段：

1. **AI自主探索** - 自动探索应用UI，记录操作与响应
2. **构建导航树** - 将探索结果结构化为树形数据
3. **生成测试用例** - 基于导航树自动生成测试脚本

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI驱动的UI自动化测试                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐              │
│   │ AI自主探索 │ ──▶ │ 构建导航树 │ ──▶ │ 生成测试  │              │
│   └──────────┘     └──────────┘     │   用例    │              │
│        │                │           └──────────┘              │
│        ▼                ▼                │                    │
│   ┌──────────┐     ┌──────────┐         ▼                    │
│   │ 截图+坐标  │     │ JSON配置  │     ┌──────────┐            │
│   │ 映射关系   │     │ 路径数据  │     │ pytest   │            │
│   └──────────┘     └──────────┘     │ 测试脚本  │            │
│                                      └──────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 阶段一：AI自主探索

### 1.1 探索目标

让AI像人类测试员一样自主操作应用，通过：
- 截图分析页面元素
- 点击/滑动等操作
- 对比操作前后的页面变化
- 记录并解释每个操作的含义

### 1.2 探索流程

```
截图(Before) → 识别可点击区域 → 执行点击 → 截图(After) → 对比分析 → 记录映射
     ↑                                                              ↓
     └────────────────────── 循环探索 ←───────────────────────────────┘
```

### 1.3 探索实践

#### 初始探索（广度优先）

从主页面开始，探索所有一级入口：

```python
# 探索底部导航栏
探索步骤:
1. 截图当前页面（消息页面）
2. 点击"日历"Tab → 截图 → 记录：页面切换到日历视图
3. 点击"工作台"Tab → 截图 → 记录：页面切换到工作台
4. 点击"通讯录"Tab → 截图 → 记录：页面切换到通讯录
5. 点击"更多"Tab → 截图 → 记录：弹出底部面板（非页面切换）
```

#### 深度探索（深度优先）

选定一个功能，深入探索完整流程：

```python
# 深度探索"创建群组"功能
探索步骤:
1. 消息页面 → 点击添加按钮(+)
   └── 记录：弹出功能菜单
2. 菜单 → 点击"创建群组"
   └── 记录：进入"添加群成员"页面
3. 添加群成员 → 选择联系人 → 点击确定
   └── 记录：可能出现"选择已有群组"分支
4. 点击"创建新的群组"
   └── 记录：群组创建成功，进入群聊页面
5. 群聊页面 → 点击群名称
   └── 记录：进入群设置页面
6. 继续探索群设置的各个选项...
```

### 1.4 探索输出

每次探索生成：

| 输出物 | 说明 |
|--------|------|
| 截图序列 | `explore_01_xxx.png`, `explore_02_xxx.png`... |
| 操作坐标 | 每个点击位置的(x, y)坐标 |
| 页面变化 | 操作前后的对比结果 |
| 映射关系 | 操作→结果的对应关系 |

示例输出：
```
[探索1] 点击: 日历Tab (162, 900)
   → 页面切换: 消息页面 → 日历视图
   → 特征: 日期选择器 + 时间轴

[探索2] 点击: 添加按钮(+) (490, 70)
   → 交互类型: 下拉菜单
   → 菜单选项: 添加联系人、创建群组、发起会议...
```

---

## 阶段二：构建导航树

### 2.1 数据结构设计

将探索结果结构化为JSON配置，采用"路径"表示法：

```json
{
  "pages": {
    "消息页面": {"signature": "顶部消息标题+底部导航消息高亮"},
    "日历页面": {"signature": "日期选择器+时间轴"},
    "群设置页面": {"signature": "设置标题+群信息+群成员"}
  },
  
  "paths": {
    "日历页面": [
      {"tap": [162, 900], "desc": "点击日历Tab", "wait": 1}
    ],
    "创建群组": [
      {"tap": [490, 70], "desc": "点击添加按钮", "wait": 0.5},
      {"tap": [378, 303], "desc": "点击创建群组", "wait": 1.5}
    ],
    "退出登录": [
      {"tap": [47, 72], "desc": "点击用户头像", "wait": 1},
      {"tap": [118, 620], "desc": "点击设置", "wait": 1},
      {"swipe": [270, 700, 270, 300], "desc": "向上滑动", "wait": 0.5},
      {"tap": [270, 850], "desc": "点击退出登录", "wait": 1}
    ]
  }
}
```

### 2.2 树形结构可视化

```
桌面
└── 网易POPO
    └── 消息页面
        ├── 底部导航栏
        │   ├── 消息Tab
        │   ├── 日历Tab → 日历页面 → 新建日程
        │   ├── 工作台Tab → 工作台页面
        │   ├── 通讯录Tab → 通讯录页面
        │   └── 更多Tab → 更多应用弹窗
        │
        ├── 顶部操作区
        │   ├── 用户头像 → 侧边栏 → 设置 → 退出登录
        │   ├── 搜索按钮 → 全局搜索页面
        │   └── 添加按钮 → 功能菜单
        │       ├── 添加联系人
        │       ├── 创建群组 → 添加群成员 → 群聊页面
        │       ├── 发起会议
        │       └── 扫一扫
        │
        └── 消息列表
            └── 会话项 → 聊天详情页 → 群设置
```

### 2.3 路径查找

给定目标，反推完整操作路径：

```python
# 输入: "退出登录"
# 输出:
路径: 消息页面 → 侧边栏 → 设置 → 退出登录

步骤1: 点击用户头像 (47, 72)
步骤2: 点击设置 (118, 620)
步骤3: 向上滑动
步骤4: 点击退出登录 (270, 850)
```

### 2.4 配置文件位置

```
E:\UIAutotest\
├── config/
│   └── nav_paths.json      # 导航路径配置
├── utils/
│   └── navigator.py        # 导航器实现
└── explorer_output/
    ├── screenshots/         # 探索截图
    └── EXPLORATION_REPORT.md  # 探索报告
```

---

## 阶段三：生成测试用例

### 3.1 用例生成原则

基于rules.mdc规范：

| 规则 | 说明 |
|------|------|
| 一个用例一个文件 | 每个测试场景独立成文件 |
| 固定方法名 | 必须有`setup()`和`teardown()` |
| 禁止Page模式 | 不使用Page Object，直接调用用户方法 |
| 用户实例化位置 | setup中登录，teardown中退登 |

### 3.2 用例模板

```python
"""
测试用例: XXX功能测试
"""
from time import sleep
import pytest

from image.image_name_mapping import *


class TestXXX:
    """XXX功能测试类"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_xxx_scenario(self):
        """
        测试场景: 描述

        步骤:
        1. xxx
        2. xxx
        
        预期结果: xxx
        """
        # 使用OCR/图像识别定位，避免硬编码坐标
        self.userA.aw.click_text("目标文字")
        self.userA.aw.click_image(IMAGE_TEMPLATE, dx=100)
        
        # 断言（find_text_by_ocr找不到会自动assert False）
        self.userA.aw.find_text_by_ocr("预期文字", timeout=5)

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        self.userA.logout()
```

### 3.3 定位策略优先级

```python
# 优先级1: 直接OCR文字定位
self.userA.aw.click_text("创建群组")

# 优先级2: OCR文字 + 偏移量
self.userA.aw.click_text("会话", dy=180)  # 定位后向下偏移

# 优先级3: 图像识别 + 偏移量
self.userA.aw.click_image(MESSAGE_TAB_MSG_TEXT, dx=400)

# 最后选择: 硬编码坐标（仅用于滑动等特殊操作）
self.userA.aw.swipe(270, 800, 270, 300)
```

### 3.4 断言方式

```python
# ✅ 正确：断言元素"存在"
# find_text_by_ocr 找不到会自动 assert False
self.userA.aw.find_text_by_ocr("1234", timeout=5)

# ✅ 正确：检查后继续（不中断）
if self.userA.aw.text_exists("选择已有群组", timeout=2):
    self.userA.aw.click_text("创建新的群组")

# ❌ 错误：不要用于断言"不存在"
# pos = self.userA.aw.find_text_by_ocr("xxx")  # 找不到直接中断
# assert pos is None  # 永远执行不到
```

### 3.5 完整用例示例

```python
"""
测试用例: 创建群组并设置群公告
"""
from time import sleep
import pytest
from image.image_name_mapping import MESSAGE_TAB_MSG_TEXT


class TestCreateGroupAndSetAnnouncement:
    """测试创建群组并设置群公告功能"""

    def setup(self):
        self.userA = self.users("userA")
        self.userA.login()

    def test_create_group_and_set_announcement(self):
        """
        测试场景: 创建群组并设置群公告为"1234"
        """
        # 步骤1: 点击添加按钮
        self.userA.aw.click_image(MESSAGE_TAB_MSG_TEXT, dx=400)
        sleep(1)

        # 步骤2: 点击创建群组
        self.userA.aw.click_text("创建群组")
        sleep(1.5)

        # 步骤3: 选择联系人
        self.userA.aw.click_text("会话", dy=180)
        sleep(0.5)
        self.userA.aw.click_text("会话", dy=280)
        sleep(0.5)

        # 步骤4: 点击确定
        self.userA.aw.click_text("确定")
        sleep(2)

        # 步骤5: 处理分支（如果出现）
        if self.userA.aw.text_exists("选择已有群组", timeout=2):
            self.userA.aw.click_text("创建新的群组")
            sleep(2)

        # 步骤6-9: 设置群公告
        self.userA.aw.click_text("名群成员", dy=-30)
        sleep(1.5)
        self.userA.aw.click_text("群公告")
        sleep(1.5)
        self.userA.aw.click_text("输入群公告内容")
        self.userA.aw.input_text("1234")
        sleep(1)
        self.userA.aw.click_text("群公告", dx=200)
        sleep(1)
        self.userA.aw.click_text("发送到群聊")
        sleep(2)

        # 步骤10: 断言
        self.userA.aw.find_text_by_ocr("1234", timeout=5)
        print("✅ 群公告设置成功")

        # 步骤11: 退出群组（业务流程）
        self.userA.aw.swipe(270, 800, 270, 300)
        sleep(0.5)
        self.userA.aw.click_text("退出群组")
        sleep(1)
        self.userA.aw.click_text("转让并退出")
        sleep(1)
        self.userA.aw.click_text("转让群主", dy=150)
        sleep(1)
        self.userA.aw.click_text("确定")
        sleep(2)

    def teardown(self):
        self.userA.logout()
```

---

## 工具与脚本

### 核心文件

| 文件 | 用途 |
|------|------|
| `utils/ai_explorer.py` | AI自主探索器 |
| `utils/navigator.py` | 导航器（路径查找+脚本生成） |
| `config/nav_paths.json` | 导航路径配置 |
| `utils/aw/aw_base.py` | 基础操作（tap/click_text/find_image） |
| `utils/aw/aw_business.py` | 业务操作（login/logout） |

### 常用命令

```bash
# 列出所有可用导航目标
python -c "from utils.navigator import list_targets; list_targets()"

# 查找到达目标的路径
python -c "from utils.navigator import find_path; find_path('退出登录')"

# 运行测试用例
pytest tests/test_create_group_announcement.py -v
```

---

## 最佳实践

### 探索阶段

1. **先广度后深度** - 先探索所有一级入口，再选择重点功能深入
2. **记录截图** - 每步操作前后都截图，方便回溯
3. **标注坐标** - 记录每个可点击元素的坐标
4. **识别分支** - 注意条件分支（如弹窗、已有数据等）

### 构建阶段

1. **数据代码分离** - 路径数据存JSON，代码负责逻辑
2. **使用页面签名** - 定义每个页面的识别特征
3. **支持路径组合** - 复杂流程可由多个简单路径组合

### 用例阶段

1. **优先OCR定位** - 减少硬编码坐标，提高稳定性
2. **合理使用偏移** - `dx`/`dy`参数可精确调整点击位置
3. **业务逻辑完整** - 退群、清理等操作放在用例方法中
4. **不用try-catch** - 让错误暴露，不隐藏bug

---

## 总结

这套方法论将UI自动化测试分为三个清晰的阶段：

```
探索 → 建模 → 生成
```

通过AI的视觉能力进行自主探索，将结果结构化为可维护的导航树，最终基于规范生成高质量的测试用例。这种方式大大降低了UI自动化测试的编写成本，同时保持了代码的可读性和可维护性。
