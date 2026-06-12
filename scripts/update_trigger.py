import requests

JENKINS = "http://10.220.28.153:8080"
session = requests.Session()
session.auth = ("popoqa", "popoqa163")
crumb = session.get(f"{JENKINS}/crumbIssuer/api/json").json()
session.headers[crumb["crumbRequestField"]] = crumb["crumb"]

# 拉当前配置
config = session.get(f"{JENKINS}/job/Android-UIAutotest-Checklist/config.xml").text

# 替换 trigger spec
import re
config = re.sub(r'<spec>.*?</spec>', '<spec>20 0 * * *</spec>', config)

resp = session.post(
    f"{JENKINS}/job/Android-UIAutotest-Checklist/config.xml",
    data=config.encode("utf-8"),
    headers={"Content-Type": "application/xml; charset=utf-8"},
    timeout=15
)
print(f"Status: {resp.status_code}")
