import requests
import json 

responst = requests.post("http://0.0.0.0:8000/summarize", json={"document": "This is a test document to verify the summarization functionality of the Flask application. The document should be summarized correctly by the endpoint."})

print(responst.json())