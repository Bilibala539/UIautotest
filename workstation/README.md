# workstation —— Swan 功能地图工作站后端

> 收编于 2026-10-13 用例域整合 P2(分支 feature/case-domain)。这是工作站后端**唯一受版本管理的副本**;运行实例在 .167 `/opt/app/server/serve.py`,改动以本目录为源、改完部署回 /opt/app。

## 身份

- Swan 功能地图工作站(:8090)的单文件后端,**纯 Python 标准库**(ThreadingHTTPServer + sqlite3),无第三方依赖
- 前端为 React 构建产物(`/opt/app` 下),不在本仓库;本目录只管后端逻辑
- md5 `1081a5f` 与 .167 运行实例一致(2026-10-13 部署时核对)

## 共库架构(一库两服务)

与测试平台(`dashboard/server.py`,:8080)**共用唯一库** `/opt/uiautotest/output/dashboard.sqlite3` 的 `case_defs` 表——展示、人审、用例增删改查打同一张表。方案详见 `docs/用例域整合计划.md`。

| 环境变量 | 默认 | 说明 |
|---|---|---|
| `SWAN_CASE_DB` | `/opt/uiautotest/output/dashboard.sqlite3` | 共库路径 |
| `SWAN_CASE_PRIMARY_VER` | `0.3.0` | 走共库的工作站版本号;其他版本(如 0.2.0 demo)走旧文件只读,POST 人审/CRUD 返回 409 |

- 版本双源:`CASE_PRIMARY_VER` 的用例数据读 `case_defs`(structured 还原原始报文 + review_meta 叠加人审态);旧版本读 `data/versions/<v>/cases.json` 文件(只读)
- 人审 POST 三件套(gate/decision/batch)直接 UPDATE `review_meta`,`human_confirmed` 联动;`audit.jsonl` 照旧追加
- 用例 CRUD(POST/PUT/DELETE `/api/review/cases`)与测试平台写同一张表
- SQLite WAL + busy_timeout=15000

## 部署流程(改完 serve.py 后)

```bash
# 1. 本地改 workstation/serve.py
# 2. 推到 .167 并替换(sudo;属主 autotest)
scp workstation/serve.py 192.168.12.167:/tmp/serve.py
ssh 192.168.12.167 "sudo cp /tmp/serve.py /opt/app/server/serve.py && sudo chown autotest:autotest /opt/app/server/serve.py && sudo systemctl restart swan-map-station"
# 3. md5 核对 + 健康检查
ssh 192.168.12.167 "md5sum /opt/app/server/serve.py; curl -s http://127.0.0.1:8090/api/review/state | head -c 200"
```

注意:`/opt/app` 属主为 **autotest**(2026-10-13 统一),systemd 单元 `swan-map-station.service` 以 autotest 运行;jks 用户操作该目录需 sudo。

## 验证基线(2026-10-13 P2)

改版前后 `/api/review/cases` 1060 条逐字段 0 差异、顺序一致(模块按 sort_order JOIN);工作站审一条 → 测试平台 human_confirmed 即变;CRUD 建/改/删全通;demo 版只读 409。
