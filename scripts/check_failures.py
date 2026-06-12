import paramiko, json, sys

sys.stdout.reconfigure(encoding="utf-8")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("10.220.28.125", username="popoqa91", password="123456", timeout=15)

session_dir = "/var/www/html/reports/sessions/20260611_160134_parallel/logs"

_, o, _ = ssh.exec_command(
    "cat /var/www/html/reports/sessions/20260611_160134_parallel/session.json"
)
data = json.loads(o.read().decode("utf-8", errors="replace"))

failed = [t for t in data.get("tests", []) if t.get("status") in ("failed", "error")]
print(f"失败用例数: {len(failed)}\n")

seen = set()
for t in failed:
    name = t.get("node_id", t.get("name", "?"))
    short = name.split("::")[-1] if "::" in name else name
    file = name.split("::")[0].split("/")[-1] if "::" in name else name
    log = t.get("log", "")
    if file in seen:
        continue
    seen.add(file)
    print(f"用例: {file} > {short}")
    if log:
        _, o2, _ = ssh.exec_command(
            f"grep -h 'AssertionError\\|未找到图片\\|未找到文字\\|超时\\|timeout\\|image_exists' "
            f"{session_dir}/{log} 2>/dev/null | tail -3"
        )
        result = o2.read().decode("utf-8", errors="replace").strip()
        print(f"  原因: {result[:200]}" if result else "  (日志无匹配行)")
    print()

ssh.close()
