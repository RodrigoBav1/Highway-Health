import requests
from requests.structures import CaseInsensitiveDict

url = "https://weather.hereapi.com/v3/report"
url2 = "https://account.api.here/apps/yVwpwlZLYAUSxHLAKXeZ/accessKeys"
headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
headers["Authorization"] = "Bearer 3cYsPZh-SYjVq3oYPkD5Qg"


resp = requests.get(url, headers=headers)
# resp = requests.get(url2)

print(resp.json())
