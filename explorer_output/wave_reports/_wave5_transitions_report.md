# Wave 5 AI/Vision/视频域探索 transitions 报告

> 执行日期：2026-09-10　|　执行者：aw-explorer（Wave 5）
> 设备：c0614b6a（OPPO，Android 11）　|　App：com.swan.network，账号已登录
> 过程数据：`E:\UIAutotest\explorer_output\wave5\`（explore.py + dumps/ + 截图 screenshots/wave5/）
> ⚠️ 本报告为 Wave5 transitions 汇总，**未合入 app_map.json**（由 orchestrator 决定合入时机）。

## 新增页面（draft/）

| page_id | 路由 | 可达性 |
|---|---|---|
| swan_所有角色页 | 待考古（候选 /home/aiRoles 或 /ai/role/manage） | ✅ 实测 |
| swan_角色编辑页 | /ai/role/create | ✅ 实测 |
| swan_AI形象页 | /ai/role/images | ✅ 实测 |
| swan_DIY形象页 | null（挂在 images 之下的子页） | ✅ 实测 |
| swan_AI平台管理页 | /ai/platform/manage | ✅ 实测（列表可达，绑定按钮被门禁拦） |
| swan_AI历史页 | /ai/history | ✅ 实测 |
| swan_视频分类页 | /music_platform/qq/video-classify | ⚠️ 授权门禁拦截（QQ音乐未授权） |
| swan_Vision域不可达页 | /vision/wallpaper 等 4 族 | ❌ 不可达（未绑定可视音箱，无入口） |

## 新发现 transitions（均真机实测，2026-09-10 Wave5）

### swan_首页AITab（补充）

| to | action | type | status |
|---|---|---|---|
| swan_所有角色页 | click_image `SWAN_HOME_AI_ROLE_SETTINGS`（右 pill 图标按钮） | 推进 | verified |
| swan_角色编辑页 | click_text「添加更多AI角色」（左 pill；推定与所有角色页底部按钮同路径） | 推进 | draft |
| swan_AI历史页 | click_text「历史对话记录」（**区块标题行本身**，可点 ImageView；⚠️ 不是记录行） | 推进 | verified |

### swan_所有角色页

| to | action | type | status |
|---|---|---|---|
| swan_首页AITab | press_back | 返回 | verified |
| swan_AI对话页 | click 系统角色行（OCR 角色问候语整行；实测云舒雁行，对话记录回显） | 推进 | verified |
| swan_角色编辑页 | click_text「添加更多AI角色」（底部通栏） | 推进 | verified |
| （本页内）多选模式 | click_text「多选」（自定义区标题行右侧）→ 按钮变「取消」+ 底栏「全选/删除」；点「取消」退出。多选=角色批量管理（删除 ⛔ 危险不点） | 模式切换 | verified |

### swan_角色编辑页

| to | action | type | status |
|---|---|---|---|
| swan_所有角色页 | press_back（从所有角色页进入时） | 返回 | verified |
| swan_AI形象页 | click_text「选择」（形象生成区右上） | 推进 | verified |
| swan_AI平台管理页 | click_text「更多AI平台」（AI平台选择区通栏） | 推进 | verified |
| （表单）语音单选 | click 语音行（知楠/知琪/知厨/知德/知佳/知茹 ×6，OCR 行文案） | 表单操作 | draft（未逐个实测） |
| （表单）提交 | click_text「完成」（底部通栏） | 推进 | draft（⛔ 未点，必填项全空） |

### swan_AI形象页

| to | action | type | status |
|---|---|---|---|
| swan_角色编辑页 | press_back | 返回 | verified |
| swan_DIY形象页 | click_text「DIY形象」（底部右半） | 推进 | verified |
| swan_角色编辑页 | click_text「完成」（底部左半，携带所选动图返回；未实测选中态） | 返回 | draft |

### swan_DIY形象页

| to | action | type | status |
|---|---|---|---|
| swan_AI形象页 | press_back | 返回 | verified |
| （付费红线） | 「开始生成」（0.2 惠币/张起）与「充值」⛔ 只断言不点击；「上传照片」未点（拉起系统选择器） | — | — |

### swan_AI平台管理页

| to | action | type | status |
|---|---|---|---|
| swan_角色编辑页 | press_back | 返回 | verified |
| swan_授权门禁弹层 | click 行右侧 48×48 深色方形图标按钮（无 key 无文案，行本体不可点；实测 Qwen 行）→ 弹「添加新平台/请先添加该 AI 平台…/添加」+ 纱罩；press_back 关闭。8 个平台行同构，⛔ 「添加」不点 | 弹层（授权拦截） | verified |

### swan_AI历史页

| to | action | type | status |
|---|---|---|---|
| swan_首页AITab | press_back（实测落地 AI Tab，不回来源链） | 返回 | verified |
| swan_AI对话页 | click 会话记录行（OCR 记录摘要；实测 play a song → 小薇对话回显） | 推进 | verified |

### swan_首页AITab（历史区补充，原地）

- 点历史**记录行**（区块内摘要卡）→ 直达 `swan_AI对话页`（不经过 AI 历史页），verified。

### swan_首页音乐Tab（视频域补充）

| to | action | type | status |
|---|---|---|---|
| swan_授权门禁弹层 | click_text「QQ音乐」（平台区块标题）→ 变体B「请先登录 QQ 音乐/授权登录」+ 纱罩；press_back 关，⛔ 不点授权。**视频分类页 /music_platform/qq/video-classify 的上游即此多级页，未授权不可达** | 弹层（授权拦截） | verified |

### swan_首页可视音箱Tab（Vision 域结论）

- 未绑定态内容区=单一不可点 ImageView（raw dump 确认零可点子节点），壁纸/唤醒词/语音包/高级设置**全部无入口**；功能地图「壁纸允许未绑定预览」未在 UI 实现。❌ 见 `swan_Vision域不可达页`。

## 与现有知识的一致性 / 勘误

1. `swan_首页AITab` 现文档 route 标 /home/aiRoles：Wave5 发现「所有角色」页更像独立路由页，
   /home/aiRoles 到底指 AI Tab 卡片区还是所有角色页**待考古 Core 仓路由表**，draft 中如实记录两候选。
2. AI Tab 系统角色实为 4 个（所有角色页可见云舒雁），首页卡区横滑只露 3 张——卡区可左右翻页（箭头 [32,324][80,372] / [640,324][688,372]），云舒雁在第 4 张（未翻页验证）。
3. 授权门禁弹层新增第三种文案变体：「添加新平台/请先添加该 AI 平台，即可开启专属于你的 AI 之旅～/添加」（AI 平台绑定场景），纱罩判据不变。

## 新坑（建议入 runtime_experience Swan 表）

| 场景 | 正确做法 |
|---|---|
| AI 平台管理页标题 | 标题 OCR 文案就是「平台」二字，与底部 tab「平台」同名；断言必须 region 限定顶栏，否则误命中底 tab |
| 历史对话记录双入口 | AI Tab 的「历史对话记录」区块：点**标题行**进 /ai/history 页，点**记录行**直达 AI 对话页；两者落点不同，用例须区分 |
| AI 对话页返回栈 | 从 AI 历史页/所有角色页进 AI 对话页后 press_back 一律回 AI Tab（对话页替换栈顶），不回来源页 |
| 平台行不可点 | AI 平台管理页 8 行行本体 clickable=false，只有右侧方形图标按钮可点；点击弹添加门禁（⛔ 不点添加） |
| DIY 形象付费 | DIY形象页「开始生成」0.2 惠币/张起 + 「充值」链接，自动化一律只断言不点击 |
| 多选删除危险 | 所有角色页多选态底栏「删除」会删自定义角色，⛔ 禁止点击；「全选」也勿点 |
| 角色编辑页两屏 | 自定义设置表单语音选择/昵称输入/完成按钮在下半屏，须 swipe_up x2 才可见（OCR 断言注意滚动前置） |
| 图片读取受限 | Read 工具在本环境对 png 只回 CDN 链接不回显内容；图标形态判断用 OpenCV 轮廓/像素分析替代人工看图 |

## 待 element 截图建议（下批 aw-element）

1. `SWAN_ALL_ROLES_TITLE`：所有角色页标题行（或用 OCR 即可）
2. `SWAN_ALL_ROLES_MULTISELECT`：「多选」文字按钮（含取消态）
3. `SWAN_ROLE_EDITOR_SELECT`：「选择」按钮（角色编辑页）
4. `SWAN_ROLE_EDITOR_MORE_PLATFORM`：「更多AI平台」通栏按钮
5. `SWAN_ROLE_EDITOR_DONE`：底部「完成」通栏按钮（页面最底）
6. `SWAN_ROLE_IMAGES_DIY_BTN`：「DIY形象」按钮（AI形象页底栏右半）
7. `SWAN_AI_PLATFORM_ROW_BTN`：平台行右侧方形图标按钮（8 行同构可共用一张）
8. `SWAN_AI_PLATFORM_TITLE`：顶栏「平台」标题（region 断言用）
9. `SWAN_AI_HISTORY_TITLE`：历史对话记录页标题行
10. `SWAN_DIY_GENERATE_BTN` / `SWAN_DIY_UPLOAD_CARD`：DIY形象页关键卡（只断言不点）
