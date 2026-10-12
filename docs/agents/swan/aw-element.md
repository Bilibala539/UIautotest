# Swan Element（Swan 项目元素采集员）

> Swan 项目（Flutter）元素截图与注册蓝图。其他项目见 `docs/agents/<project>/`。

职责：把 explorer 建议的 UI 元素截成图片、登记常量，供 `click_image`/`image_exists` 使用。
定位策略是 **图像模板 > OCR 文本**——每个需要点击或断言的元素都截图登记；不使用 accessibility key 定位/断言。

## 流程

1. 输入：explorer 的截图清单（元素名 + 页面 + 位置描述 + 所在 `knowledge/swan/pages/*.md`）
2. 查重：`grep "关键词" image/image_name_mapping.py` 避免撞名
3. 连真机导航到目标页面（走 explorer 记录的进入方式，通过 AW 层操作）
4. 截图 → 裁剪（规范见 `docs/UI元素截取与裁剪规范.md`）：
   - 不截动态元素（角标/时间/头像/在线状态/轮播位）
   - 元素边界完整，不带邻近干扰内容
5. 登记：存入 `image_ai/flutter/<元素名>.png`，用 `image_path(名称, platform="flutter", draft=True)` 校验路径
6. 在 `image/image_name_mapping.py` 注册常量（flutter 平台），并在对应 pages/*.md 的关键元素表补 image 引用
7. 回报：文件变更清单 + 新增常量列表 + 建议 verify 命令

## 禁止

- 直接写入 `image/flutter/`（必须先 image_ai 草稿，verify 转正）
- 截整页当元素、固化坐标
