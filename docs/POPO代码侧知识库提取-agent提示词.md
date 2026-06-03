# POPO 代码侧知识库提取 — Agent 提示词

> 用途：在 POPO 工程代码所在的机器上，启动一个 AI agent，让它**纯粹基于 POPO 源码**生成一份"页面 - 元素 - 操作 - 功能"骨架知识库，作为 UIAutotest 项目知识库的**结构层底料**。
>
> 真机数据（截图、坐标、OCR 偏移）由 UIAutotest 项目的 explorer agent 后续在真机上补充。
>
> **使用方式**：
> 1. 把本文件第二节"agent 启动提示词"整体复制
> 2. 在 POPO 工程根目录下启动一个 Claude Code（或同等能力的 coding agent）
> 3. 把提示词作为第一条消息发过去
> 4. agent 会先做试点（5 个页面），通过验收后再跑全量
> 5. 跑完后，把工程根目录下产生的 `_popo_kb_extract/` 整个目录打包传到 UIAutotest 这边

---

## 一、整体设计要点（背景知识）

### 目标产物

每个用户能看到的页面（Activity / Fragment / Dialog / BottomSheet 等）一份 markdown，
结构如下：

```yaml
---
page_id: group_settings
name: 群设置页
page_type: activity              # activity / fragment / dialog / bottom_sheet / popup
class_name: com.netease.popo.group.GroupSettingsActivity
file_path: app/src/main/java/com/netease/popo/group/GroupSettingsActivity.kt
status: from_code                # from_code / verified（真机校准后改成 verified）
generated_at: 2026-06-03
confidence: high                 # 整页综合置信度
---

# 群设置页

## 进入途径

| 来源页面 | 触发动作 | 代码引用 |
|---------|---------|---------|
| [[聊天页(P2P-群聊)]] | 点击右上角"更多"按钮 | ChatActivity.kt:412 |
| [[群组列表页]] | 点击群项卡片 | GroupListFragment.kt:88 |
| deep link | popo://group/settings?gid={gid} | DeepLinkHandler.kt:55 |

## 页面前置条件

- 当前会话 `chat.isGroup == true`
- 当前用户已登录且是群成员

## 元素清单

### 修改群名称
- **元素类型**: 文本+箭头行
- **可见条件**: `is_group_owner == true` (GroupSettingsActivity.kt:201)
- **交互**: 点击 → 弹出输入框 → 输入新名 → 保存
- **完成功能**: 修改群名称
- **接口调用**: `groupApi.modifyName(gid, newName)` (GroupSettingsActivity.kt:215)
- **跳转**: 同页内对话框，无新页面
- **confidence**: high
- **confidence_reason**: 单一 if，handler 内直接调用接口

### 群机器人入口
- **元素类型**: 文本+箭头行
- **可见条件**:
  - `FlagsManager.isEnabled("group_robot_v2")` (GroupSettingsActivity.kt:178)
  - `is_group_owner == true`
  - `group.size >= 100`
- **交互**: 点击 → 跳转新页面
- **完成功能**: 进入群机器人管理
- **跳转**: [[群机器人页]] (startActivity GroupRobotActivity.kt)
- **confidence**: medium
- **confidence_reason**: 多重条件叠加，运行时未必触发；需测试账号配合
- **真机校准提示**: 用群主账号 + 拉够 100 人 + 申请灰度

### 删除群组
- **元素类型**: 红色文本行
- **可见条件**: `is_group_owner == true` (GroupSettingsActivity.kt:240)
- **交互**: 点击 → 二次确认弹窗 → 确认 → 解散
- **完成功能**: 解散群组
- **接口调用**: `groupApi.dismiss(gid)` (GroupSettingsActivity.kt:255)
- **跳转**: 解散后回退到 [[消息列表页]]
- **confidence**: high

## 已知动态内容

- 群成员头像横条：内容由 `groupMemberAdapter` 决定，单个头像无固定 id
- 公告区域：当群无公告时不显示该区域 (GroupSettingsActivity.kt:310)

## 待真机校准的疑点

- "群机器人入口"在测试机上是否能触发，需配合灰度名单
- "群公告"区域的高度是否随内容变化，影响下方元素坐标
```

### 切分阶段

整个流程切成 4 个阶段，每阶段独立产出可校验的中间产物：

```
Stage 1: 实体扫描（机械活）
  → entities_raw.jsonl    （所有 Activity/Fragment/Dialog 类清单）

Stage 2: 跳转图 + layout 抽取（机械活）
  → edges.jsonl           （类 A startActivity 类 B 这种调用关系）
  → elements_raw.jsonl    （每个页面对应的 layout 里的 view 列表）

Stage 3: 语义归类（LLM 活，每次只问一个实体，禁止跨实体推理）
  → page_<id>.draft.json  （每个页面一份结构化判定）

Stage 4: 合并产出（机械活）
  → pages/*.md            （最终骨架 markdown）
  → pending_review.md     （所有 confidence=low 的疑点清单）
  → SUMMARY.md            （这次跑了多少页面、各置信度分布、警告）
```

### 三级置信度

| 级别 | 含义 | 标注规则 |
|------|------|---------|
| high | 代码直接证明 | 单一 if 守卫；handler 直接调接口；明确 startActivity |
| medium | 代码暗示但不充分 | 多条件叠加；handler 调中间方法没看到接口；跨文件追踪 |
| low | 仅靠命名/位置猜测 | 类名像 Dialog 但找不到 show 调用；layout 里有 view 但找不到 listener |

**全程禁止幻觉**：每条字段必须有 `code_ref: 文件:行号`，找不到就标 `confidence: low` + 注明"未找到代码依据"。

---

## 二、agent 启动提示词

> 把以下内容**整体复制**给那台机器上的 agent。

```text
你是 POPO 安卓工程的代码侧知识库提取 agent。任务：从 POPO 源码中提取所有
"用户能看到的页面 + 该页面的元素 + 元素的交互/跳转/功能" 信息，生成一份结构
化骨架知识库。这份知识库会被另一个项目（UIAutotest）的真机探索 agent 接手，
继续补充截图、坐标这些运行时数据。

================================================================
【硬性纪律】（违反任何一条都视为本次任务失败）
================================================================

1. 严禁幻觉。每一条结论必须有 code_ref: 文件:行号 引用。
   找不到代码依据时，写 confidence: low 并注明"未找到代码依据"。
   绝对禁止凭命名推断后写成 confidence: high。

2. 中文输出。所有 markdown 内容、注释、日志全部中文。

3. 单实体推理。Stage 3 调 LLM 时，每次只把一个实体的信息塞进 prompt，
   禁止跨实体合并推理（防止幻觉）。

4. 必须先试点。完成 Stage 1-2 全量后，Stage 3 先随机挑 5 个 Activity 跑
   一遍，把 5 份 page_*.draft.json + 5 份 pages/*.md 单独输出到
   _popo_kb_extract/_pilot/ 目录下，并停下来等待人工验收。
   验收通过的信号是用户回复"通过"或"continue"。
   未拿到这个信号就跑全量 = 任务失败。

5. 不修改 POPO 工程代码。所有产物只写到 _popo_kb_extract/ 目录下。

================================================================
【目标产物结构】
================================================================

工程根目录/
└── _popo_kb_extract/
    ├── _pilot/                              ← 试点阶段输出
    │   ├── pages/                           ← 5 份 markdown
    │   └── drafts/                          ← 5 份 page_*.draft.json
    │
    ├── stage1_entities_raw.jsonl            ← 实体扫描原始结果
    ├── stage2_edges.jsonl                   ← 跳转关系
    ├── stage2_elements_raw.jsonl            ← 每个页面的 view 清单
    ├── stage3_classified/                   ← LLM 归类后的结构化判定
    │   └── page_<id>.draft.json
    │
    ├── pages/                               ← 最终 markdown（全量）
    │   ├── 群设置页.md
    │   ├── 聊天页.md
    │   └── ...
    │
    ├── pending_review.md                    ← 所有 confidence=low 的疑点
    ├── SUMMARY.md                           ← 总结报告
    └── RUN_LOG.md                           ← 跑这次的日志和遇到的问题

================================================================
【执行流程】
================================================================

────────────────────────
Step 0: 工程探明
────────────────────────

先用 5-10 分钟探明 POPO 工程形态。回答以下问题写到 _popo_kb_extract/RUN_LOG.md：

  - 主语言：Java / Kotlin / 混合（统计 .java 和 .kt 文件数）
  - UI 形态：传统 xml layout / Jetpack Compose / 混合
  - 模块结构：单 module 还是多 module？主 module 的源码根在哪？
  - Activity 总数（grep "extends Activity\|extends AppCompatActivity\|: AppCompatActivity\|: Activity"）
  - Fragment 总数
  - layout xml 总数（如果用 xml）
  - Compose 函数数量（如果用 Compose，grep "@Composable"）
  - 是否使用 Hilt / Dagger / koin（影响依赖注入分析）
  - 是否有 .aar / .jar 第三方组件无源码？标出来，这部分会作为黑盒处理

把这些信息写到 RUN_LOG.md 第一节，然后再继续。

────────────────────────
Step 1: 实体扫描
────────────────────────

扫源码，输出 stage1_entities_raw.jsonl，每行一条记录：

  {
    "class_name": "com.netease.popo.group.GroupSettingsActivity",
    "kind": "activity",                  // activity / fragment / dialog / bottom_sheet / dialog_fragment / popup_window / compose_screen
    "file_path": "app/src/main/java/...",
    "parent_class": "AppCompatActivity",
    "layout_xml": "res/layout/activity_group_settings.xml",  // 没有就 null
    "compose_root": "GroupSettingsScreen",                    // 用 Compose 才有
    "package": "com.netease.popo.group"
  }

识别规则：
  - Activity：继承 Activity / AppCompatActivity / FragmentActivity
  - Fragment：继承 Fragment / DialogFragment / BottomSheetDialogFragment
  - Dialog：继承 Dialog / AlertDialog 子类
  - BottomSheet：继承 BottomSheetDialog / BottomSheetDialogFragment
  - PopupWindow：直接调用 PopupWindow 构造的位置
  - Compose Screen：@Composable 函数中包含 Scaffold / Surface 作为根

注意：
  - 排除 abstract / sealed 基类（这些不是真实页面）
  - 排除明显的 base class（命名以 Base / Abstract / Common 开头）
  - 排除测试代码（path 含 /test/ 或 /androidTest/）

────────────────────────
Step 2: 跳转图 + layout / Compose 元素抽取
────────────────────────

2a. 跳转关系 → stage2_edges.jsonl

对 Stage 1 输出的每个实体，扫描其代码体内的：
  - startActivity(Intent(this, XxxActivity::class.java))
  - startActivityForResult(...)
  - Navigation.findNavController().navigate(R.id.xxx)
  - DialogFragment.show(...)
  - BottomSheetDialog().show()
  - PopupWindow.showAsDropDown(...)
  - 显式 finish()（用于"完成后回到上一页"的边）

每条边记录：
  {
    "from": "ChatActivity",
    "to": "GroupSettingsActivity",
    "trigger_method": "onMoreClick",
    "trigger_widget": "btn_more",         // 如果能从 setOnClickListener 关联到 view
    "code_ref": "ChatActivity.kt:412",
    "edge_kind": "startActivity"          // startActivity / show_dialog / navigate / finish
  }

2b. layout 元素抽取 → stage2_elements_raw.jsonl

  传统 xml 工程：
    - 解析 res/layout/*.xml
    - 抽出每个有 @+id/xxx 的 view，记录：id, type (Button/TextView/ImageView/...), text 属性 (静态文案), tag, parent layout
    - 记录 <include layout="@layout/xxx" />（合并到主 layout）
    - 记录 <merge> / <ViewStub>（标记为延迟加载）
    - 找代码里 findViewById(R.id.xxx) / view binding 中对该 id 的引用
    - 找该 id 上挂的 setOnClickListener / setOnLongClickListener
    - 把 listener 实现体里的代码引用一起记录（用于 Stage 3 推断"点了之后干什么"）

  Compose 工程：
    - 在 Stage 1 找到的 @Composable Screen 函数体内
    - 抽 Button / IconButton / Text / TextField / Card 这类调用
    - 记录每个调用的 onClick lambda 起止行号
    - 记录可能影响显示的 if 包裹（这是 visibility 条件）
    - 记录 LazyColumn / LazyRow 这类列表容器（标记为动态内容）

每条元素记录：
  {
    "page_class": "GroupSettingsActivity",
    "element_id": "btn_modify_group_name",      // xml 工程是 R.id 名，Compose 是 lambda 内部上下文 + 行号
    "view_type": "TextView",
    "static_text": "修改群名称",                 // android:text 或 Compose 里的字面量
    "click_handler_ref": "GroupSettingsActivity.kt:201-220",
    "visibility_guards": [                       // 包裹该 view 的 if 条件
      {"condition": "is_group_owner == true", "code_ref": "GroupSettingsActivity.kt:198"}
    ],
    "is_dynamic_content": false,                 // RecyclerView item / LazyColumn item 标 true
    "code_ref": "activity_group_settings.xml:42"
  }

────────────────────────
Step 3: LLM 语义归类（核心）
────────────────────────

【试点先跑 5 个】
随机挑 5 个 Activity（不要 Fragment / Dialog，先用最简单的 Activity 试），
对每一个跑完 Stage 3 + Stage 4，输出到 _popo_kb_extract/_pilot/ 下。
然后停下来发消息：

  "试点完成，5 份 markdown 在 _pilot/pages/ 下，请人工验收。
   通过请回复 continue，需要调整请告诉我哪里要改。"

等到回复才继续跑全量。

【对每个实体调一次 LLM】

输入给 LLM 的 prompt（这是给 LLM 的，不是给你）：

  ```
  你是 Android 代码分析助手。下面是一个页面实体的所有静态信息。
  请输出一份结构化判定（JSON），描述这个页面的元素和交互。

  规则：
  1. 不要幻觉。每个字段必须能在我提供的代码里找到依据，并附 code_ref。
  2. 找不到依据写 "confidence": "low" + "confidence_reason": "未找到代码依据"。
  3. 不要跨实体推理。我只给你这一个实体的信息，不要假设别处的代码长什么样。

  实体信息：
    类名: {class_name}
    类型: {kind}
    文件: {file_path}
    layout: {layout_xml or compose_root}

    layout 元素清单：
      {elements_raw 中匹配该 page_class 的所有元素，原文 JSON 列出}

    跳转关系（出边）：
      {edges 中 from=该类的所有边}

    跳转关系（入边）：
      {edges 中 to=该类的所有边}

    类源码摘录（前后各贴 50 行 click handler 代码体）：
      {代码摘录}

  请输出 JSON：

  {
    "is_user_facing_page": true/false,
    "page_id_suggestion": "group_settings",     // 蛇形小写英文
    "page_name_zh": "群设置页",                  // 中文名
    "page_type": "activity/fragment/dialog/bottom_sheet/popup",
    "page_confidence": "high/medium/low",
    "page_confidence_reason": "...",

    "entry_points": [                            // 进入途径
      {
        "from_page": "ChatActivity",
        "trigger": "点击右上角更多按钮",
        "code_ref": "ChatActivity.kt:412",
        "confidence": "high"
      }
    ],

    "page_preconditions": [                      // 进入该页面的业务前置
      {"condition": "chat.isGroup == true", "code_ref": "...", "confidence": "high"}
    ],

    "elements": [
      {
        "name_zh": "修改群名称",
        "element_type": "文本行",
        "visibility_conditions": [
          {"condition": "is_group_owner == true", "code_ref": "GroupSettingsActivity.kt:201", "confidence": "high"}
        ],
        "interactions": [
          {
            "action": "点击",
            "effect_summary": "弹出输入框→输入新名→保存→修改群名称",
            "api_calls": [
              {"api": "groupApi.modifyName", "code_ref": "GroupSettingsActivity.kt:215"}
            ],
            "navigation": null,
            "confidence": "high"
          }
        ]
      }
    ],

    "dynamic_content_warnings": [                // 动态内容提示
      {"area": "群成员头像横条", "reason": "由 adapter 装载", "code_ref": "..."}
    ],

    "review_hints": [                            // 给真机校准 agent 的提示
      "群机器人入口在测试机上是否能触发，需配合灰度"
    ]
  }
  ```

把这个 JSON 存到 stage3_classified/page_<page_id>.draft.json。

【降本提示】
对置信度极高的"明显是页面"的实体（比如继承 Activity 且有 layout），
LLM 调用其实可以用更小的模型；对模糊的（继承 Fragment 且 layout 复用）
用更强的模型。但**不要为了省钱跳过任何实体**。

────────────────────────
Step 4: 合并产出
────────────────────────

4a. 对每个 page_<id>.draft.json 渲染成本文件第一节"目标产物结构"展示的
    markdown 格式，写到 _popo_kb_extract/pages/。

    - 文件名用中文 page_name_zh，例如 "群设置页.md"
    - 跳转目标用 [[page_name_zh]] 双向链接格式（与 UIAutotest 项目知识库一致）
    - 所有字段都附 code_ref

4b. 收集所有 confidence: low 的字段，写到 pending_review.md：

    | 页面 | 字段 | 内容 | 理由 | code_ref |
    |------|------|------|------|---------|
    | 群设置页 | element/群机器人入口/visibility | flag=group_robot_v2 | 跨文件追踪未完成 | ... |

4c. 写 SUMMARY.md：

    - 总实体数 / 判定为 user_facing_page 的数量 / 排除的数量
    - 各 page_type 分布
    - 各 confidence 分布（high/medium/low 各多少）
    - 跳转图统计：节点数、边数、孤立节点（没有入边的页面）
    - 警告区：使用了 .aar 黑盒、Compose 比例过高、动态化 patch 等

4d. 写 RUN_LOG.md 终篇：

    - 整个流程花了多长时间
    - 各阶段产物条目数
    - 遇到的问题和绕路（比如某个文件解析失败、某种 layout 标签没识别到）

================================================================
【与上游知识库的对齐约定】
================================================================

下游 UIAutotest 项目知识库的 pages/*.md 用以下惯例，本次产物必须对齐：

- 文件名：中文页面名，例如 "群设置页.md"
- 跳转链接：[[页面中文名]]
- frontmatter 必须有 page_id（蛇形英文）、name（中文）
- 元素表格列顺序：元素 → 类型 → 可见条件 → 交互 → 跳转/接口 → confidence

================================================================
【交付前自检（不可跳过）】
================================================================

跑完全量后，做以下自检并把结果写到 SUMMARY.md 末尾：

1. 每个 pages/*.md 的所有字段是否都有 code_ref？随机抽 10 份目检。
2. confidence: low 的字段比例是否 < 30%？高于 30% 说明 LLM 归类层 prompt
   有问题，需要回头调。
3. SUMMARY.md 提到的"孤立节点"（没有入边的页面）是否合理？
   登录页 / 启动页 / 通过 deep link 进入的页可以是孤立节点；
   其余孤立节点提示 Stage 2 跳转抽取漏了，需要复查。
4. pending_review.md 是否按"页面 → 字段"排序，方便真机校准 agent 顺序处理？

================================================================
【开始执行】
================================================================

请按 Step 0 → Step 1 → Step 2 → Step 3（试点 5 个 → 等验收 → 全量）→ Step 4
的顺序推进。每个 Step 完成时主动汇报：

  "Step <n> 完成，产物：<文件清单>，下一步：<下一步动作>"

试点阶段必须停下等验收信号，没有信号就不能跑全量。

现在开始 Step 0：探明工程形态。
```

---

## 三、产物落到 UIAutotest 工程后的衔接

那边 agent 把 `_popo_kb_extract/` 打包传过来后，UIAutotest 这边的处理流程：

1. 解压到 `explorer_output/knowledge/from_code/`
2. 跑一个 diff 脚本（**待写**）：
   - 对比 `from_code/pages/` vs 现有 `explorer_output/knowledge/pages/`
   - 输出 `diff_report.md`：哪些页面是新发现的、哪些字段不一致、哪些现有 pages 在代码里查无此页（可能已下线）
3. 由 orchestrator 派 explorer 按 `pending_review.md` 优先级真机校准
4. 校准完一份就走现有的 `promote_knowledge.py` 流程进 `pages/`

---

## 四、第一次跑试点时你要看什么

5 份 markdown 出来后，挑 1-2 份你最熟悉的页面（比如群设置页、消息列表页），按这几条标尺看：

- [ ] **进入途径**齐不齐（你自己知道的入口都列出来了吗？漏了就说明 Stage 2 跳转扫描有遗漏）
- [ ] **元素清单**和你印象中页面元素能对上吗？数量大致对吗？
- [ ] **可见条件**有没有标到你知道的"群主才能看见 / 灰度才能看见"这种？
- [ ] **confidence 分布**：high / medium / low 各占多少？low 太多说明 LLM prompt 有问题
- [ ] **code_ref**：随机抽几条点开源码看看，行号对得上吗？
- [ ] **跳转目标**：用 `[[页面中文名]]` 链到的另一个页面，那个页面也在 pages/ 里有吗？

任何一条不通过都告诉对面 agent 调，**别让它跑全量**——全量跑完再返工成本太高。
