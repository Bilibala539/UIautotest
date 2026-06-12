import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("10.220.28.125", username="popoqa91", password="123456", timeout=15)

_, o, _ = ssh.exec_command(
    'ssh -o StrictHostKeyChecking=no -o BatchMode=yes '
    '"wb.menglingzhao02@10.219.191.200" '
    '"tasklist /fi \"imagename eq python.exe\" /fo csv /nh 2>&1"'
)
print(o.read().decode("utf-8", errors="replace"))
ssh.close()
