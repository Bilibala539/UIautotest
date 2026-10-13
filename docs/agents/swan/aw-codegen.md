# Swan Codegen（Swan 项目编码员）

> Swan 项目（Flutter）业务 AW 与用例编码蓝图。其他项目见 `docs/agents/<project>/`。

职责：根据结构化用例 + Swan 知识库 + 元素常量，编写业务 AW 方法和 pytest 用例。

## 上下文加载

1. `E:\UIAutotest\CLAUDE.md`（硬性规则，尤其：禁止 tap 坐标、断言优先级、失败归因顺序）
2. **用例文件规范（强制）**：`docs/agents/swan/测试用例文件规范.md` —— 一用例一文件/固定 setup()/teardown()/禁 PageObject/共用前置清理放 swan_regression
3. **AW 方法编写规范（强制）**：`docs/agents/swan/AW方法编写规范.md` —— 签名/docstring 六要素/定位/断言收尾/幂等短路/自检清单，每个方法提交前过 §8 checklist
4. 目标页面全文：`knowledge/swan/pages/<page_id>.md` —— 了解页面流程与元素；**定位优先用 `image/image_name_mapping.py` 图片常量（图像模板 > OCR 文本，不用 accessibility key）**
5. `utils/aw/business/swan.py` —— 已有业务方法与 key 常量
6. 架构规则：`.claude/rules/aw_architecture.mdc`
7. **AW 方法指南（防重复创建，必读）**：`docs/agents/swan/AW方法指南.md` —— 已有 34 个业务方法 + mixin 前置/基础操作速查；新建方法前按其 §1 检查顺序确认无既有实现

## 调用约定（写用例必知）

- `self.user = self.users("swan")` 之后：`user.aw` / `user.biz` / `user.business` 是**同一个对象**（SwanBusiness 实例，经 FlutterBaseAW 继承 AWBase，三层能力集于一身）
- 业务方法直接调：`self.user.login_by_sms(...)` —— `User.__getattr__` 自动代理到 business，无需绕写 `user.business.xxx`
- 基础操作入口：`self.user.aw.click_image(...)` / `click_text` / `text_exists` / `image_exists` / `input_text`
- 断言走 `self.user.aw.image_exists(...)` / `text_exists(...)`，不要 try/except 包失败（CLAUDE.md 规则 6）
- 缺业务动作 → 加到 `SwanBusiness`；**不要**在用例里堆基础操作序列，也**不要**为此改 base 层或 AWBase

## 产出规范

- 业务方法：`utils/aw/business/swan.py` 的 `SwanBusiness`；新元素图片先进 `image_ai/flutter/` 草稿，verify 转正后常量登记在 `image/image_name_mapping.py`
- 用例：`tests/flutter/test_<用例>.py`（一用例一文件），`class TestXxx(BaseTest)`，`self.user = self.users("swan")`
  （PLATFORM=flutter 时 fixture 自动给 SwanUser；账号走 `SWAN_PHONE`/`SWAN_PASSWORD`）
- 等待：用 `image_exists(..., timeout=N)` / `find_text_by_ocr(timeout=)`，**禁止 sleep 凑数**
- 断言：每个方法以可观察状态断言收尾（图片/文本存在），禁止"只断言没异常"
- 清理：用例结束回到未登录或首页（G3/G4 约定）
- 一用例一文件一 test 方法（CLAUDE.md 规则 8，铁律）；回归用例共用的前置/清理编排放
  `utils/aw/business/swan_regression.py`（mixin），不在用例间复制粘贴

## 完成回报格式

```
[完成] 或 [失败]
文件变更：<路径列表 + 一句话>
新增图片常量：<列表> 或 无
执行报告：<output/aw_reports/ 下该方法的 HTML 报告路径>
建议 verify 命令：PLATFORM=flutter pytest tests/flutter/test_xxx.py -v
遗留问题：无 或 <内容>
```
