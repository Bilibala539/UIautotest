# AW 补全计划（Swan / flutter）

> 范围（2026-10-12 拍板）：**只覆盖 flutter 平台 Swan App**；TidiTree（web）与音箱屏（android）不纳入本计划。
> 目标：Swan AW 业务层补全到"回归 76 条全实现、运行时零 key、每域有方法有用例"。
> 本计划是待办清单的执行拆解，落批次跟踪；每批完成后更新 §2 批次表状态并同步 AW 方法指南。
> 创建：2026-10-12（分支 feature/swan-aw）。维护：主会话（orchestrator）。

## 0. 现状盘点（2026-10-12）

| 维度 | 现状 | 结论 |
|---|---|---|
| 业务方法 | 34 公开业务方法（+回归 mixin 三件套，79 含内部辅助） | 主线完成约 55% |
| 用例 | 28 文件 / 77 条（回归域 3/4/7/8 + 登录存量） | 域 1/2/5/6/9 未落地 |
| 知识库 | 48 页 + 2 digest；QQ/网易/酷狗 3 平台主页 draft 缺 | W1-D 前置 |
| 图片资产 | 90 正式 + 21 暂存 | 域 1/5/6/2/9 约缺 20 张 |
| 基础层 | AWBase/FlutterBaseAW 操作齐备（find_image_rect/wait_toast/region_changed/drag_on_template/connect_wifi） | 不再是瓶颈 |
| 定位策略债 | 登录域 5 方法 + 导航 2 方法仍为存量 key 实现 | W1-A 迁移 |
| vector_kb MCP | venv 缺 chromadb 依赖未建 | 非阻塞（图谱层可用） |

## 1. 批次总表（按依赖排序）

| 批次 | 内容 | 产出（方法/用例文件/图片） | 依赖/阻塞 | 状态 |
|---|---|---|---|---|
| **W1-A 存量 key 迁移** | 登录域 5 方法（login_by_sms/login_with_password/logout_if_needed/enter_sms_code_step/fill_sms_code）+ 导航 3 方法（go_home/go_bottom_tab/tab 断言）重写为 [图]/[OCR]；登录页/首页锚点图补截 | ~8 方法改造 / 登录域 12 用例文件回归验证 / 新图约 6 张 | 无外部阻塞，**最先做**（解锁全工程零 key） | ✅ **完成（2026-10-12）**：两批落地（导航 3 方法 21/21 真机绿；登录域 7 方法+mixin 6 辅助，真机首飞 3 连过含 OTP 自动取码，验收 8/9 后修复两态模板复验通过）；swan.py 运行时 key 清零；10 图转正+1 暂挂（密码提交钮待密码域用例）；登录域 4+密码域 3 用例待密码注入后跑全量 |
| **W1-B 域1 启动登录新增** | A4 微信登录 / A5 微博登录（跨 App 授权）、A6 冷启动断言 / A7 后台恢复 / A8 绑定手机返回；用例 1-3、6-8 落地 | +5 方法 / +5 用例文件 / 新图约 4 张 | ⑤ 三方 App 登录态（微信/微博账号预置） | ⬜ 待开工 |
| **W1-C 域5 平台授权** | A24 authorize_platform / A25 assert_platform_state / A26 deauthorize_platform；用例 32-37 | +3 方法 / +6 用例文件（parametrize 平台×入口） / 新图约 6 张 | ⑤ 三方登录态 + ⑥ 授权半自动口径拍板 | ⬜ 待开工 |
| **W1-D 域6 平台内容页** | A27 open_platform / A28 open_platform_entry；用例 38-40 | +2 方法 / +3 用例文件 / 新图 2 张 | explorer 先补 QQ音乐/网易云/酷狗 3 个主页 draft | ⬜ 待开工（可与 W1-C 并行探索） |
| **W1-E 域2 配网** | A9 provision 统一入口 / A10 BLE / A11 热点（connect_wifi 已实现）；用例 9-10 | +3 方法 / +2 用例文件 / 新图约 5 张 | ④ 1 台**未配网**设备 | ⬜ 待开工 |
| **W1-F 域9 多房间** | A35 sync_rooms / A36 assert_room_synced；用例 73-76 | +2 方法 / +4 用例文件 / 新图约 3 张 | ④ ≥3 台 A31 + 3 台 H76D/H76G（rig 最多的一批） | ⬜ 待开工 |
| **W1-G Driver 尾巴** | D3 get_foreground_package（热启动恢复断言辅助，可选） | +1 driver 方法 | 框架层，**须用户拍板**（规则 9） | ⬜ 待拍板 |

执行序：**W1-A → W1-B/D(并行) → W1-C → W1-E → W1-F**；W1-G 随时穿插。

## 2. 外部阻塞清单（用户侧待办）

| # | 事项 | 影响批次 |
|---|---|---|
| ④ | 设备 rig：未配网设备 ×1（W1-E）；WiFi 音箱在线 ×2；A31×3 + H76D/H76G×3（W1-F） | W1-E、W1-F |
| ⑤ | 三方 App 登录态预置：微信/微博/QQ音乐/网易云/酷狗账号在测试手机不退出 | W1-B、W1-C、W1-D |
| ⑥ | 授权用例半自动口径：三方 App 内最终授权步（人工辅助 or OCR 兜底） | W1-C |
| D3 | driver 层 get_foreground_package 是否批准（框架层，规则 9） | W1-G |

## 3. 编排方式（每批一个交付周期）

```
explorer（需知识库的批次先跑，如 W1-D）→ element（截图进 image_ai/flutter，登记常量）
→ codegen（方法进 SwanBusiness + 用例文件按铁律一用例一文件；新方法同步 AW 方法指南 §2）
→ verify（pytest 真机冒烟 → 通过后 promote_image 转正 → 知识库 aw_status 更新 → 批次表打勾）
```

- 每批派发走 G1-G5 门禁；codegen 开工必读 AW 方法指南（防重复创建）
- 涉及 driver/base 层新增按 CLAUDE.md 规则 9 上报用户拍板
- 每批验证口径：新用例真机通过 + 存量 77 条收集数不回退 + 图片全部转正

## 4. 验收标准（计划完成定义）

1. `swan.py` / `swan_regression.py` / 登录域用例 **grep 不到运行时 click_accessibility/wait_accessibility**（仅剩 explorer 蓝图与 dump 辅助）
2. 回归方案 76 条用例全部有对应单方法用例文件且真机通过（§2.3 A1-A36 全部实现）
3. AW 方法指南与 swan.py 实际方法数一致
4. 图片资产：所有新截图经 image_ai 转正，无滞留草稿

## 5. 已完成前置（2026-10-12 基线）

一用例一文件铁律落地（26 文件）、回归 mixin 迁 business 层、AW 方法指南建立、规范收敛至 CLAUDE.md——补全工作在此基线上展开。

## 6. 范围外（明确不做）

TidiTree（web）与音箱屏（android）的 AW 建设——2026-10-12 用户拍板不纳入；其知识库/业务类空壳现状保留原样，后续如重启另行立计划。
