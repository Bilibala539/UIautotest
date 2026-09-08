---
page_id: agents_page
name: "Agents 列表（M8）"
aliases:
  - Agents
  - M8 Agents
status: verified
last_updated: 2026-09-01
signature:
  - Agents
  - Delegated agents available to this workspace
  - m8-agents-page
type: route_state
route: /agents?view=agents
auth_state: authenticated
---

# Agents 列表（M8） (agents_page)

## 页面概述

M8 Agent Runtime 的 Agent 注册表。页面展示 Agent 汇总指标、近期失败摘要、筛选器、分页列表及查看/删除等操作入口。

## 进入方式

| 来源页面 | 操作 | 验证 |
|---|---|---|
| [[login_page]] | 成功提交登录表单 | `m8-agents-page` 可见 |
| 任意已登录页面 | 点击侧边栏 “Agents (M8)” | URL 为 `/agents?view=agents` |
| M8 Runtime 等页签 | 选择顶栏 “Agents” | Agents 页签处于选中状态 |

## 退出方式

| 目标页面 | 操作 | 验证 |
|---|---|---|
| M8 Runtime | 选择顶栏 “Runtime” | URL 包含 `view=runtime` |
| 平台其他模块 | 使用侧边栏导航 | 目标模块根节点可见 |

## 页面布局

```
┌ 侧边栏 ┬──────────────────────────────────────────────┐
│ 模块导航 │ M8: Agents | Runtime | BI | AI log           │
│          ├──────────────────────────────────────────────┤
│          │ 汇总指标 + 近期失败摘要                       │
│          ├──────────────────────────────────────────────┤
│          │ 搜索 + 生命周期/运行/健康/同步/连接器筛选器   │
│          ├──────────────────────────────────────────────┤
│          │ Agent 表格：状态、归属、最近运行、查看/删除  │
│          └──────────────────────────────────────────────┘
```

## 关键元素

| 元素 | 稳定定位器 | 操作 | 副作用 | 验证状态 |
|---|---|---|---|---|
| 页面根节点 | `m8-agents-page` | 可见性断言 | 无 | 已实测 |
| 汇总区 | `m8-agents-summary` | 读取 | 无 | 已实测 |
| Agent 筛选区 | `m8-agents-filters` | 读取/筛选 | 无 | 已实测 |
| 名称搜索框 | `m8-agents-filter-search` | 输入 | 无 | 已实测 |
| 生命周期筛选 | `m8-agents-filter-lifecycle` | 选择 | 无 | 已实测 |
| 运行状态筛选 | `m8-agents-filter-runtime` | 选择 | 无 | 已实测 |
| 健康状态筛选 | `m8-agents-filter-health` | 选择 | 无 | 已实测 |
| 同步状态筛选 | `m8-agents-filter-sync` | 选择 | 无 | 已实测 |
| 连接器筛选 | `m8-agents-filter-connector` | 选择 | 无 | 已实测 |
| Agent 表格 | `m8-agents-table-wrapper` | 读取/分页 | 无 | 已实测 |
| 动态行 | CSS `[data-testid^='m8-agents-row-']` | 读取 | 无 | 已实测 |
| 查看按钮 | CSS `[data-testid^='m8-agents-view-']` | 详情探索待补充 | 无 | 已发现 |
| 新建/导入/同步/删除 | `m8-agents-*-btn` 与动态 delete locator | 不纳入首批 | 写入或外部副作用 | 已发现 |

## 测试数据与安全

1. 列表当前包含动态 Agent 数据，测试不得依赖总数、动态 UUID、真实名称或失败统计值。
2. 首批只覆盖读取、筛选、分页和详情查看；禁止自动执行新建、导入、同步、删除。
3. 写入类测试须使用独立测试租户或可清理的专用 Agent，并在流程中记录清理步骤。

## 关联

| 关联页面 | 关系类型 | 说明 |
|---|---|---|
| [[login_page]] | precondition | 需要有效登录会话 |

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/flows/agent_list_read_only.md | [[agent_list_read_only]] |
| pages/login_page.md | [[login_page]] |
| digest/platform_profile.md | [[platform_profile]] |

_自动生成于 2026-09-01 10:16_
<!-- backlinks:end -->