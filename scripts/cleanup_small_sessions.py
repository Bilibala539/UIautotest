#!/usr/bin/env python3
"""
清理服务器上用例数 < 10 的测试 session。
操作：
  1. 读远端 sessions/index.json，找出 total < 10 的 session id
  2. 从 index.json 移除这些条目
  3. 从 test_history.json 移除这些 session_id 的所有记录
  4. 删除远端对应的 session 目录（session.json + logs/）
"""

import io
import json
import sys

# Windows GBK 控制台兼容
if sys.platform == "win32":
    import io as _io
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    import paramiko
except ImportError:
    sys.exit("❌ 请先 pip install paramiko")

HOST      = "10.220.28.125"
USER      = "popoqa91"
PASS      = "123456"
REMOTE    = "/var/www/html/reports/sessions"
THRESHOLD = 10          # 用例数严格小于此值时删除


def main(dry_run: bool = False):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=30)
    sftp = ssh.open_sftp()

    def read_json(path, default):
        try:
            buf = io.BytesIO()
            sftp.getfo(path, buf)
            return json.loads(buf.getvalue().decode("utf-8"))
        except Exception:
            return default

    def write_json(path, data):
        buf = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
        sftp.putfo(buf, path)

    def rm_dir(path):
        """递归删除远端目录"""
        try:
            items = sftp.listdir_attr(path)
        except FileNotFoundError:
            return
        for item in items:
            full = f"{path}/{item.filename}"
            import stat
            if stat.S_ISDIR(item.st_mode):
                rm_dir(full)
            else:
                sftp.remove(full)
        sftp.rmdir(path)

    # ── 读 index.json ──────────────────────────────────────
    index = read_json(f"{REMOTE}/index.json", {"sessions": []})
    all_sessions = index.get("sessions", [])

    small = [s for s in all_sessions if s.get("total", 0) < THRESHOLD]
    keep  = [s for s in all_sessions if s.get("total", 0) >= THRESHOLD]

    if not small:
        print("✅ 没有用例数 < 10 的 session，无需清理")
        sftp.close(); ssh.close()
        return

    print(f"找到 {len(small)} 个待删除 session（共 {len(all_sessions)} 个）：")
    for s in small:
        print(f"  {s['id']}  total={s.get('total',0)}  ts={s.get('ts','')}")

    if dry_run:
        print("\n[dry-run] 以上是将被删除的条目，实际未执行任何修改")
        sftp.close(); ssh.close()
        return

    small_ids = {s["id"] for s in small}

    # ── 更新 test_history.json ─────────────────────────────
    hist = read_json(f"{REMOTE}/test_history.json", {})
    cleaned_keys = 0
    for key in list(hist.keys()):
        orig_len = len(hist[key])
        hist[key] = [r for r in hist[key] if r.get("session_id") not in small_ids]
        if len(hist[key]) < orig_len:
            cleaned_keys += 1
        if not hist[key]:
            del hist[key]
    write_json(f"{REMOTE}/test_history.json", hist)
    print(f"\n✅ test_history.json 已更新（清理了 {cleaned_keys} 个测试键的历史记录）")

    # ── 更新 index.json ────────────────────────────────────
    index["sessions"] = keep
    write_json(f"{REMOTE}/index.json", index)
    print(f"✅ index.json 已更新（保留 {len(keep)} 个 session）")

    # ── 删除远端 session 目录 ──────────────────────────────
    for sid in small_ids:
        path = f"{REMOTE}/{sid}"
        rm_dir(path)
        print(f"🗑️  已删除: sessions/{sid}/")

    sftp.close()
    ssh.close()
    print("\n✅ 清理完成")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    main(dry_run=dry)
