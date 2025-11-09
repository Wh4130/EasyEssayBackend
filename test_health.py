import requests
import json 

responst = requests.get("http://0.0.0.0:8000/result/7baa6609-7f20-4ebd-8c39-94fc2ade9218")

print(responst.json())