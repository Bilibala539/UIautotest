# 运行时经验

> 此文件由 orchestrator 在每次子 Agent 完成后追加新发现。
> 通过 `mcp__vector_kb__semantic_search(query, source_type="docs")` 检索。
> 定期人工审查，过期条目直接删除。

## 已验证操作

| 场景 | 正确做法 | 禁止做法 |
|------|---------|---------|
| MuMu 开关控件点击 | 点 x=450-480, y=555 | 图片匹配开关图标 |
| 管理标签页：删除自定义标签页 | 点右侧三点按钮（x≈510）→ 底部弹窗 → 选删除 | 点左侧 icon（只是切换显示/隐藏） |
| OCR `click_text` 偏上 | 筛选器标签/弹窗选项/底部栏按钮加 `dy=8~12` | 不加偏移直接点（会点到上方元素） |
| 图片匹配失败 | 先查图片质量（灰度标准差>5、均值5-250、无角标/阴影），再查代码 | 直接改代码逻辑或加坐标回退 |
| `click_image` 失败时 | 重截图或调阈值 | 加 `tap(x,y)` fallback |
| 框架层发现问题 | 报告用户，由用户决定是否改、如何改 | 自己改 devices.py / conftest.py / driver/ |
| Python 多行命令 | 走 PowerShell 执行 | CodeMaker Hub 路径校验会报错 |

## 已验证 AW 方法

| 方法 | 页面 | 备注 |
|------|------|------|
| user.send_message(recipient, message) | 会话列表 → 聊天页 | isback=False 时停在会话内 |
| user.search(tab, text) | 搜索页 | isclose=False 时保持搜索页打开 |
| user.open_sidebar() | 消息列表页 | 打开左侧侧边栏 |
| user.open_settings() | 侧边栏 | 进入设置页 |

## 已知限制

| 场景 | 描述 |
|------|------|
| 搜索页 Tab 定位 | 需用 region 排除消息列表标题干扰，如 `region=(0,100,540,100)` |
| 搜索结果加载 | 搜索后需 `time.sleep(3)` 等待结果加载完成，不能用图片判断 |
| 弹窗选项点击 | OCR 返回坐标偏上，需加 dy=8~12；列表条目无需加 |
