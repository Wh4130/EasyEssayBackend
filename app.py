from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import time
import uuid
import logging
import uvicorn 
import os
from dotenv import load_dotenv
from scripts.summarize import * 
from scripts.summarize import update_summary_to_db
load_dotenv()

from scripts.summarize import * 

key = os.getenv("GEMINI_KEY")

logger = logging.getLogger("uvicorn")
app = FastAPI()

# 儲存任務結果的簡單字典（生產環境可換 Redis / DB）
tasks = {}


# 模擬耗時摘要任務
def summarizeRUN(file_id: str, doc: Document):
    logger.info(f"Starting background task {file_id}")
    time.sleep(5)  # 模擬長任務
    result = update_summary_to_db(doc)
    tasks[file_id] = {"status": "SUCCESS", "result": result}
    logger.info(f"Task {file_id} finished")

@app.post("/summarize")
async def summarize(doc: Document, background_tasks: BackgroundTasks):
    tasks[doc.fileid] = {"fileid": doc.fileid, "status": "PENDING", "filename": doc.filename}

    # 把長時間任務丟給 background_tasks
    background_tasks.add_task(summarizeRUN, doc.fileid, doc)
    return tasks[doc.fileid]

@app.get("/result/{fileid}")
async def get_result(fileid: str):
    if fileid not in tasks:
        return {"error": "Task not found"}, 404
    return tasks[fileid]

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)