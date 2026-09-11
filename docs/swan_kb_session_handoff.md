# Swan 知识库建设 · 会话交接(2026-09-11)

> 用途:主会话重启/换人接手时恢复上下文。工作完成后可归档。
> 权威计划:`docs/待办与缺口清单.md`;踩坑经验:`docs/runtime_experience.md`(必读)。

## 一、任务目标(用户 7 项需求)

完善 Swan 知识库,支撑 UI 自动化用例生成:① 覆盖每个页面;② 元素全量+静态/动态区分;③ 元素出现/消失=生效断言语义;④ 结构化进入方式(来源页|locator|操作|到达断言);⑤ 功能概念串页面/元素/操作/App反应(即 flow);⑥ 每元素有截图供 OpenCV 断言;⑦ 双层架构(图谱+向量)。

## 二、当前状态(全部已 push 至 origin/master @ e3618b8)

- **页面层**:48 页全在 `knowledge/swan/pages/`,draft/ 清零;app_map 48 页(33 verified/15 page)
- **元素图**:62 张正式(`image/flutter/`),全部真机验证转正;暂存区空
- **流程层**:7 个 feature + 6 条 flow + 中文索引 + 页面覆盖对照
- **索引层**:backlinks 50 文件注入;ChromaDB 367 块;两套向量库均已入 git(`knowledge/swan/.chroma_db` 8MB + 根目录 web 用 188KB)
- **文档术语已全面中文化**(无障碍键/可点击/坐标范围/静态动态/草稿已验证);代码标识符(反引号内 key 值、AW 方法名、frontmatter 字段名)不翻译
- **git 提交链**:2ac47a8(W4探索)→ b978a67(W3远端阻塞)→ e6e9041/15e0b16(W4元素+转正)→ b92e0a9(6条flow)→ 286b1d8/cfe5b7a/ca347a6(W5探索+采集+转正)→ 6884fa4(集成+中文化)→ 973a954/e3618b8(向量库入库)

## 三、探索波次进度(依据 digest/页面覆盖对照.md)

- Wave 1(P1 核心)✅、Wave 2(收藏/播放器)✅、Wave 4(平台/搜索)✅、Wave 5(AI/角色/DIY/Vision)✅
- **Wave 3(设备域)未跑**:远端 .166 的 vivo 手机 USB 断开曾阻塞;**2026-09-11 用户已插新安卓机但手机端 USB 调试未开**(Windows 只枚举到 Linux File-CD Gadget,无 ADB 接口)——等用户在手机上开开发者选项+USB调试+传输文件模式+授权指纹,然后 `ssh 192.168.12.166 "C:/platform-tools/adb.exe devices"` 验证
- 危险项只读波次(充值/退款/订单/解绑/固件升级)未跑;绑定手机号(50015)/第三方登录未覆盖

## 四、待办与已知问题

1. **vector_kb MCP 本会话报 chromadb 导入失败**:`.mcp.json` 已指向 venv pythonw(配置正确),但会话启动的 MCP 进程是旧配置——重启会话/`/mcp` reconnect 即可;knowledge_graph MCP 正常
2. **测试账号全平台未授权** → 卡住:统一音乐库/批量操作/选择歌单/播放队列/歌词/视频分类/艺人页/排行榜等(⛔ 页面已如实记录不可达);需用户决定是否给测试账号授权
3. **flow 层仍薄**(6 条),后续补:授权门禁弹层、AI 域链路、登录密码登入分支等
4. 首页 AI Tab 路由归属存疑(/home/aiRoles vs 独立路由)——待 Core 仓库考古
5. 旧格式页面(如 swan_首页/收藏分组详情页)缺 frontmatter,迁移待办
6. 中文输入(歌单名/AI对话)框架不可达:`adb shell input text` 不支持中文,需 IME 方案(**框架层改动,须用户决策**)
7. web 项目旧 `.chroma_db`(188KB)可能是 9-8 后过期的,下次做 web 时先重建

## 五、关键操作知识

- **远端 .166**:ssh 192.168.12.166(admin);adb 在 `C:\platform-tools\adb.exe`(**本机 adb 在 `D:\scrcpy-win64-v4.1\adb.exe`,勿混**);本机设备 serial c0614b6a;远端仓库 E:\uiautotest
- **远端派活**用户要求可见 CLI 窗口(禁止 headless `claude -p`);run-task.ps1 曾因 4KB 任务文本作 argv 卡确认框,方案=短指令+让远端自己 Read task.txt+`--add-dir E:\uiautotest`(修复是否落地需到 .166 核实)
- **冲突约定**:远端只写 draft+报告并 git push,不碰 app_map;先 push 先得,后者 pull --rebase
- **嵌入管线**:必须 `UIAUTOTEST_EMBEDDING_MODEL=E:/UIAutotest/models/paraphrase-multilingual-MiniLM-L12-v2` + venv python(否则去连 huggingface 必败);protobuf 钉 3.20.2;paddle/torch 分进程
- **安全红线**(不可违):⛔ 注销账号/删除歌单/设备行点击/授权去授权/充值支付/固件升级——只断言入口;⛔ 坐标点击;⛔ 授权门禁弹层用 press_back 关
- **转正门禁**:image_ai 暂存 → 离线匹配 ≥0.8 → 真机点击反应 → promote_image;探索(draft)与验证(verify)分离
- **调度模式**:用户指定"一个 agent 负责拆分调度,其他 agent 执行"(调度器 agent 曾用 id aa92c3d3fbc77c2bd,已被用户手动停止;可重新 spawn 或主会话直接编排)
