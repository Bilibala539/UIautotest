# Laya 本地决策模型 POC

测试"文字用例是否靠谱"能否用 Laya（Convai Innovations 开源的 Jev 兼容决策模型）本地判定。
分支：`laya-poc`（独立于 master 开发线）。

## 目录

| 目录 | 内容 | 部署位置 |
|---|---|---|
| `platform-167/` | POC 脚本（用例抽取 + 三实验 + 诊断） | .167 `~/laya_poc/` |
| `platform-167/results/` | 实验数据（164 条用例 + 结果 CSV/JSON + 诊断日志） | 同上 |
| `judge-176/` | GPU 判定 HTTP 服务 | .176 `~/laya-judge/` |
| `leader/` | 两级 agent 编排：小领导章程 ×2 + 引导脚本 | 各机 `~/leader/LEADER.md` |

## POC 设计（防作弊是核心）

用例从平台库只读抽取（`extract.py` → `cases.json`，164 条文本用例，剥掉 `name:`/`domain:` 行防模型偷答案）：

- **EXP1 一致性**：真标题 vs 错配标题（sham = `cases[(i+7)%n]`），noul 判断"标题与内容是否同一场景"。真错配对天然构成 ground truth，**不用人工标注**。
- **EXP2 域分类**：25 条带 domain 标签的用例做 choice 分类。
- **EXP3 可验证性**：noul 判断"预期结果是否明确可观察"。

## POC 结论（2026-09-22，诊断闭环，详见 leader/REPORT-167-001.md）

| 实验 | 结果 | 判读 |
|---|---|---|
| EXP1 一致性 | true mean=0.991 / sham mean=0.992，acc≈0.50（随机） | **失败**：noul 对同体裁长文本饱和 |
| EXP2 域分类 | top1=0.279（7×随机）、top3=0.395 | 信号真实但 choice 头塌缩（30/43 塌到"设备管理与配网"，错误预测置信 0.91+） |
| EXP3 可验证性 | 全部 ≥0.5 | 饱和，无区分度 |

**根因：模型能力边界，非推理配置。** 四个假设全部被数据排除：中文指令无效 ✗（琐碎 ZH 0.313/0.045 方向正确）、max_len 超界 ✗（序列 p50=443/max=946，从未触顶）、声明格式 ✗（3 变体同饱和）、英文 checkpoint ✗（EN ckpt 同样 acc 0.537，饱和与语言无关）。关键对照：长用例体 + 无关假声明"天空是绿色" → noul=0.323 不饱和 → 头做的是粗话题匹配，标题↔内容同话题即判 true。multilingual checkpoint 仅 15987 updates / 4.97h 单卡训练量。mmBERT 余弦基线同样失败（acc 0.537）→ 廉价检索路线也不通。

**修复路线**：
1. 开放语义判定（一致性/可验证性/域归类）→ 转 LLM 通道（judge 服务形态不变）
2. laya 保留场景：短文本属性级 noul 断言、强区分小选项（k≤5）choice；上线前需重做置信校准
3. 不建议：本地微调（训练栈未随 pip 发布、164 条样本远不够）、翻译走 EN 检查点（已证与语言无关）

## GPU judge 服务（.176:8089）—— 已上线验收通过

- 架构：单实例 HTTP 服务，各测试机调 `POST /predict {"state","questions"}`，避免每台机器装 CUDA
- `judge_server.py`：stdlib ThreadingHTTPServer，token 鉴权（`X-Judge-Token`，token.txt 不入库），全局锁串行 predict，warmup 预热，`GET /health`
- `start.sh`：HF 镜像 + venv 启动；`laya-judge.service`：systemd 常驻（enable 自启，Restart=on-failure）
- 驱动 580.178.04 / CUDA 13.0；torch 2.14.0+cu126；模型常驻显存 1753MiB；防火墙 8089 限内网段
- **实测**（.167→.176 内网，真实中文负载）：端到端 11-25ms/请求；服务端冷 108.6ms / 热 ~20ms，device=cuda；单连接约 50-90 QPS（瓶颈在串行锁，GPU 计算本身 1-2ms）
- **调用方注意**：choice 型问题必须带 `criteria` 字典，否则 500；noul 不需要。中文负载必须 UTF-8（Windows curl 默认 GBK 会被拒）
- 部署经过见 `leader/REPORT-176-001/003/004.md`（驱动修复 176-002、换源与 wheelhouse 抢救 176-003、模型内网直传 176-004）

## 两级 agent 编排

大领导（.229 主会话）派活 → 小领导（各机 tmux `leader` 会话里的常驻 claude）执行，可自起 teammate。任务进 `~/leader/inbox/<ts>.md`，报告出 `~/leader/outbox/<ts>.md`。章程见 `leader/LEADER-m*.md`：

- m167：平台库严格只读、不停任何服务、不改 /opt/uiautotest、不 apt
- m176：绝不碰 Jenkins 与 /opt/build-env、不重启机器，sudo 仅限 NVIDIA 驱动 / judge 单元 / 8089 防火墙
