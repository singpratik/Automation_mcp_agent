
import requests

task = {
    "type": "api",
    "method": "GET",
    "url": "https://jsonplaceholder.typicode.com/posts/1"
}

res = requests.post("http://localhost:8000/task/", json=task)
print(res.json())
