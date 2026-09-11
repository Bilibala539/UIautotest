---
page_id: swan_消息中心页
name: "消息中心"
aliases: [消息页, message_page]
route: /me/messages
status: 已验证
last_updated: 2026-09-10
type: 页面
package_name: com.swan.network
activity: null
orientation: portrait
---

# 消息中心 (swan_消息中心页)

## 页面概述

账号消息列表页（路由 /me/messages，详情页 /me/messages/detail）。

**⚠️ 入口受限：本轮真机全路径排查未找到 UI 入口，页面内容未经真机验证，以下均为入口排查记录。**

存在性证据（APK libapp.so 字符串静态分析，只读不改设备）：
- `presentation/pages/me/message/message_page.dart` / `message_detail_page.dart` 源文件路径
- `pure_flutter_message_center_port.dart` / `message_center_port.dart` 平台端口
- l10n 中文串"消息中心"（UTF-16LE 命中 1 处）

## 生效断言

> 未进入本页，暂无可执行断言。

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| （待补） | — | — | 需先找到入口 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| （未找到） | — | — | — |

**已排查清单（2026-09-10 真机实测，均无入口）：**

1. 我的页全部功能行（滚动到底，关于与升级为最后一行）：无消息中心/消息通知行
2. 我的页顶部 raw dump：只有扫一扫一个图标，无消息铃铛图标
3. 首页四顶 Tab / 平台页 / 设备页顶栏：无消息图标

**推测入口方向（未验证，禁止当事实用）：** 系统推送通知点击触达（功能地图标注"推送通知 Port 仅见定义、
到达路径待确认"；`message_center_port` 的存在支持此推测）。自动化如需触达，
可能要借助 adb 通知注入或服务端发推送——属于框架层能力，须用户决策。

## 关键元素

> 页面未进入，不写任何未经验证的元素。

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| （待入口找到后补充） | — | — | — | — | — | blocked |

### 元素截图（image/flutter）

无。

## 页面布局

未验证。消息列表预期为 动态（内容随消息变化）。

## 功能关联

- 所属 feature：`[[feature_账号体系]]`（个人中心域）
- 相关：反馈未读红点服务（功能地图：pure_flutter_user_feedback_unread_port）、`[[swan_帮助与反馈页]]`
- 上游：未知（疑似推送通知）；下游：消息详情 /me/messages/detail（未验证）

## 反向引用
<!-- backlinks:start -->

| 引用来源 | 页面ID |
|---------|--------|
| digest/features/feature_账号体系.md | [[feature_账号体系]] |

_自动生成于 2026-09-11 13:44_
<!-- backlinks:end -->