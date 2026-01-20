import yaml


def get_test_data(test_data_path):
    case = []  # 存储测试用例名称
    http = []  # 存储请求对象
    expected = []  # 存储预期结果

    with open(test_data_path, encoding='utf-8') as f:
        dat = yaml.safe_load(f.read())
        test = dat['tests']
        for td in test:
            case.append(td.get('case', ''))
            http.append(td.get('http', {}))
            expected.append(td.get('expected', {}))
    parameters = list(zip(case, http, expected))
    return case, parameters