# TidyTree Android 知识库

本目录记录 TidyTree Android App 的已验证页面、状态、导航路径、定位器和可复用测试上下文。它与 Web 知识库 `explorer_output/knowledge/` 完全分开，不能把 Web 路由、DOM 定位器或浏览器 viewport 当作 Android 事实使用。

## 当前状态

- 状态：已初始化，尚未录入已验证页面。
- 目标平台：Android 真机或模拟器，通过 ADB 驱动。
- 页面事实：必须由 Android 探索或测试实际验证后写入 `pages/`。
- 包名、Activity、设备序列号、账号和业务数据：未填写时保持空值，禁止猜测或写入凭据。

## 目录结构

```text
android/
├── app_map.json            # Android 页面、状态、转场和功能索引
├── audit_state.json        # 页面实测审计状态
├── backlinks.json          # 由页面 wikilink 生成的反向链接
├── graph_view.md           # 导航图概览
├── pages/                  # 已验证页面（正式知识）
├── draft/                  # 探索草稿，验证后再转入 pages/
├── digest/                 # 平台摘要和跨页面流程
└── templates/              # 页面和流程录入模板
```

## Android 录入规范

1. 每个页面使用稳定的 `page_id`，建议使用 `android_` 前缀，例如 `android_home_page`。
2. 页面类型使用 `screen`、`dialog`、`bottom_sheet`、`system_popup` 或 `route_state`，并记录进入前置条件、操作、成功断言和副作用。
3. 定位器优先级：`resource-id` > accessibility/content-desc > 可见文本 > 稳定的 class/resource 组合 > 图像/OCR。动态 UUID、坐标和设备相关像素只能作为探索证据，不能作为长期断言。
4. 记录设备上下文：Android 版本、屏幕尺寸、density、横竖屏、应用包名和 Activity。不同设备导致的差异写在页面的“设备差异”章节。
5. 写入、删除、导入、同步、权限和外部连接必须使用可清理的测试数据，并记录清理步骤；只读页面可标记 `side_effect: read_only`。
6. 账号密码、token、会话 ID、真实用户数据和生产业务数据不得进入知识库。只引用环境变量名。
7. 新内容先写入 `draft/`，完成静态检查和真机验证后再转入 `pages/`，同时更新 `app_map.json`、`backlinks.json` 和 `audit_state.json`。

## 探索前检查清单

- `PLATFORM=android`
- `adb devices` 中目标设备状态为 `device`
- 已设置 `ANDROID_DEVICE_SERIAL`（多设备时必须设置）
- 已确认 `ADB_PATH`（如果 adb 不在 PATH）
- 已记录应用包名和启动 Activity
- 已记录设备分辨率、density、Android 版本和屏幕方向
- 已准备可回收的测试账号/测试数据

## 与测试代码的对应关系

Android 测试仍通过 `utils.aw.AWBase` 和 `AndroidAdbDriver` 进行交互。知识库只描述页面事实和稳定定位信息，不绕过 AWBase 直接固化 `tap(x, y)` 坐标。

## 维护命令

以下命令显式指定 Android 知识库；Web 默认仍使用 `explorer_output/knowledge/`。

```powershell
python scripts/knowledge/health_check.py --knowledge-dir knowledge/android --json
python scripts/knowledge/backlinks_generator.py --knowledge-dir knowledge/android
python scripts/knowledge/promote_knowledge.py --knowledge-dir knowledge/android --check-only
python scripts/knowledge/embedding_pipeline.py --knowledge-dir knowledge/android --chroma-dir knowledge/android/.chroma_db
python scripts/knowledge/_obsidian_like_preview.py --knowledge-dir knowledge/android --port 8766
```
