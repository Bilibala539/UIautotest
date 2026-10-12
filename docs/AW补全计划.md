# AW 补全计划（三项目全景）

> 目标：把自动化工程的 AW 业务层从"Swan 半成品 + 另两端空壳"补全到"三项目全覆盖、运行时零 key、每域有方法有用例"。
> 本计划是待办清单的执行拆解，落批次跟踪；每批完成后更新 §2 批次表状态并同步 AW 方法指南。
> 创建：2026-10-12（分支 feature/swan-aw）。维护：主会话（orchestrator）。

## 0. 现状盘点（2026-10-12）

| 项目 | 业务方法 | 用例 | 知识库 | 图片资产 | 结论 |
|---|---|---|---|---|---|
| Swan（flutter） | 34 公开业务方法（+回归 mixin 三件套） | 28 文件 / 77 条 | 48 页 + 2 digest | 90 正式 + 21 暂存 | **主线，完成约 55%**（域3/4/7/8 + 登录存量） |
| TidiTree（web） | **0**（tiditree.py 空壳 12 行） | **0** | 仅 2 页 | 0 | 空壳，基建齐全（browser fixture/并行）待重建 |
| 音箱屏（android） | **1**（android.py 空壳 24 行） | **0** | **0 页** | 0 | 全空白，需探索先行 |
| 公共 | AWBase/FlutterBaseAW 基础操作齐备（find_image_rect/wait_toast/region_changed/drag_on_template/connect_wifi 等） | — | MCP 图谱层可用（vector_kb 缺依赖未建） | — | 基础层不再是瓶颈 |

## 1. 三个工作流

```
W1 Swan 补全收尾（主线）   —— 存量 key 迁移 + 6 个缺失域，沿回归方案 §2.3/§6 批次推进
W2 音箱屏(android) 从零建  —— explorer 探索先行 → 知识库 → element → codegen
W3 TidiTree(web) 重建     —— 前提：用户确认重启优先级（当前无设备/环境信息）
```

## 2. 批次总表（W1 为主线，按依赖排序）

| 批次 | 内容 | 产出（方法/用例文件/图片） | 依赖/阻塞 | 状态 |
|---|---|---|---|---|
| **W1-A 存量 key 迁移** | 登录域 5 方法（login_by_sms/login_with_password/logout_if_needed/enter_sms_code_step/fill_sms_code）+ 导航 3 方法（go_home/go_bottom_tab/tab 断言）重写为 [图]/[OCR]；登录页/首页锚点图补截 | ~8 方法改造 / 登录域 12 用例文件回归验证 / 新图约 6 张 | 无外部阻塞，**最先做**（解锁全工程零 key） | ⬜ 待开工 |
| **W1-B 域1 启动登录新增** | A4 微信登录 / A5 微博登录（跨 App 授权）、A6 冷启动断言 / A7 后台恢复 / A8 绑定手机返回；用例 1-3、6-8 落地 | +5 方法 / +5 用例文件 / 新图约 4 张 | ⑤ 三方 App 登录态（微信/微博账号预置） | ⬜ 待开工 |
| **W1-C 域5 平台授权** | A24 authorize_platform / A25 assert_platform_state / A26 deauthorize_platform；用例 32-37 | +3 方法 / +6 用例文件（parametrize 平台×入口） / 新图约 6 张 | ⑤ 三方登录态 + ⑥ 授权半自动口径拍板 | ⬜ 待开工 |
| **W1-D 域6 平台内容页** | A27 open_platform / A28 open_platform_entry；用例 38-40 | +2 方法 / +3 用例文件 / 新图 2 张 | explorer 先补 QQ音乐/网易云/酷狗 3 个主页 draft | ⬜ 待开工（可与 W1-C 并行探索） |
| **W1-E 域2 配网** | A9 provision 统一入口 / A10 BLE / A11 热点（connect_wifi 已实现）；用例 9-10 | +3 方法 / +2 用例文件 / 新图约 5 张 | ④ 1 台**未配网**设备 + D2 已实现无阻塞 | ⬜ 待开工 |
| **W1-F 域9 多房间** | A35 sync_rooms / A36 assert_room_synced；用例 73-76 | +2 方法 / +4 用例文件 / 新图约 3 张 | ④ ≥3 台 A31 + 3 台 H76D/H76G（rig 最多的一批） | ⬜ 待开工 |
| **W1-G Driver 尾巴** | D3 get_foreground_package（热启动恢复断言辅助，可选） | +1 driver 方法 | 框架层，**须用户拍板**（规则 9） | ⬜ 待拍板 |
| **W2 音箱屏从零** | 阶段1：explorer 探索核心页（首页/设置/播放）建 knowledge/android 骨架；阶段2：element 截首批元素；阶段3：codegen 建 AndroidBusiness 首批 10-15 方法 + 冒烟用例 | +10-15 方法 / +3-5 用例文件 / 新图约 15 张 / 知识库 0→8 页 | **用户确认：项目名/设备到位情况/首批功能范围** | ⬜ 需输入 |
| **W3 TidiTree 重建** | tiditree.py 业务层按 checklist 模块重建（登录/搜索/消息等）+ 用例落地 | 视 checklist 范围 | **用户确认：是否重启该项目及其优先级** | ⬜ 需输入 |

建议执行序：**W1-A → W1-B/D(并行) → W1-C → W1-E → W1-F**；W2 在 W1-A 落地后由 explorer 并行启动探索；W3 等用户拍板。

## 3. 外部阻塞清单（用户侧待办）

| # | 事项 | 影响批次 |
|---|---|---|
| ④ | 设备 rig：未配网设备 ×1（W1-E）；WiFi 音箱在线 ×2（切换/播放）；A31×3 + H76D/H76G×3（W1-F） | W1-E、W1-F |
| ⑤ | 三方 App 登录态预置：微信/微博/QQ音乐/网易云/酷狗账号在测试手机不退出 | W1-B、W1-C、W1-D |
| ⑥ | 授权用例半自动口径：三方 App 内最终授权步（人工辅助 or OCR 兜底） | W1-C |
| D3 | driver 层 get_foreground_package 是否批准（框架层，规则 9） | W1-G |
| — | 音箱屏项目：项目名/设备/首批功能范围 | W2 |
| — | TidiTree 是否重启及优先级 | W3 |

## 4. 编排方式（每批一个交付周期）

```
explorer（需知识库的批次先跑，如 W1-D/W2）→ element（截图进 image_ai/flutter，登记常量）
→ codegen（方法进 SwanBusiness + 用例文件按铁律一用例一文件；新方法同步 AW 方法指南 §2）
→ verify（pytest 真机冒烟 → 通过后 promote_image 转正 → 知识库 aw_status 更新 → 批次表打勾）
```

- 每批派发走 G1-G5 门禁；codegen 开工必读 AW 方法指南（防重复创建）
- 涉及 driver/base 层新增按 CLAUDE.md 规则 9 上报用户拍板
- 每批验证口径：新用例真机通过 + 存量 77 条收集数不回退 + 图片全部转正

## 5. 验收标准（全计划完成定义）

1. `swan.py` / `swan_regression.py` / 登录域用例 **grep 不到运行时 click_accessibility/wait_accessibility**（仅剩 explorer 蓝图与 dump 辅助）
2. 回归方案 76 条用例全部有对应单方法用例文件且真机通过（§2.3 A1-A36 全部实现）
3. `knowledge/android/` ≥10 页 + AndroidBusiness 首批方法 + 冒烟用例绿
4. TidiTree：视 W3 拍板结果（若重启，checklist 模块逐域重建）
5. AW 方法指南与三项目实际方法数一致

## 6. 已完成前置（本次计划的基础，2026-10-12）

一用例一文件铁律落地（26 文件）、回归 mixin 迁 business 层、AW 方法指南建立、规范收敛至 CLAUDE.md——补全工作在此基线上展开。
