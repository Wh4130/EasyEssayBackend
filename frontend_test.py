import requests
import json 
import argparse

def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", 
                        required = True, 
                        choices = [
                            "summarize", "pinecone", "chat", "health"
                        ]
                        )
    parser.add_argument("--type", 
                        choices = [
                            "local", "render"
                        ],
                        default = "local"
                        )
    return parser.parse_args()



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

def test_summarize(type):
    if type == "render":
        response = requests.post("https://easyessaybackend.onrender.com/summarize", json=json_data)
    else:
        response = requests.post("http://127.0.0.1:8000/summarize", json=json_data)

    print(f"api test result: {response}")
    print(response.json())

def test_pinecone(type):
    if type == "render":
        # TODO
        response = requests.post("https://easyessaybackend.onrender.com/upsert_to_pinecone", json=json_data)
    else:
        response = requests.post("http://127.0.0.1:8000/upsert_to_pinecone", json=json_data)

    print(f"api test result: {response}")
    print(response.json())

def test_health(type):
    if type == "render":
        # TODO
        response = requests.get("https://easyessaybackend.onrender.com/health")
    else:
        response = requests.get("http://127.0.0.1:8000/health")

    print(response)
    print(response.json())

    
def main():
    args = parse_arg()

    if args.api == "summarize":
        test_summarize(args.type)
    elif args.api == "pinecone":
        test_pinecone(args.type)
    elif args.api == "health":
        test_health(args.type)

if __name__ == "__main__":
    main()