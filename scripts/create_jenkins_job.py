import requests

JENKINS = "http://10.220.28.153:8080"
session = requests.Session()
session.auth = ("popoqa", "popoqa163")
crumb = session.get(f"{JENKINS}/crumbIssuer/api/json").json()
session.headers[crumb["crumbRequestField"]] = crumb["crumb"]

config_bytes = session.get(f"{JENKINS}/job/Android-UIAutotest-Checklist/config.xml").content
config = config_bytes.decode("utf-8")

# 替换参数定义区域
OLD_PARAMS = config[config.index("<parameterDefinitions>"):config.index("</parameterDefinitions>") + len("</parameterDefinitions>")]

NEW_PARAMS = """<parameterDefinitions>
        <hudson.model.ChoiceParameterDefinition>
          <name>EXECUTION_MODE</name>
          <description>执行模式</description>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              <string>并行</string>
              <string>串行</string>
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
        <hudson.model.ChoiceParameterDefinition>
          <name>N_INSTANCES</name>
          <description>MuMu 并行实例数（串行模式时忽略）</description>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              <string>4</string>
              <string>3</string>
              <string>2</string>
              <string>1</string>
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
        <hudson.model.ChoiceParameterDefinition>
          <name>REINSTALL</name>
          <description>是否重启 MuMu 并重装 POPO 客户端</description>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              <string>是</string>
              <string>否</string>
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>BRANCH</name>
          <description>REINSTALL=是 时生效：latest_online=自动取正式服最新包；或填分支名如 release_4.23.5</description>
          <defaultValue>latest_online</defaultValue>
          <trim>true</trim>
        </hudson.model.StringParameterDefinition>
        <hudson.model.ChoiceParameterDefinition>
          <name>RUN_TESTS</name>
          <description>是否执行 checklist 用例</description>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              <string>是</string>
              <string>否</string>
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>TEST_DIR</name>
          <description>测试目录或文件，如 tests/checklist、tests/add（RUN_TESTS=是 时生效）</description>
          <defaultValue>tests/checklist</defaultValue>
          <trim>true</trim>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>"""

new_config = config.replace(OLD_PARAMS, NEW_PARAMS)

resp = session.post(
    f"{JENKINS}/job/Android-UIAutotest-Checklist/config.xml",
    data=new_config.encode("utf-8"),
    headers={"Content-Type": "application/xml; charset=utf-8"},
    timeout=15
)
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(resp.text[:200])
