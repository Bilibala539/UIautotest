# Laya 短文本"页面状态分类" POC —— 结论文档

**分支**：`laya-aw-poc`（从 dev 切出的独立工作树 `E:\UIAutotest-laya-aw`，不 merge）
**日期**：2026-09-28
**判定**：**FAIL（未达 90% 上岗门槛，归档；不建 `laya_soft_assert.py` 原型）**

## 一、实验问题

前一 POC（`laya-poc` 分支，750 字长文档判定）证明 Laya（convaiinnovations/laya-multilingual，
choice/score/noul 三种题型）判长文档逻辑不及格，但留下一个未测的难度档：
**AW 场景下 OCR 出来的 50~200 字短文本块 → 判断"当前是哪个页面"**。
本 POC 用真机回归攒下的带页面标签的真实截图实测该场景，检验 Laya 能否当 AWBase
软断言裁判（上岗门槛：top-1 准确率 ≥90%）。

## 二、数据集（93 对样本 / 22 个页面类）

- 来源：`E:\UIAutotest\explorer_output\` 下真机回归截图（verify_run2/run3、
  verify_regression1、aw_element_tmp/{domain3,recap11,recap12,根目录 src_*、castsheet}），
  全部为 720x1612 全屏截图，PaddleOCR（`E:\UIAutotest\venv`，ch 模型，conf≥0.5）提文本，
  文本块 33~182 字（远低于 600 上限）。
- 22 个页面类：home 5 个顶 Tab（推荐/音乐/电台/可视音箱/AI）、我的、设备、平台、
  全屏播放页、歌单库、歌单详情、SWAN收藏、播放历史、设备切换弹层、音量弹层、登录页、
  授权弹层、AI角色设置、个人信息修改、基本信息修改弹窗、修改昵称、区号选择。
- **标注纪律**：标签 = 文件名 + OCR 内容模式 + 人工看图核实（12 张歧义图逐张看图定标）。
  多个文件名与实际内容不符，按**实际页面**定标，例如：
  - `verify_run2/final_home.png`、`src_home_recommend.png` → 实为首页**电台** Tab
  - `recap11/home_music.png` → 实为首页**推荐** Tab
  - `FAIL_top_推荐/音乐.png` → 实为**我的**页（tab 切换失败落点）；
    `FAIL_top_AI/电台/可视音箱.png` → 实为 **SWAN收藏**页
  - `domain3/playlist_page.png` → 实为**登录**页；`after_gedan_click.png` → 实为**歌单库**页
  - `diag_after_goto_home.png` → 实为**我的**页
- 覆盖≥6 页面、≥60 对的门槛满足（93 对 / 22 类，最大类 home_recommend 21 个，
  最小类 1 个）。

## 三、实验结果（judge：http://192.168.12.176:8089，串行，毫秒级/次）

### 主实验（任务指定的两种问法，全 22 类）

| 方法 | top-1（22 类，tab 级） | top-1（home tabs 归并为 18 类页面级） |
|---|---|---|
| Exp A：noul 逐页判断（22 问取最高分） | **25.8%** | 47.3% |
| Exp B：choice 单问（22 criteria） | **31.2%** | 35.5% |

随机基线 = 1/22 = 4.5%（22 类）/ 1/18 = 5.6%（页面级）。

**Exp A 失败形态：饱和。** 93 个样本 × 22 问全部返回 noul≈1.0（top1-top2 分差
mean=0.017、max<0.35），argmax 纯属噪声。与 laya-poc 长文档结论同根因：
noul 头做的是**粗话题匹配**——"当前界面是电台页吗"和"当前界面是我的页吗"是同一
粗话题（Swan 音乐 App 界面），全部判"是"。

**Exp B 失败形态：塌缩 + 过度自信。** 全部 22 类任由描述长短，预测塌到
home_recommend 和 me 两类（me 9/9 全对、login 4/4、collection 3/3、home_recommend
11/21，其余 18 类近乎全错）。且**置信度完全不可用**：conf≥0.9 桶 n=40 准确率仅
42.5%（错误预测同样给高置信）。典型混淆：
`home_recommend→me ×10、player→device ×8、home_radio→me ×5、platform→me ×4`
——每个页面底部都有全局播放条（含设备名 HiVi M300MKII），首页各 Tab 共享顶栏，
页面间文本大量共现，choice 头直接放弃区分。

### 抢救实验（排除"问法没设计好"的假设，33 样本子集）

| 变体 | top-1 |
|---|---|
| A choice22 + 短 criteria（"首页推荐页"式两字~五字） | 21.2% |
| B choice **k=6**（强区分小候选，旧 POC 建议的 k≤5 场景） | 36.4% |
| C noul **属性级**（"界面文字中出现了切换设备、手机蓝牙吗"，旧 POC 保留场景） | 15.2% |
| D noul 短问句（"当前界面是我的页面吗"） | 12.1% |
| E B + OCR 上下文前缀 | 36.4% |
| **S 对照：纯子串匹配基线（同一属性表，零模型成本）** | **69.7%** |

- k=6 也救不回来：即便只留 home/me/device/platform/player/login 六个强区分页，
  36.4%（随机 16.7%）。
- 属性级 noul 同样塌（margin mean=0.018）：**即使特征词确实出现在文本中**
  （如"我的权益"9/9 命中且他类零出现），noul 头也用不上——它不做词面判断。
- 二分类 sanity check（me vs device 二选一）choice 能给 0.98/0.02 的正确分离，
  说明极端小 k、强对比时头部有粗信号，但远不足以支撑页面级软断言。

### 其他落锤证据

1. **score 题型在 judge 服务端就是坏的**：`{"type":"score"}` 一律 HTTP 500
   （服务端 `TypeError: 'NoneType' object is not iterable`，judge 所装 laya 0.3.5 的
   score 头未接通）。score 路线不可用。
2. **同一份数据，确定性方法接近满分**：从各半类样本自动提取判别性文本片段做
   子串匹配，全集命中率 **97.8%**（91/93）。Laya 失败的这个任务本身是**平凡可解**
   的——框架现有的 `text_exists`（OCR + 子串/图像模板断言）就是正确工具，
   根本不需要语义裁判。

## 四、结论与败因

**Laya 不能当 AW 的"页面状态分类"软断言裁判。** 败因（与 laya-poc 长文档结论
连续、互相印证）：

1. **noul 头 = 粗话题匹配器**。短文本没有改变这一点：同一 App 的所有页面同属
   一个粗话题，逐页问"是不是 X"全部饱和于 yes。它只在"同话题 vs 跨话题"级别的
   区分上有效（旧 POC 的"天空是绿色"对照），对页内级别无区分度。
2. **choice 头在候选页共现文本下塌缩**。Swan 的全局播放条/底部导航/顶栏让页面间
   文本大量重叠，choice 无论 k=22 还是 k=6、无论 criteria 长短都塌向少数几类，
   且**错误预测伴随高置信**（校准失效），软断言需要的"低置信→降级为人审"通路
   也不成立。
3. **任务错配**：页面识别本质是"判别性文本片段是否存在"，确定性子串匹配 97.8%，
   Laya 12~36% 且慢一个量级（GPU 往返 vs 本地字符串比较）。

**给将来的启示（若再考虑语义裁判）**：需要的是能做词面/特征级判断的通道——
小 LLM（如 judge 服务形态不变换模型）、或 embedding 相似度检索（页面参考文本库 +
top-1 检索）是候选；Laya 的三个头（choice/score/noul）在"同话题短文本细分类"
这一档全部不可用。score 头在当前 judge 部署中本身就是坏的。

## 五、产物清单（本分支 `poc_aw/`）

| 文件 | 内容 |
|---|---|
| `01_ocr_extract.py` | PaddleOCR 批量提文本（93 张全屏截图 → ocr_texts.json） |
| `ocr_texts.json` | OCR 原始文本（样本级，UTF-8） |
| `labels.py` | 22 类页面定义 + 93 对（路径,标签,标注依据）+ 页面级归并表 |
| `02_run_exp.py` | 主实验（noul 逐页 / choice 单问）→ results_noul.csv / results_choice.csv / summary.json |
| `results_noul.csv` | Exp A 全部得分（93×22 分数矩阵 + 预测 + 时延） |
| `results_choice.csv` | Exp B 全部概率（93×22 + confidence + 预测 + 时延） |
| `summary.json` | 汇总指标 + 混淆对 |
| `03_sweep.py` | 抢救 sweep（短 criteria/k=6/属性 noul/前缀/子串基线） |
| `sweep_results.json` | sweep 明细 |
| `04_probe_score.py` | score 题型探针 + 自动属性子串上限（97.8%） |
| `README.md` | 本文档 |

## 六、遗留问题

1. judge 服务（.176 `laya-judge.service`）的 **score 题型 500** 未修——若日后想用
   score 头需先修服务端（本次按约束只做了 health/status/读 token，未动服务）。
2. 自动属性子串基线（97.8%）是"留半提取"的乐观估计；落成 AW 断言需人审属性表。
   若要推进"软断言"，建议方向是把 `text_exists` 断言模板化（页面特征片段表），
   而非引入语义模型——属框架层改动，须用户决策，本 POC 不越界。
3. 数据集 93 对中 player 类文本极稀（8~66 字），OCR 短文本页面天然不利；
   但这恰是真实运行面，不影响 FAIL 判定（确定性方法在同一数据上 97.8%）。
