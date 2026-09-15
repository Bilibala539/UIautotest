# BUG 报告：SWAN-BUG-20260910-002

- 任务：`SWAN-20260910-001-feature-boundary`（B 线片 2，U5 密码模式状态矩阵）
- 分类：`anr + validation-missing`（高危候选，未定级未提单）
- 模块：`com.swan.network` 登录页 / 密码登入模式
- 基线：App `dev@4d1ed7b` / Core `dev@402853a`；APK v5.3.0（2026-09-04 安装）
- 现象：密码框无前端长度校验——6 位 "123456"（占位假值）即点亮登录键；点击后主线程 ANR 循环（FocusEvent 5s 超时，dropbox ErrorId 57f0fd98），"等待"无法恢复，仅 force-stop 可退出。对照：验证码模式手机号框同样只校验位数≥11 不校验号段（非法号段点击→行内红字 `login_error_text`，不发码）。
- 未决事实：**登录请求是否已发到服务端未确认**（ANR 阻塞在点击处理阶段）——2026-09-10 用户裁决：先记录本地 BUG 库，服务端核对（测试服查 13800138000/123456 到达记录）暂不执行，留待定级阶段决定。
- 证据：`results\SWAN-20260910-001-feature-boundary\executor\states-matrix.md` §11-12 + progress.md 片 2 段 + dropbox ANR trace（ErrorId 57f0fd98）
- 关联：与 SWAN-BUG-20260904-004（启动 ANR 候选 P-003）不同触发点——本条由文本输入/点击触发，佐证 P-003 嫌疑链路应从"启动时序"扩展至"输入链路"。
- 结论：证据齐备的高危候选。执行从已按探索边界终止深试。
- 后续：①定级时裁决是否做服务端到达核对；②逆向用例从加"前端长度/号段校验缺失"维度。
