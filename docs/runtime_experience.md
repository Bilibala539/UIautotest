# 运行时经验

> 此文件由 orchestrator 在每次子 Agent 完成后追加新发现。
> 通过 `mcp__vector_kb__semantic_search(query, source_type="docs")` 检索。
> 定期人工审查，过期条目直接删除。

## 已验证操作

| 场景 | 正确做法 | 禁止做法 |
|------|---------|---------|
| MuMu 开关控件点击 | 点 x=450-480, y=555 | 图片匹配开关图标 |
| 管理标签页：删除自定义标签页 | 点右侧三点按钮（x≈510）→ 底部弹窗 → 选删除 | 点左侧 icon（只是切换显示/隐藏） |

## 已验证 AW 方法

| 方法 | 页面 | 备注 |
|------|------|------|
| user.send_message(recipient, message) | 会话列表 → 聊天页 | isback=False 时停在会话内 |
| user.search(tab, text) | 搜索页 | isclose=False 时保持搜索页打开 |

## 已知限制

| 场景 | 描述 |
|------|------|
| Python 多行命令 | 走 PowerShell 执行；避免 CodeMaker Hub 路径校验报错 |
| OCR click_text 偏移 | 点击筛选标签/弹窗选项/底部栏按钮时，加 dy=8~12 偏移 |
