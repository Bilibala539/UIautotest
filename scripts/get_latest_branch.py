import urllib.request, json, sys

try:
    url = "http://10.220.28.152:8081/api/device_type/android/online/1/1/"
    data = json.loads(urllib.request.urlopen(url, timeout=10).read())
    branch = data["package"][0]["branch_name"].replace("origin/", "")
    sys.stdout.write(branch)
except Exception as e:
    sys.stderr.write(str(e))
    sys.exit(1)
