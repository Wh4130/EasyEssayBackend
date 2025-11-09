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
    "additional_prompt": "Please ensure the summary is concise and highlights the main points.",
    "db_url": "https://docs.google.com/spreadsheets/d/1m-bN4w5Wxvjp4KtMukwLI3yquWuRyXx367SajrvU84Q/edit?gid=455424109#gid=455424109"
}

# responst = requests.post("https://easyessaybackend.onrender.com/summarize", json=json_data)
responst = requests.post("http://127.0.0.1:8000/summarize", json=json_data)

    

print(responst.json())