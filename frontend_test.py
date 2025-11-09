import requests
import json 



json_data = {
    "fileid": "testfile19999",
    "filename": "testfile.txt",
    "content":  "This is a test document to verify the summarization functionality of the FastAPI application. The document should be summarized correctly by the endpoint.",
    "user_id": "testuser456",
    "tag": "testtag",
    "length": 1000,
    "lang": "en",
    "additional_prompt": "Please ensure the summary is concise and highlights the main points."
}

responst = requests.post("http://0.0.0.0:8000/summarize", json=json_data)
    

print(responst.json())