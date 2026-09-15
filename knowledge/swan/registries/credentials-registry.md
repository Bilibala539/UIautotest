# 05g 凭据清单（实例）

> **安全纪律**：本文件只登记"凭据存在于哪里、谁维护、如何轮换"，**禁止把凭据明文写入本文件、聊天记录、BUG 报告或任何文档正文**。
> 违反处理：发现明文即视为 S3 安全缺陷登记 BUG，并立即轮换该凭据。

| 用途 | 存放位置 | 维护人 | 轮换方式 | 备注 |
|------|----------|--------|----------|------|
| 禅道 API（ZENTAO_URL / 账号） | 用户级环境变量 + `~/.claude/settings.json`（zentao-cli MCP env） | 用户 | 建议改用个人 API token 替代密码明文（zenTao 个人设置生成后 `setx ZENTAO_TOKEN`） | ⚠️ 现状密码明文于 settings.json，属已接受风险，待轮换 |
| Git 仓库（git.hivi.com） | Windows 凭据管理器 + `~/.ssh/`（ed25519 key） | 用户 | 站点侧改密/换 key | SSH key 已配置并验证连通 |
| 被测 App 测试账号 | 任务卡按需下发（禁止写入文档/报告） | 主对话按需 | 禅道/测试环境管理 | 测试数据一律 data_label=TEST-SYNTHETIC |
| 第三方 App 登录态 | 实机本地（人机交接预置，见 00c） | 用户预置 | 过期重登 | 被踢线任务标 BLOCKED: credential-required |
