---
page_id: swan_视频分类页
name: "视频分类（QQ音乐视频域入口族）"
aliases: [video_classify, 视频分类, 平台视频]
route: /music_platform/qq/video-classify
status: 已验证
last_updated: 2026-09-10
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 视频分类 (swan_视频分类页)

## 页面概述

QQ音乐平台视频分类页（路由 /music_platform/qq/video-classify，platform_video_classify_page.dart）。
同族还有视频播放页 /music_platform/video-player、视频投屏浮窗、投屏设备选择 弹层（功能地图「视频与投屏」域）。

**⚠️ 入口受限（授权门禁拦截）**：视频分类页挂在 QQ音乐平台多级页内，
而 QQ音乐多级页的全部入口在未授权账号下均被 `[[swan_授权门禁弹层]]` 拦截
（2026-09-10 Wave5 实测：首页·音乐 Tab 点「QQ音乐」区块标题 → 变体B
"请先登录 QQ 音乐/授权登录"，desc='纱罩'，press_back 关闭，⛔ 授权按钮不点）。
QQ音乐授权前无法触达视频分类及其下游视频播放/投屏页面。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| （不可达） | — | — | 页面未触达，无实测断言；转正前须在已授权账号上补测 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_首页音乐Tab]]` | `OCR"QQ音乐"`（平台区块标题） | click | **被拦截** → `[[swan_授权门禁弹层]]` 变体B（2026-09-10 Wave5 实测） |

自然语言补充：视频分类页的精确上游（是多级页内 Tab、宫格卡还是歌单详情内入口）未能确认——
上游 QQ音乐多级页本身进不去。首页·音乐 Tab 全页滚动排查（QQ/网易/酷狗/Apple/Qobuz 五区块）
无独立"视频/MV"区块；搜索结果页六分类 Tab（单曲/艺人/专辑/歌单/电台/播客）也无视频分类。

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| （未触达） | — | — | — | — | — | ⚠️ 授权门禁拦截 |

## 页面布局

未触达，无实测布局。依功能地图仅知实现文件：
platform_video_classify_page.dart / platform_video_player_page.dart /
platform_video_cast_floating.dart / platform_video_projection_device_sheet.dart。

## 功能关联

- 所属 feature：`[[feature_平台聚合]]`（视频与投屏域，建议单列 feature_视频与投屏）
- 上游：QQ音乐平台多级页（⚠️ 授权门禁拦截）
- 下游：视频播放页 /music_platform/video-player（同族，均未触达）
- 前置条件：**需要 QQ音乐平台授权**（本账号全平台未授权）
