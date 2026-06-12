import paramiko, json, sys, base64, os

sys.stdout.reconfigure(encoding="utf-8")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("10.220.28.125", username="popoqa91", password="123456", timeout=15)

session_dir = "/var/www/html/reports/sessions/20260611_160134_parallel/logs"
save_dir = r"E:\UIAutotest\output\failure_screenshots"
os.makedirs(save_dir, exist_ok=True)

_, o, _ = ssh.exec_command(
    "cat /var/www/html/reports/sessions/20260611_160134_parallel/session.json"
)
data = json.loads(o.read().decode("utf-8", errors="replace"))

failed = [t for t in data.get("tests", []) if t.get("status") in ("failed", "error") and t.get("log")]

seen_logs = set()
for t in failed:
    log = t.get("log", "")
    name = t.get("node_id", "").split("::")[-1]
    file = t.get("node_id", "").split("/")[-1].replace(".py", "").replace("\\", "").replace(":", "_")[:40]
    if log in seen_logs:
        continue
    seen_logs.add(log)

    _, o2, _ = ssh.exec_command(
        f"grep -o 'data:image/png;base64,[A-Za-z0-9+/=]*' {session_dir}/{log} 2>/dev/null | tail -1"
    )
    b64 = o2.read().decode().strip()
    if b64 and "," in b64:
        img_data = base64.b64decode(b64.split(",")[1])
        save_path = os.path.join(save_dir, f"{file[:40]}.png")
        with open(save_path, "wb") as f:
            f.write(img_data)
        print(f"已保存: {file}")
    else:
        print(f"无截图: {file}")

ssh.close()
