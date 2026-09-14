# Swan 知识库贡献规范（CONTRIBUTING）

> 本文件是页面/元素/断言/功能的**写法标准**。转正流程、验证门槛见 [README](README.md)。
> 目标：知识库同时服务「人读」和「机器读」（pytest 生成 + MCP 双层索引）。

## 1. 页面文档结构

所有 `pages/*.md` 必须遵循 `templates/page.md`：

- YAML frontmatter 必填：`page_id` / `name` / `route` / `status` / `last_updated` / `type`
- 正文章节固定顺序：页面概述 → 生效断言 → 进入方式 → 关键元素 → 页面布局 → 功能关联
- 旧页面（H1 + blockquote 代替 frontmatter 的）在新一轮探索时迁移，迁移时同步更新 `app_map.json`

## 2. 静态 / 动态元素判定

| 判定 | 类型 | 定位策略 |
|---|---|---|
| 内容固定（图标、固定文案、按钮形状） | 静态 | 截图 → `image_exists` / `click_image` |
| 内容随状态变化（曲目名、头像、UUID、角标、时间、在线状态） | 动态 | 无障碍键 优先；无无障碍键 用 OCR 文案锚定周边静态元素 |
| 结构固定但数据变化（列表行、卡片） | 动态 | 截图只截**行内固定部分**（如分组名），不截数据部分 |

**禁止**给 动态 元素截整块图 —— 换账号/换曲目必失配。

## 3. 生效断言写法

- 每页至少 1 条「出现」断言（进页面就该看到的稳定元素）
- 有加载态的页面补 1 条「消失」断言（loading 弹层消失 = 数据就绪）
- 断言优先级：图片断言 > 无障碍键 > OCR 文案
- 断言必须写成可执行的表达式（`image_exists(常量)` / OCR 关键词），不能只写"页面正常显示"

## 4. 进入方式写法

- 每页一张表：`来源页面 | 操作元素(locator) | 操作类型 | 到达断言`
- locator 写法：无障碍键用反引号 `` `tab_me` ``，OCR 用 `OCR"文案"`，图片用常量名 `SWAN_XXX_ROW`
- 特殊前置（需滚动/需登录/需特定账号状态）写在表格下方自然语言区

## 5. 截图规范

- 遵循 `docs/UI元素截取与裁剪规范.md`，Swan 命名为下划线三段式 `swan_{页面}_{元素}.png`
- 新图先进 `image_ai/flutter/`，以 draft=True 在 `image_name_mapping.py` 注册
- aw-verify 跑通用例后 `promote_image()` 转正到 `image/flutter/`
- 动态元素不截图，在元素表"截图"列写 `dynamic-不截图` 并在备注说明锚定方式

## 6. 功能 / 路径文档

- `digest/features/<feature_id>.md`：按功能域组织（账号体系、导航框架、收藏管理…），一个 feature 含多个页面和 flow
- `digest/flows/<flow_id>.md`：一条可自动化的端到端路径，步骤表必须能直接翻译成 `SwanBusiness` 方法调用
- flow 的 `risk: high`（充值/注销/删除设备）只断言不点击
- 新建 feature/flow 后更新 `app_map.json` 的 `feature_categories` 与 `flows` 字段

## 7. 键型标注与 dump 时序（2026-09-11 R3 修订）

- 键型标注：`bottom_player` / `tab_*` / `full_player_page` / `player_*` / `person_info_*` /
  `me_user_profile_entry` / `multiroom_sheet` / `device_*` / `wifi_device_*` 实机均为
  **resource-id**，不是 content-desc（R3 P0-2，.62 提出/.229 三方确认）。新页面一律标注
  `resource-id`；旧页面的「无障碍键」括注已在 R4 统一替换为 resource-id。
- dump 时序坑：页面转场后立即 dump 语义树常不完整，需等待 2-3s 或重试
  （nav.py 已内置 3 次重试；R3 P2-12）。dump 结果异常时先怀疑时序，再怀疑结构。

## 8. 双层索引维护

```
git commit → post-commit hook → auto_update.py
             ├─ backlinks_generator.py   （graph 层）
             └─ embedding_pipeline.py --incremental （vector 层）
```

手工重建：

```bash
set UIAUTOTEST_EMBEDDING_MODEL=E:\UIAutotest\models\paraphrase-multilingual-MiniLM-L12-v2
python scripts/knowledge/backlinks_generator.py --knowledge-dir knowledge/swan
python scripts/knowledge/embedding_pipeline.py --knowledge-dir knowledge/swan --chroma-dir knowledge/swan/.chroma_db --incremental
```
