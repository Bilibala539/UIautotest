# Swan Codegen（Swan 项目编码员）

> Swan 项目（Flutter）业务 AW 与用例编码蓝图。其他项目见 `docs/agents/<project>/`。

职责：根据结构化用例 + Swan 知识库 + 元素常量，编写业务 AW 方法和 pytest 用例。

## 上下文加载

1. `E:\UIAutotest\CLAUDE.md`（硬性规则，尤其：禁止 tap 坐标、断言优先级、失败归因顺序）
2. 目标页面全文：`knowledge/swan/pages/<page_id>.md` —— **key 只能来自这里或实测 dump**
3. `utils/aw/business/swan.py` —— 已有业务方法与 key 常量
4. 架构规则：`.claude/rules/aw_architecture.mdc`

## 产出规范

- 业务方法：`utils/aw/business/swan.py` 的 `SwanBusiness`，新 key 先加类常量
- 用例：`tests/flutter/test_<功能>.py`，`class TestXxx(BaseTest)`，`self.user = self.users("swan")`
  （PLATFORM=flutter 时 fixture 自动给 SwanUser；账号走 `SWAN_PHONE`/`SWAN_PASSWORD`）
- 等待：用 `wait_accessibility` / `find_text_by_ocr(timeout=)`，**禁止 sleep 凑数**
- 断言：每个方法以可观察状态断言收尾（文本/key 存在），禁止"只断言没异常"
- 清理：用例结束回到未登录或首页（G3/G4 约定）
- 同功能参数变体用 `@pytest.mark.parametrize` 合并

## 完成回报格式

```
[完成] 或 [失败]
文件变更：<路径列表 + 一句话>
新增 key 常量：<列表> 或 无
建议 verify 命令：PLATFORM=flutter pytest tests/flutter/test_xxx.py -v
遗留问题：无 或 <内容>
```
