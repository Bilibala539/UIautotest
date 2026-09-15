# 登录用例翻译评级表(YAML → pytest 可执行度分级)

> 翻译对象:`SWAN-20260907-002-login-positive-cases.yaml`(47 条 L2 正向 14 条中的 14 条)与 `SWAN-20260907-003-login-negative-L2.yaml`(逆向 33 条,尚未翻译)。
> 评级口径:**全自动**(黑盒 UI 可跑)/ **受限**(需特殊前置:清数据/服务端控制/OCR 视觉通道)/ **BLOCKED**(依赖第三方真实授权环境)/ **禁止**(不可逆或危险操作)。
> 数据映射:YAML 的 TEST-SYNTHETIC 池(13800000002 / SynthPass01 等)在测试环境未必预置,翻译件统一改走 `.env.local` 真实账号(users("swan") 注入)。

## 正向 14 条逐条评级

| case_id | 名称 | 评级 | 产物 | 说明 |
|---|---|---|---|---|
| POS-001 | 冷启动隐私弹窗同意 | 受限 | — | 需"首次安装/清数据"才能触发隐私弹窗;OPPO 真机无 `pm clear` 权限,拿不到首启态。待模拟器或可清数据设备 |
| POS-002 | 短信两步登录主路径 | 全自动 | `test_swan_login_positive.py::test_pos002` | 中间态(验证码页出现)+收口态(进首页)已断言;请求体冗余字段/三处 token 同步为抓包级,不覆盖 |
| POS-003 | 密码登录主路径 | 全自动(已有) | `test_swan_password_login.py::test_password_login_success` | 融合前已实现,不重复 |
| POS-004 | 短信⇄密码互切 | 全自动(已有) | `test_swan_password_login.py::test_login_page_toggle` | 同上 |
| POS-005 | 协议勾选联动 | 全自动 | `test_swan_login_positive.py::test_pos005` | 黑盒近似:未勾协议点主按钮不切页;第三方图标可点性不发起真实授权,未覆盖 |
| POS-006 | 60s 倒计时/同号复用 | 受限 | — | 倒计时文本需 OCR/视觉通道;`login-resend-code-button` 仅 ValueKey 轨(Semantics 未 dump 到);请求次数断言需抓包 |
| POS-007 | 满 4 位自动提交边界 | 全自动 | `test_swan_login_positive.py::test_pos007` | 3 位不提交 + 第 4 位自动提交均断言;请求计数为抓包级,不覆盖 |
| POS-008 | 第三方登录成功收口 | BLOCKED | — | third-party-required:依赖设备装微信/微博并完成真实授权(YAML 自带 BLOCKED-risk 标注) |
| POS-009 | 50015→绑定手机号 | BLOCKED | — | third-party-required + 需服务端预置未绑定账号 |
| POS-010 | 冷启动 token 恢复免登 | 全自动 | `test_swan_login_positive.py::test_pos010` | 杀进程重启直达首页;Authorization 注入/日活节流为抓包级,不覆盖 |
| POS-011 | 登出触发点1(退出登入) | 全自动 | `test_swan_login_positive.py::test_pos011` | 四步路径+落地登录页已断言;"先 push 二级页再登出验清栈"子场景简化为从个人信息页登出 |
| POS-012 | 登出触发点2(注销账号) | **禁止** | — | 注销不可逆,页面知识库明确 `person_info_cancel_account_button` 禁止自动化点击;如需覆盖,人工执行一次性虚构账号 |
| POS-013 | 登出触发点3(30003 会话失效) | 受限 | — | 需测试环境可控让某接口返回 30003(服务端配合),黑盒无法自造失效码 |
| POS-014 | 登出触发点4(切服登出) | 受限 | — | 涉及"关于我们"切服,改写本机服务端配置;需人工确认环境后执行,禁止切线上 |

## 汇总

- 全自动:9 条(2 条融合前已有,5 条本次翻译,另有 2 条由既有文件覆盖)
- 受限:3 条(POS-001 / 006 / 013 / 014 中标注)
- BLOCKED:2 条(第三方授权依赖)
- 禁止:1 条(POS-012 注销)

## 逆向 33 条(未翻译)

`SWAN-20260907-003-login-negative-L2.yaml` 尚未翻译。已知可先行的方向:错误密码拒绝已在 `test_swan_password_login.py::test_wrong_password_rejected` 覆盖;空手机号/未勾协议/短验证码等纯 UI 逆向可复用本次封装的方法直译。待正向试点真机跑通后铺开。
