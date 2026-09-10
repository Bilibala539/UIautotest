# flows/ —— 端到端操作路径

一条 flow = 一条可在真机上走通的操作路径（页面 → 元素 → 操作 → App 反应 → 断言），是 aw-codegen 生成 pytest 用例的直接输入。

- 模板：`templates/flow.md`
- 命名：`flow_<功能域>_<路径名>.md`，如 `flow_登录_密码登录.md`
- 写法标准：`../CONTRIBUTING.md` 第 6 节
- `risk: high` 的 flow（充值/注销/删除设备/固件升级）只断言不点击
