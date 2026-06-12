import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("10.220.28.125", username="popoqa91", password="123456", timeout=15)

_, o, e = ssh.exec_command(
    'ssh -o StrictHostKeyChecking=no -o BatchMode=yes '
    '"wb.menglingzhao02@10.219.191.200" '
    '"schtasks /run /tn UIAutotestNightly" 2>&1'
)
import sys
sys.stdout.buffer.write(o.read())
sys.stdout.buffer.write(e.read())
ssh.close()
