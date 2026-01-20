import requests as requests
import pytest
from utils.commonlib import get_test_data

cases, list_params = get_test_data(r'E:\UIAutotest\data\test_in_theaters.yaml')



class TestInTheaters(object):
    @pytest.mark.parametrize("case, http, expected", list(list_params), ids=cases)
    def test_in_theaters(self, case, http, expected):
        host = "http://api.douban.com"
        path = "/v2/movie/in_theaters"
        params = {"apikey": "0df993c66c0c636e29ecbb5344252a4a",
                  "start": 0,
                  "count": 10
                  }
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }
        r = requests.request(list_params[0][1]["method"],
                             url=host + list_params[0][1]["path"],
                             headers=list_params[0][1]["headers"],
                             params=list_params[0][1]["params"])
        response = r.json()
        print(response["msg"])
        print(response["code"])
        assert response["msg"]
        assert response["code"]
