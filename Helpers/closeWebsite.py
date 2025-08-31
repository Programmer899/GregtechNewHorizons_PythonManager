import requests

try:
    response = requests.get('http://127.0.0.1:8080/closeWebsite')
    print(response.content)
except OSError as e:
    # print(e)
    pass