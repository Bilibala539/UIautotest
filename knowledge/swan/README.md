# Swan (Flutter) 知识库

本目录记录 Swan App（Flutter，`com.swan.network`）的已验证页面、导航路径、无障碍 定位器和可复用测试上下文。

## 隔离原则

- 本知识库只属于 Swan 项目，与 `knowledge/web`（TidiTree Web）、`knowledge/android`（音箱屏 Android 项目）完全隔离
- 禁止把其他项目的路由、DOM 定位器、页面结构当作 Swan 的事实来源
- 页面事实必须由真机探索或测试实际验证后写入 `pages/`，禁止猜测

## 当前状态

- 状态：15 页已录入并转正（2026-09-08，explorer + verify 双重验证）
- 设备：Android 真机，`ANDROID_DEVICE_SERIAL` 指定
- 定位策略：无障碍键 优先（Flutter Semantics 暴露的 resource-id），OCR 文本次之，图像模板兜底，禁止坐标

## 目录结构

```text
swan/
├── app_map.json            # 页面、元素、转场和功能索引
├── backlinks.json          # 页面 wikilink 反向索引
├── pages/                  # 已验证页面（正式知识）
├── draft/                  # 探索草稿（验证通过后转正 pages/）
├── digest/
│   ├── features/           # 跨页面功能全景
│   └── flows/              # 跨页面流程文档
└── templates/page.md       # 页面文档模板
```

## 页面文档五要素（草稿 转正门槛）

1. `## 页面概述` — 用途、进入条件、稳定 UI 状态
2. `## 进入方式` — 可执行的导航步骤 + 成功断言
3. `## 关键元素` — 无障碍键 / 文案 / 图片常量表
4. `## 页面布局` — 区域划分（不写死坐标）
5. `## 关联` — `[[swan_page_id]]` 上下游关系

## MCP 访问

```text
knowledge_graph_swan / vector_kb_swan  （.mcp.json 已按 UIAUTOTEST_KNOWLEDGE_DIR 指向本目录）
```
