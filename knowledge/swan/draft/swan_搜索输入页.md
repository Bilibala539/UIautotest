---
page_id: swan_搜索输入页
name: "搜索输入页"
aliases: [search_page, 搜索页]
route: "/search"
status: draft
last_updated: 2026-09-10
type: screen
package_name: com.swan.network
activity: null
orientation: portrait
---

# 搜索输入页 (swan_搜索输入页)

## 页面概述

全域搜索的输入页（route `/search`，search_page.dart）。顶栏为「返回 + 搜索框 + 搜索按钮」，
搜索框是**原生 android.widget.EditText**（非 Flutter 语义节点），默认 hint「搜索歌曲或艺术家等」。
下方为「搜索历史」区（关键词 chip 列表，整行可点，点击即带词直达搜索结果页）。
聚焦搜索框后页面底部弹出 **App 自定义 T9 键盘**（分词/ABC/DEF…/中英切换/123/清空），
系统 IME 不出现。底部播放条与全局 tab 栏**不出现**（本页为全屏独立路由，返回后回到来源页）。

2026-09-10 Wave4 实测：`adb input text` 输入英文有效（"piano"/"harmony" 均成功）；
中文不可输入（adb 限制，见 runtime_experience）。

## 生效断言

| 断言元素 | 出现/消失 | 断言方式 | 含义 |
|---|---|---|---|
| 搜索框 hint | 出现 | OCR"搜索歌曲或艺术家等" | 本页已生效 |
| 搜索按钮 | 出现 | OCR"搜索"（顶栏右侧 y≈117-163，region 限定顶栏） | 本页已生效 |
| 搜索历史标题 | 出现 | OCR"搜索历史" | 历史区加载 |

## 进入方式

| 来源页面 | 操作元素（locator） | 操作类型 | 到达断言 |
|---|---|---|---|
| `[[swan_首页音乐Tab]]` | `OCR"跨平台搜索音乐"`（搜索条） | click | 见「生效断言」 |
| `[[swan_首页电台Tab]]` | `OCR"搜索电台"`（搜索条，SWAN_HOME_RADIO_SEARCH_BAR 图已有） | click | 同一 /search 页，hint 相同（实测，非电台专属输入页） |
| `[[swan_搜索结果页]]` | press_back | 返回 | 关键词回填输入框、历史 chip 保留 |

注意：多入口共用同一页面（功能地图记 8 处入口；已实测音乐/电台两处，推荐 Tab 音源卡与平台域入口待后续验证）。
返回箭头（无 key 无文案）与 X 清空按钮均无语义 key，需 element 截图。

## 关键元素

| 元素 | locator（key / OCR 文案 / 图片常量） | 类型 | 操作 | 成功断言 | 截图 | 验证状态 |
|---|---|---|---|---|---|---|
| 返回按钮（左上） | 无 key 无文案（bounds 类 ImageView）→ 图片 `SWAN_SEARCH_BACK` | static | click | 回来源页 | `swan_搜索输入页_返回按钮.png`（draft） | 2026-09-10 element 已采集 |
| 搜索输入框 | 原生 EditText；OCR hint"搜索歌曲或艺术家等"定位后 click，`input_text(英文)` | dynamic | input | 框内出现关键词（OCR） | dynamic-不截图 | verified（piano/harmony 实测） |
| X 清空按钮 | 输入后出现于框右侧，无 key → 图片 `SWAN_SEARCH_CLEAR` | static | click | 关键词清空 | `swan_搜索输入页_清空按钮.png`（draft） | 2026-09-10 element 已采集 |
| 搜索按钮 | `OCR"搜索"`（顶栏右，region 限定避开自定义键盘"搜索"键）或图片 `SWAN_SEARCH_SUBMIT` | static | click | `[[swan_搜索结果页]]` 生效断言 | `swan_搜索输入页_搜索按钮.png`（draft） | verified |
| 搜索历史 chip | OCR 关键词文案（如"piano"，整行节点 desc=关键词） | dynamic | click | 直达 `[[swan_搜索结果页]]` 并自动执行搜索 | dynamic-不截图 | verified（piano 实测） |
| 自定义 T9 键盘 | OCR"分词"/"中/英"/"清空"（键盘区 y>1150） | static | 只读 | — | 待截 | draft（未用键盘输入，走 adb） |

### 元素截图（image/flutter）

| 元素 | 建议常量 | 图片文件 |
|---|---|---|
| 返回按钮 | `SWAN_SEARCH_BACK` | image_ai/flutter/swan_搜索输入页_返回按钮.png（2026-09-10 已采集，draft） |
| 搜索按钮 | `SWAN_SEARCH_SUBMIT` | image_ai/flutter/swan_搜索输入页_搜索按钮.png（2026-09-10 已采集，draft；与结果页共用） |
| X 清空按钮 | `SWAN_SEARCH_CLEAR` | image_ai/flutter/swan_搜索输入页_清空按钮.png（2026-09-10 已采集，draft） |

## 页面布局

- 顶栏：返回箭头（左）+ 搜索框（中，原生 EditText）+ 搜索按钮（右）
- 内容区：「搜索历史」标题 + 关键词 chip 行（可点复搜）；无「热门搜索」区
- 底部：聚焦输入框时为 App 自定义 T9 键盘（分词/ABC/DEF/GHI/JKL/MNO/PQRS/TUV/WXYZ/0、
  123、中/英、清空、搜索）；无 bottom_player、无全局 4 tab

## 功能关联

- 所属 feature：`[[feature_平台聚合]]`（搜索域）
- 上游：`[[swan_首页音乐Tab]]`、`[[swan_首页电台Tab]]`（其余 6 处入口待验证）
- 下游：`[[swan_搜索结果页]]`
- 功能地图对应：搜索输入页 /search（14 条 L2 用例因 ANR BUG-004 执行 BLOCKED；探索实测本账号可正常进出）
