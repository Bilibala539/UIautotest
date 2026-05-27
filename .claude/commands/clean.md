# 清理运行产物

清理 `output/` 目录下的所有运行时产物（日志、截图、allure数据、session历史）。

## 执行步骤

1. 删除 `output/` 下所有内容
2. 重建空目录结构（allure-results、screenshots、logs、sessions）
3. 清理所有 `__pycache__/` 目录（排除 venv）
4. 报告清理结果

```powershell
# 清理 output/
Get-ChildItem "E:\UIAutotest\output" -Recurse | Remove-Item -Recurse -Force -Confirm:$false

# 重建目录结构
New-Item -ItemType Directory -Force "E:\UIAutotest\output\allure-results" | Out-Null
New-Item -ItemType Directory -Force "E:\UIAutotest\output\screenshots" | Out-Null
New-Item -ItemType Directory -Force "E:\UIAutotest\output\logs" | Out-Null
New-Item -ItemType Directory -Force "E:\UIAutotest\output\sessions" | Out-Null

# 清理 __pycache__
Get-ChildItem "E:\UIAutotest" -Directory -Recurse -Filter "__pycache__" | Where-Object { $_.FullName -notmatch "venv" } | Remove-Item -Recurse -Force -Confirm:$false
```
