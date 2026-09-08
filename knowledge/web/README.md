# TidyTree Web 知识库

本目录记录 TidyTree Web 平台的已验证页面、导航路径、稳定定位器和测试约束，供 Web 自动化测试与 AI 探索使用。

## 架构

知识库采用 Graph + Embedding 双层架构：

```
Graph: app_map.json + pages/*.md + [[wikilink]] + backlinks.json
Embedding: pages/*.md + digest/*.md + web_tests/*.py
```

## 目录结构

```
knowledge/
├── app_map.json          # 路由、UI 状态、跳转、元素及功能索引
├── pages/                # 已验证页面文档
├── draft/                # AI 探索草稿，验证后再转正
├── digest/               # 平台概况、跨页面流程、业务规则和角色矩阵
├── backlinks.json        # 自动生成的双向链接索引
├── audit_state.json      # 页面实测审计结果
└── graph_view.md         # 自动生成的图谱视图
```

## Web 建模规则

- 一个节点表示“路由模板 + 可测试 UI 状态”，而不是一条动态数据记录。
- 定位器优先级：`data-testid` → ARIA role/name → label → CSS；截图仅作证据。
- 每个跳转应记录前置条件、操作、成功断言和副作用等级。
- 不记录账号密码、会话 ID、API Key 或生产业务数据。
- 写入、删除、导入、同步、运行外部工作流等操作须使用可清理的测试数据。

## 更新流程

```
browser explorer → draft/*.md → 静态校验与实测 → pages/*.md
                                                   ↓
                              app_map + backlinks + embedding 增量更新
```
