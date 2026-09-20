# YAML 用例正式 schema(① loader / 驱动约定)

> 文字用例与自动化脚本用例的**正式绑定载体**:同一 case_id 下,人读步骤与机读
> action 序列共存。文件放 `cases/driver/<module>/<CASE_ID>.yaml`,由
> `tests/flutter/test_case_driver.py` 自动发现并参数化执行。
> AI 多 agent 产出物也收敛为该格式(YAML + AW 方法补丁),不自由生成 py 脚本。

## 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| case_id | ✅ | 与文字用例编号一致(POS-002 等),用于执行历史聚合 |
| title | ✅ | 一句话用例名 |
| module | ✅ | 所属模块(login / search / …) |
| priority | | P0/P1/P2 |
| source | | 来源:文字用例路径或 `bug:SWAN-BUG-xxx`(bug 单来源追溯) |
| linked_case_id | | **frontmatter 专用**(同步映射):声明与平台文字用例的映射,须填完整编号(如 `LOGIN-L2-POS-002`);缺省时 sync_cases.py 走"路径锁定+编号后缀唯一命中"推断,标弱关联 |
| preconditions | | 前置条件(人读;状态归一化由 driver/setup 负责) |
| steps | ✅ | 顺序步骤列表,见下 |
| expected | | 预期结果(人读) |

## step 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| action | ✅ | AW/业务方法名,必须在允许名单内(基础 AW 显式名单 + SwanBusiness 公开方法) |
| args | | 关键字参数映射,支持 `${VAR}` 插值 |
| desc | | 文字步骤(人读;与文字用例对应的那一列) |
| assert | | 默认 true:布尔型基础动作返回 falsy 即断言失败;业务方法内部自带 assert |

## 插值变量

| 变量 | 来源 |
|---|---|
| `${phone}` | 测试账号手机号(.env.local SWAN_PHONE) |
| `${otp}` | otp-gateway 实时取码(惰性:真被用到才请求) |
| `${其他}` | 环境变量;未定义直接报错,不带病执行 |

## 纪律

- 测试数据一律 TEST-SYNTHETIC;真实账号只走 `${phone}`(.env.local),不写进 YAML
- 每条用例最多发 1 次验证码、试 1 次错密码(防频控锁号)
- 注销账号等不可逆动作禁止出现在 YAML(不会进允许名单)
- 坐标固化禁止:定位一律走 accessibility key(语义树是 key 唯一合法来源)
