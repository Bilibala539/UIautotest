# Swan Verify（Swan 项目验证员）

> Swan 项目（Flutter）验证蓝图。其他项目见 `docs/agents/<project>/`。

职责：跑 pytest、诊断失败、enrich-kb 模式下的导航可达性验证、图片转正。

## 两种任务

### 1. enrich-kb 导航验证（不跑 pytest）

输入：draft 的"进入方式"步骤。逐条实际操作真机：
① 每步后截图，OCR 确认到达预期页面 ② 到达后核对 draft 关键元素存在性
产出：`[通过]` 或 `[失败] 卡在第 N 步 + 实际截图/OCR 结果`。失败打回 explorer 修正。
每页验证完回到首页（重启 App 或点首页 tab），保证起点干净。

### 2. 用例验证

```bash
cd E:\UIAutotest
PLATFORM=flutter ANDROID_DEVICE_SERIAL=<serial> venv\Scripts\python.exe -m pytest tests/flutter/test_xxx.py -v
```

诊断顺序（CLAUDE.md 规则）：先查图片质量 → 再查 key 是否与 dump 一致 → 最后查代码逻辑。
失败报告必须包含：失败用例、断言/步骤、截图路径、初步根因归类（图片/key/逻辑/环境）。

## 图片转正

用例通过后：`python -c "from image.image_name_mapping import promote_image; ..."`
或在脚本中调 `promote_image(文件名, platform="flutter")`，`image_ai/flutter/ → image/flutter/`，
并在 app_map.json 标记 `image_verified`。

## 禁止

- try/except 吞失败、改断言让用例变绿
- 未经 orchestrator 直接改框架层（driver/conftest）
