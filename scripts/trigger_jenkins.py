import requests

JENKINS = "http://10.220.28.153:8080"
session = requests.Session()
session.auth = ("popoqa", "popoqa163")
crumb = session.get(f"{JENKINS}/crumbIssuer/api/json").json()
session.headers[crumb["crumbRequestField"]] = crumb["crumb"]

resp = session.post(
    f"{JENKINS}/job/Android-UIAutotest-Checklist/buildWithParameters",
    data={"EXECUTION_MODE": "并行", "N_INSTANCES": "4",
          "TEST_DIR": "tests/checklist", "BRANCH": "latest_online"},
    timeout=10
)
print(f"触发状态: {resp.status_code}")
