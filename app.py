from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import time
import uuid
import logging
import uvicorn 

import os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GEMINI_KEY")

logger = logging.getLogger("uvicorn")
app = FastAPI()

# 儲存任務結果的簡單字典（生產環境可換 Redis / DB）
tasks = {}

class Document(BaseModel):
    document: str

# 模擬耗時摘要任務
def summarize_document_task(task_id: str, document: str):
    logger.info(f"Starting background task {task_id}")
    time.sleep(5)  # 模擬長任務
    summary = f"Summarized content of: {document[:30]}..."
    tasks[task_id] = {"status": "SUCCESS", "summary": summary}
    logger.info(f"Task {task_id} finished")

@app.post("/summarize")
async def summarize(doc: Document, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())  # 生成唯一 task_id
    tasks[task_id] = {"status": "PENDING"}
    # 把長時間任務丟給 background_tasks
    background_tasks.add_task(summarize_document_task, task_id, doc.document)
    return {"task_id": task_id, "status": "PENDING"}

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    if task_id not in tasks:
        return {"error": "Task not found"}, 404
    return tasks[task_id]

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)