# Android UI 自动化测试框架

基于 pytest + Appium 的安卓 UI 自动化测试框架，支持图像识别和 OCR 定位。

## 📋 功能特性

- ✅ **图像识别定位**: 基于 OpenCV 模板匹配
- ✅ **OCR 文字识别**: 基于 Tesseract OCR
- ✅ **随机账号登录**: 从账号池中随机选择账号
- ✅ **独立测试文件**: 每个用例文件包含 setup/teardown
- ✅ **自动截图**: 失败时自动保存截图
- ✅ **日志记录**: 详细的测试日志
- ✅ **HTML 报告**: 生成美观的测试报告

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装 Python 3.8+
# 安装 Appium Server
npm install -g appium

# 安装 Tesseract OCR
# Ubuntu/Debian: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
# Windows: 下载 Tesseract for Windows

# 安装 Android SDK 并配置环境变量