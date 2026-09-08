# TidyTree 平台概况

## 已实测入口

- 首页：仪表盘、KPI 健康度、待办和系统状态。
- 流程与任务：`/processes`、`/workflows`、`/tasks`。
- 业务数据：Customers、Products、Collections、KPIs、OKRs、BI。
- 组织与权限：Org & People、Admin、Credentials。
- 平台能力：Integrations、Agents (M8)、DevBoard、AI Chat。

## 自动化策略

1. 以路由、页签和 UI 状态建模；树、表格、抽屉、弹窗、筛选和分页是独立状态。
2. 使用 `data-testid` 作为首选定位器，禁止对动态 UUID、指标数字和业务名称做硬编码断言。
3. 读取型用例可在现有账号下建立；写入、外部连接器、权限与凭据类用例必须先具备隔离环境和清理策略。

## 首批范围

首批仅覆盖 [[login_page]] 与 [[agents_page]] 的登录、列表展示、筛选和分页等只读能力。
