import requests

JENKINS = "http://10.220.28.153:8080"
session = requests.Session()
session.auth = ("popoqa", "popoqa163")
crumb = session.get(f"{JENKINS}/crumbIssuer/api/json").json()
session.headers[crumb["crumbRequestField"]] = crumb["crumb"]

# 拉当前配置
current = session.get(f"{JENKINS}/job/Android-UIAutotest-Checklist/config.xml").text
print(current)
