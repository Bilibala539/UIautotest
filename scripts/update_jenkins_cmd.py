import requests

JENKINS = "http://10.220.28.153:8080"
session = requests.Session()
session.auth = ("popoqa", "popoqa163")
crumb = session.get(f"{JENKINS}/crumbIssuer/api/json").json()
session.headers[crumb["crumbRequestField"]] = crumb["crumb"]

config_bytes = session.get(f"{JENKINS}/job/Android-UIAutotest-Checklist/config.xml").content
config = config_bytes.decode("utf-8")

# batch 只做一件事：调 run_parallel.py，参数从 Jenkins 环境变量来
NEW_CMD = (
    "C:\\Users\\wb.menglingzhao02\\AppData\\Local\\Programs\\Python\\Python39\\python.exe"
    " E:\\UIAutotest\\scripts\\jenkins_run.py"
)

start = config.index("<command>") + len("<command>")
end = config.index("</command>")
new_config = config[:start] + NEW_CMD + config[end:]

resp = session.post(
    f"{JENKINS}/job/Android-UIAutotest-Checklist/config.xml",
    data=new_config.encode("utf-8"),
    headers={"Content-Type": "application/xml; charset=utf-8"},
    timeout=15
)
print(f"Status: {resp.status_code}")
