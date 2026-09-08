---
page_id: android_<stable_page_id>
name: "页面名称"
aliases: []
status: draft
last_updated: null
type: screen
package_name: null
activity: null
orientation: portrait
---

# 页面名称 (android_<stable_page_id>)

## 页面概述

说明页面用途、进入条件和可观察的稳定 UI 状态。

## 进入方式

记录前置页面、ADB/应用操作和进入成功断言。

## 关键元素

| 元素 | 稳定定位器 | 操作 | 成功断言 | 验证状态 |
|---|---|---|---|---|
| 示例元素 | `resource-id` / `content-desc` / `text` | `click_text` 或 `click_image` | 可观察状态 | draft |

## 页面布局

记录顶部栏、内容区、列表、底部导航、弹窗或系统权限层级。

## UI 状态

记录 default、loading、empty、error、permission 等状态及其触发条件。

## 设备差异

记录 Android 版本、分辨率、density、横竖屏差异；不要写入设备序列号。

## 数据与安全

说明测试数据来源、环境变量名和清理步骤，不记录密码、token 或真实业务数据。

## 关联

使用 `[[android_other_page]]` 记录 Android 页面关系。不要直接链接 Web 页面 ID。
