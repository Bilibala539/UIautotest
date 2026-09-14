---
feature_id: feature_播放器
name: "播放器"
aliases: [播放, player]
status: 草稿
last_updated: 2026-09-10
domains: [播放器与输出]
---

# 播放器 (feature_播放器)

## 功能定义

全屏播放页 + 输出设备切换（multiroom）+ （待解锁）播放队列/歌词。2026-09-10 Wave2 从
feature_导航框架 拆出：播放域页面已成簇（播放页/切换设备弹层/队列 sheet/歌词视图），
独立归属便于播放用例组织与安全约束（控制类按钮只断言不点）集中管理。

## 包含页面

| 页面 | 角色 | 状态 |
|---|---|---|
| `[[swan_播放页]]` | 全屏播放页 /player | 页面 |
| `[[swan_切换设备弹层]]` | 输出设备切换 multiroom_sheet | 草稿 |

待解锁（无播放任务/未授权不可达）：播放队列 底部弹层（current_queue_bottom_sheet.dart，
无任务时 `player_queue_button` 点击无反应）、歌词视图（lyric_view.dart，入口疑似播放中封面区）。

## 包含 flow

- （待建）flow_播放_打开关闭播放页
- （待建）flow_播放_切换输出设备弹层断言（⛔ 只断言不选择）

## 边界与危险操作

- ⛔ 播放/暂停/切歌/循环/音量等控制按钮：只 image_exists 断言，不下发点击（真实音箱安全约定）。
- ⛔ `[[swan_切换设备弹层]]` 设备行（Libretto_0E00 / Maestro1100_A20C / HiVi M300MKII）为实验室
  真实音箱，禁止选择；只断言 `multiroom_sheet` 出现与设备名 OCR。
- 本账号（13555555555）所有第三方平台未授权，**无法建立任何播放任务**（歌单/电台/AI 点歌三路
  均被授权弹层拦截），播放中状态探索需已授权账号。

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_导航框架.md | [[feature_导航框架]] |
| pages/swan_切换设备弹层.md | [[swan_切换设备弹层]] |
| pages/swan_播放页.md | [[swan_播放页]] |

_自动生成于 2026-09-14 13:26_
<!-- backlinks:end -->