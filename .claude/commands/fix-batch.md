---
name: fix-batch
description: |
  批量修复失败用例编排。基于 pytest 失败输出与本地 HTML 日志分析失败聚类，按根因优先级排序，
  逐个用例走 fix-failed 流程修复。先修高 ROI 的（一修多过），再修独立的。
  2026-10-14 按 Swan 口径改写（路径/文字用例来源/真机独占）；原 mumu/checklist/模拟器时代版本见 git 历史。
---

# fix-batch：批量失败用例修复编排（Swan 口径）

> 输入：pytest 失败输出或本地 HTML 日志路径
> 产出：修复后的代码 + 重跑验证报告

## 触发方式

以下任何表述都触发此编排：

```
/fix-batch <pytest失败输出或日志路径>
/fix-batch latest                  # 自动取 output/logs/ 下最新日志
"启动修复失败用例流程"
"修复失败用例"
"修一下这批失败的"
"跑挂了，帮我修"
"fix 这些用例"
单个用例名（如 "修一下 test_xxx"）  # 退化为单用例模式
```

**输入兼容**：
- pytest 失败输出或 HTML 日志路径 → 批量模式（读取所有失败用例）
- 单个用例路径/名字 → 单用例模式（Phase 0 退化为单组单用例）
- "latest" → 自动取 `E:\UIAutotest\output\logs\` 下最新日志

---

## 编排总览

```
Session 失败报告
  │
  ▼
Phase 0: 失败聚类分析（orchestrator 自行完成）
  │  读 pytest 失败输出与本地日志 → 按根因分组 → 按影响面排优先级
  │  产出：修复计划（优先级队列）
  │
  ▼
Phase 1: 逐组修复（循环，按优先级从高到低）
  │
  │  ┌─────────────────────────────────────────────┐
  │  │  对每个失败组：                               │
  │  │    Step 1: aw-verify 采样诊断（取组内 1-2 个） │
  │  │    Step 2: 按根因分派修复 agent               │
  │  │    Step 3: aw-verify 批量验证（跑组内全部）    │
  │  │    Step 4: 更新修复计划状态                   │
  │  └─────────────────────────────────────────────┘
  │
  ▼
Phase 2: 汇总报告
  产出：修复前后对比 + 剩余未修复清单 + 建议
```

---

## Phase 0: 失败聚类分析

orchestrator 读取 pytest 失败输出与本地 HTML 日志，按以下维度对失败用例进行聚类：

### 聚类规则

```python
# 优先级从高到低（先修影响面最大的）
clusters = {
    "C1-共享前置": [],   # 多个用例共用同一个 AW 方法/前置步骤失败（如登录/进首页）
    "C2-页面导航": [],   # 进入目标页面失败（同一入口路径出错）
    "C3-元素定位": [],   # 图片匹配或 OCR 识别失败（同一元素）
    "C4-操作逻辑": [],   # AW 方法内部逻辑错误
    "C5-测试数据": [],   # 测试文件/数据缺失或不匹配
    "C6-环境偶发": [],   # 超时/弹窗遮挡等环境问题
}
```

### 聚类判断依据

| 特征 | 归入 | 修复策略 |
|------|------|---------|
| 多个用例同一个 `file` 前缀，且失败 duration 短（<5s） | C1-共享前置 | 修复公共 setup/导航方法（swan_regression mixin） |
| 失败日志含 "未找到文字 'xxx'" 且 xxx 是页面标题/导航文字 | C2-页面导航 | 修复导航路径或知识库 |
| 失败日志含 "未找到图片" + 同一图片路径出现多次 | C3-元素定位 | 重新截图或调整匹配阈值 |
| 单个用例独立失败，不属于上述 pattern | C4-操作逻辑 | 逐个修复 AW 方法 |
| 用例名含文件/数据操作，失败日志含"文件"/"格式" | C5-测试数据 | 修复测试数据准备 |
| duration 异常长，或仅偶发失败（第二次跑可能通过） | C6-环境偶发 | 增加重试/等待逻辑 |

### 产出格式

```markdown
## 修复计划

| 优先级 | 组 | 根因 | 影响用例数 | 修复 Agent | 代表用例 |
|--------|---|------|-----------|-----------|---------|
| P0 | C1-登录四件套 | 登录 setup 失败级联 | 12 | aw-codegen | test_密码登录成功 |
| P1 | C2-设备卡导航 | 点设备卡进入错误页面 | 6 | aw-codegen | test_设备卡进播放页 |
| P2 | C3-播放按钮 | 播放/暂停图标模板失配 | 4 | aw-element + aw-codegen | test_播放暂停切换 |
| P3 | C5-歌单数据 | 歌单为空前置未建 | 2 | aw-codegen | test_歌单添加歌曲 |
| P4 | C4-独立逻辑 | 各自不同 | ~8 | 按个分析 | - |
```

---

## Phase 0.5: 共性根因分析（orchestrator 自行完成，不派 agent）

> **目的**：修之前先找共性，同一 AW 方法导致多个失败时一次修好全部，不逐个修。

### Step 1：提取 AW 方法

从每个失败用例的 traceback 中提取最后调用的 `utils/aw/business/swan.py` 方法：

```
示例 traceback：
  tests/flutter/test_设备卡进播放页.py:42 in test_设备卡进播放页
  utils/aw/business/swan.py:885 in open_device_card    ← 提取这行
```

### Step 2：按方法分组

```
open_device_card → test_设备卡进播放页, test_设备卡信息核对（2个）← 疑似共性
login_by_password → test_密码登录, test_验证码登录, test_登出（3个）← 疑似共性
tap_play_btn → test_播放暂停切换（1个）← 独立，不是共性
```

### Step 3：二次验证（防误归类）

方法名相同 ≠ 同一根因。以下 **2 项均一致** 才确认为共性：

| 验证项 | 比对方式 | 一致判定 |
|--------|---------|---------|
| 异常消息核心内容 | 提取 error message 中的元素名/图片名/OCR文字 | 指向同一个元素或图片 |
| 失败栈帧行号 | swan.py 内部失败的行号 | 同一行或 ±3 行以内 |

### Step 4：交叉比对通过用例

对每个疑似共性方法，检查是否有 PASS 用例也调用了它：

```bash
grep -rl "open_device_card" E:/UIAutotest/tests/flutter/
```

| 比对结果 | 修复方向 |
|---------|---------|
| 有 PASS 用例调用同方法且成功 | 方法本身没问题，对比成功 vs 失败用例的调用差异（参数/前置页面/传入值） |
| 所有调用该方法的用例全部失败 | 方法本身有 bug，直接修方法 |
| 没有 PASS 用例调用该方法 | 走 Phase 1 Step 1（aw-verify 诊断） |

### Step 5：输出修复优先级队列

在原有 C1-C6 聚类基础上，共性问题排最前：

```markdown
## 修复计划（含共性分析结果）

| 优先级 | 类型 | 根因 | 影响用例数 | 修复方向 |
|--------|------|------|-----------|---------|
| P0-共性 | 共性 AW 方法 | open_device_card 元素定位失败 | 3 | 直接修方法 |
| P1-共性 | 共性 AW 方法 | login_by_password 匹配逻辑 | 2 | 对比成功用例调用差异 |
| P2-独立 | C4-操作逻辑 | test_播放暂停切换 各自不同 | 1 | 逐个分析 |
```

**每轮 fix 后重新执行 Phase 0 + Phase 0.5**——剩余失败用例变化后，聚类（C1-C6）和共性模式都可能变了，不能沿用上轮结论。

---

## Phase 1: 逐个修复（按优先级队列依次处理）

对修复计划中的用例，按优先级从高到低逐个处理：

### 单用例处理流程

```
orchestrator 取队列中下一个待修复用例
  │
  ├─ Step 0: 🔴 代码-用例一致性校验（必须，不可跳过）
  │    读取用例代码 + 对应的文字用例（来源见下方）
  │    对比：代码实现的操作步骤 vs 文字用例的操作步骤和预期结果
  │    │
  │    ├─ 一致 → 进入 Step 1（正常修复流程）
  │    └─ 不一致 → 走"删除重建"分支：
  │         ① 删除当前用例文件
  │         ② 进入 convert-cases 模式，用文字用例驱动重新生成
  │         ③ 生成后由 aw-verify 验证
  │         ④ 完成，处理下一个
  │
  ├─ Step 1: aw-verify 诊断
  │    输入：用例路径 + session 日志
  │    产出：失败分类 + 根因 + 建议回退 agent
  │
  ├─ Step 2: 按根因分派修复（路由表见下方）
  │    ├─ 元素变化 → aw-element 重新截图
  │    ├─ 逻辑错误 → aw-codegen 修复代码
  │    └─ 页面变化 → aw-explorer 重新探索
  │
  ├─ Step 3: aw-verify 重跑验证
  │    ├─ 通过 → commit fix，继续下一个
  │    └─ 失败 → 回 Step 1，最多 3 轮
  │
  └─ Step 4: 检查是否有"同组附带修复"
       修完一个用例后，如果修改的是公共方法（如 open_device_card），
       orchestrator 检查同组其他用例是否可能被附带修复：
       - 快速跑同组用例验证
       - 通过的直接从队列移除，标记"附带修复"
       - 仍失败的保留在队列中等待单独处理
```

### 🔴 Step 0 详细规则：代码-用例一致性校验

> **原则：代码必须忠实反映文字用例的意图。偏差了就别修，直接重写。**

#### 文字用例来源（按优先级查找）

1. 用例文件头的 `# LINKED-CASE:` 标记（如 `# LINKED-CASE: REG-015,REG-016`）与 `# CASE-ID:` 标记
2. **平台 case_defs**（工作站/测试平台 API 或页面）按编号查文字用例全文——文字用例权威源在平台（CLAUDE.md 用例域纪律，2026-10-13）
3. 用例文件顶部的 docstring / 注释中引用的原始需求
4. 若找不到原始文字用例 → 标记为"无文字用例基准"，跳过此步，直接进入 Step 1

#### 校验维度

| 维度 | 对比内容 | 判定不一致的标准 |
|------|---------|----------------|
| 操作对象 | 代码操作的是哪个页面/元素 vs 文字用例描述的目标 | 操作了错误的页面或元素 |
| 操作步骤 | 代码的步骤顺序和动作 vs 文字用例的操作步骤 | 步骤缺失、多余或顺序错误 |
| 验证断言 | 代码 assert 的内容 vs 文字用例的预期结果 | 断言了错误的内容，或遗漏关键断言 |
| 前置条件 | 代码 setup 做的事 vs 文字用例的前置条件 | 前置条件未满足或不匹配 |

#### 判定结果及处理

```
校验结果
  ├─ ✅ 一致：代码逻辑正确反映了文字用例 → 正常修复（Step 1）
  ├─ ⚠️ 轻微偏差：步骤基本对但有小细节差异 → 正常修复，修复时顺带对齐
  └─ ❌ 明显不一致：操作对象错误 / 步骤严重偏离 / 断言与预期不符
       → 删除重建：
         1. 删除用例文件：rm tests/flutter/test_<用例>.py
         2. git commit -m "remove: test_<用例>（代码与文字用例不一致，需重建）"
         3. 切换到 convert-cases 模式
         4. 输入原始文字用例，由 aw-codegen 重新生成
         5. aw-verify 验证新生成的用例
         6. 通过 → commit feat，处理下一个
```

#### 示例：一致 vs 不一致

**一致**（应修复）：
```
文字用例：登录成功 → 点击设备卡 → 验证进入播放页
代码逻辑：login_by_password() → open_device_card() → assert 播放页元素存在
问题：open_device_card 方法内部匹配逻辑有 bug
结论：代码意图正确，方法实现有 bug → 修复方法
```

**不一致**（应删除重建）：
```
文字用例：点击设备卡播放按钮 → 验证歌曲开始播放且进度条走动
代码逻辑：进入播放页 → 验证播放页元素存在（只看了不操作）
结论：代码没有执行"播放"动作，也没验证"进度条走动" → 与文字用例意图偏离 → 删除重建
```


### 修复分派路由表

| verify 诊断 | 修复 Agent | 任务描述模板 |
|------------|-----------|-------------|
| 导航路径错误（点击进入了错误目标） | aw-codegen | 修复 `open_device_card()` 或相关导航方法，增加精确匹配和验证 |
| 图片匹配失败（元素变化/截图过时） | aw-element | 重新截取目标元素并注册 |
| OCR 识别失败（文字在但认不出） | aw-codegen | 改用 `click_image` 或调整 OCR 参数 |
| AW 方法逻辑有误 | aw-codegen | 修复具体方法，附上正确的操作序列 |
| 测试数据不匹配 | aw-codegen | 修复数据准备逻辑或验证断言 |
| 环境/timing 问题 | aw-codegen | 增加 wait/retry 或弹窗处理 |
| 页面改版（知识库过时） | aw-explorer | 重新探索目标页面，更新知识库 |

#### 修复范围约束

- **修的是根因，不是症状**：如果多个用例因同一方法失败，修那个方法，然后验证所有受影响用例
- **附带修复机制**：修完一个用例的公共方法后，快速跑同组其他用例，通过的直接从队列移除
- **Git checkpoint**：每个用例修复前 `git add -A && git commit -m "checkpoint: pre-fix [用例名]"`
- **框架层改动须用户决策**：`utils/aw/driver/*`、`conftest.py`、`run_parallel.py` — 若诊断发现是框架层问题，报告给用户，由用户决定是否改、如何改
- **禁止坐标回退**：`click_image` 失败时不允许加 `tap(x,y)` fallback，必须走图片质量排查

### 验证与推进

修复完成后，aw-verify 跑当前用例：

```bash
PLATFORM=flutter pytest tests/flutter/test_<用例>.py -v
```

验证结果：
- **通过** → 先检查是否修改了公共 AW 方法，再决定是否做基线回归：

  **如果本轮 aw-verify 修改了 `utils/aw/business/swan.py`**，在 commit 前执行基线回归：

  ```bash
  # 1. 找出依赖被修改方法的测试文件（用 sed 正确截取函数名）
  CHANGED_METHOD=$(git diff HEAD utils/aw/business/swan.py | grep "^+def \|^-def " | awk '{print $2}' | sed 's/(.*//')
  AFFECTED=$(grep -rl "$CHANGED_METHOD" E:/UIAutotest/tests/flutter/ 2>/dev/null | grep "\.py$")

  # 2. 若有受影响文件，清空临时文件，暂存修改，跑基线
  rm -f /tmp/uiat_baseline.txt /tmp/uiat_after.txt
  git stash
  for f in $AFFECTED; do
    PLATFORM=flutter pytest "$f" -v --tb=line 2>&1 | grep -E "PASSED|FAILED" >> /tmp/uiat_baseline.txt
  done

  # 3. 恢复修改，跑修复后版本
  git stash pop
  for f in $AFFECTED; do
    PLATFORM=flutter pytest "$f" -v --tb=line 2>&1 | grep -E "PASSED|FAILED" >> /tmp/uiat_after.txt
  done

  # 4. 对比：统计真实回归（baseline PASS → after FAIL）和附带修好（baseline FAIL → after PASS）
  REGRESSION=$(comm -23 \
    <(grep "PASSED" /tmp/uiat_baseline.txt | awk '{print $1}' | sort) \
    <(grep "PASSED" /tmp/uiat_after.txt   | awk '{print $1}' | sort) \
    | wc -l)
  BONUS=$(comm -13 \
    <(grep "PASSED" /tmp/uiat_baseline.txt | awk '{print $1}' | sort) \
    <(grep "PASSED" /tmp/uiat_after.txt   | awk '{print $1}' | sort) \
    | wc -l)
  echo "真实回归: $REGRESSION，附带修好: $BONUS"
  ```

  对比判决：

  | 条件 | 动作 |
  |------|------|
  | `$REGRESSION -gt 0` 且 `$REGRESSION -gt $BONUS` | 净负回归 → `git checkout -- .`，放弃，交人工 |
  | `$REGRESSION -gt 0` 且 `$REGRESSION -le $BONUS` | 有回归但附带修好更多 → 保留，commit 时注明 |
  | `$REGRESSION -eq 0` | 无真实回归 → 安全，继续 commit |

  **如果未修改 swan.py**，直接 commit：

  ```bash
  git commit -m "fix: [用例名] [根因简述]"
  ```

  - 然后检查同组其他用例（附带修复检查）
- **失败** → 回退 `git reset --hard HEAD`，进入下一轮诊断（最多 3 轮）
- **3 轮仍失败** → 标记为"需人工介入"，跳过，处理下一个

---

## Phase 2: 汇总报告

所有组处理完后，orchestrator 生成最终报告：

```markdown
# 批量修复报告

## 概览
- 输入：session 20261014_093000（77 用例，21 失败）
- 修复前通过率：72.7%
- 修复后通过率：XX%
- 本次修复用例数：XX
- 剩余未修复：XX

## 修复明细

| 组 | 修复内容 | 改动文件 | 修复前 | 修复后 |
|----|---------|---------|--------|--------|
| P0-登录四件套 | login_by_password 精确匹配 | swan.py:L2998 | 0/12 | 12/12 |
| P1-设备卡导航 | open_device_card 增加重试 | swan.py:L885 | 0/6 | 6/6 |
| ... | ... | ... | ... | ... |

## 未修复用例及原因

| 用例 | 原因 | 建议 |
|------|------|------|
| test_xxx | 需要 App 版本更新配合 | 等待下个版本 |
| test_yyy | 需要人工确认预期结果 | 升级给用户 |

## 代码变更汇总
- `utils/aw/business/swan.py` — 修复登录匹配、设备卡导航
- `image_ai/flutter/xxx.png` — 重新截取的元素
- ...
```

---

## 并行策略

- Phase 0（聚类分析）：orchestrator 独立完成，不派 agent
- Phase 1 各组之间：**串行**执行——同一台真机**任何时刻只跑一个真机任务**（pytest/agent 探索/补截图互斥，2026-10-12 实测并行必互相切 App 假失败，见 CLAUDE.md 运行时经验）
- Phase 1 组内诊断+修复：**串行**（诊断结果决定修复方案）
- 若有多台真机：不同优先级组可分配到不同 `ANDROID_DEVICE_SERIAL` 并行

---

## 退出条件

以下情况 orchestrator 停止修复循环，交给用户：

1. 同一组连续 3 轮修复仍全部失败
2. 根因判定为 "App 功能变更 / 需求变更"（不是代码 bug）
3. 根因判定为 "conftest / 框架层问题"（需要架构调整）
4. 剩余失败用例互不相关且各自独立（ROI 过低，逐个修不划算）

---

## 与其他模式的关系

- **fix-batch 是唯一的修复模式**，取代了原 fix-failed
- 单个用例失败时，Phase 0 退化为单组单用例，流程不变
- Step 0 校验不通过时，自动切换到 **convert-cases** 模式重新生成用例
- 修复过程中发现知识库过时，按需触发 **enrich-kb** 子流程
- 编排视角（模式判断/门禁）见 `docs/agents/swan/aw-orchestrator.md` 模式三
