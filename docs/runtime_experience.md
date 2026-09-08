# 运行时经验知识库（子 Agent 执行经验沉淀）

> 按编排约定，子 agent 返回 [完成] 后由 orchestrator 把新验证的 AW 方法 / 新坑追加到对应表格，供向量检索注入。
> 记录格式：场景 / 正确做法 / 来源与日期。

## Swan 项目（flutter）

| 场景 | 正确做法 | 来源 |
|------|----------|------|
| 发送验证码 | 点"下一步"（`login_submit_button`）即自动发送，页面无"获取验证码"按钮 | explorer 2026-09-08 |
| 验证码输入 | 4 位填满自动提交，无需点确认；等 `tab_me` 出现判成功 | explorer 2026-09-08 |
| 取码链路 | App 触发后 `GET <SWAN_OTP_GATEWAY>/api/test/otp/latest?phone=` 取码；开发接口为 `https://testnetwork.hivi.com/api/user/captcha/mockCode`（必须带 api 前缀） | orchestrator 2026-09-08 |
| 拿未登录态 | 杀进程无效（登录态持久）、OPPO 禁 pm clear；唯一途径：我的→个人信息→退出登入 | element 2026-09-08 |
| 登录页"下一步"图 | `swan_login_submit_btn` 模板是置灰态，仅作存在性断言；点击一律走 key `login_submit_button` | element 2026-09-08 |
| 新建歌单弹窗 | 第一次 press_back 只收键盘，需两次返回才关弹窗 | verify 2026-09-08 |
| 音质弹层关闭判定 | 不能用"音质设置"文案判（列表项同名），判 OCR"流畅音质"/"完成"消失 | verify 2026-09-08 |
| 设备卡定位 | key 按设备 UUID 动态拼接：`wifi_device_card_<UUID>`，用前缀匹配 | explorer 2026-09-08 |
| 危险入口 | `person_info_cancel_account_button`（注销账号）紧邻退出登入，⛔ 任何自动化禁止点击 | explorer 2026-09-08 |
| 真实音箱安全 | 播放/音量/同步/授权/充值类按钮只做 image_exists，不下发点击 | 编排约定 2026-09-08 |

## 框架 / 环境

| 场景 | 正确做法 | 来源 |
|------|----------|------|
| 元素图转正门禁 | image_ai 暂存 → 离线匹配（scripts/verify_element_match.py，≥0.8）→ verify 真机点击反应 → 才 promote_image；禁止跳步 | 编排约定 2026-09-08 |
| 嵌入模型下载 | huggingface / hf-mirror 均被网络拦截；用 ModelScope 下载到本地 `models/`，管线经 `UIAUTOTEST_EMBEDDING_MODEL` 指向 | orchestrator 2026-09-08 |
| protobuf 版本 | 必须钉 3.20.2：chromadb 会把它顶到 7.x 弄坏 PaddleOCR；连带 googleapis-common-protos 钉 1.63.2 | orchestrator 2026-09-08 |
| paddle+torch 同进程 | 先 import paddle 再 import torch 会 shm.dll 崩溃；两者分进程跑（向量管线不含 paddle，天然安全） | orchestrator 2026-09-08 |
| 验证码页返回 | press_back 会退出 App（不是回登录页）；重启后回登录页 | element 2026-09-08 |
