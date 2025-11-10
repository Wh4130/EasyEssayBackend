from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import time
import pandas 
import uuid
import logging
import uvicorn 
import os
from dotenv import load_dotenv
from scripts.summarize import * 
from scripts.summarize import update_summary_to_db
from scripts.db_conn import *
from schema.schema import Document
from utils import *
load_dotenv()

from scripts.summarize import * 

key = os.getenv("GEMINI_KEY")

logger = logging.getLogger("uvicorn")
app = FastAPI()

class Summarizer:

    @staticmethod
    def create_row(doc: Document):
        """create a new row in the user doc worksheet"""
        instance = [
            doc.fileid,
            doc.filename,
            "PENDING",
            "PENDING",
            "PENDING",
            doc.tag
        ]
        GSDB_Connect.append_row(doc.db_url, instance)
        logger.info(f"Created new row in DB for fileid: {doc.fileid}")

    @staticmethod
    def update_summary_to_row(doc: Document, summary: str):
        """update the summary field in the user doc worksheet"""

        # Acquire lock
        GSDB_Connect.acquire_lock(
            sheet_id = GSDB_Connect.extract_sheet_id(doc.db_url),
            worksheet_name = "user_docs",
            file_id = doc.fileid
        )

        # Fetch the sheet data to find the row index
        df = GSDB_Connect.fetch(doc.db_url)
        row_idx = df.index[df['_fileId'] == doc.fileid].tolist()
        if not row_idx:
            logger.error("No matching fileid found in DB for update.")
            return
        row_number = row_idx[0]
        GSDB_Connect.update(
            sheet_id = GSDB_Connect.extract_sheet_id(doc.db_url),
            worksheet_name = "user_docs",
            row_idx = row_number,
            cols = ["_summary", "_generatedTime", "_length"],
            values = [summary, dt.datetime.now().strftime("%I:%M%p on %B %d, %Y"), len(summary)]
        )
        logger.info(f"Updated summary in DB for fileid: {doc.fileid}")

        # Release lock
        GSDB_Connect.release_lock(
            sheet_id = GSDB_Connect.extract_sheet_id(doc.db_url),
            worksheet_name = "user_docs",
            file_id = doc.fileid
        )
        

    # 主函數
    @staticmethod
    def RUN(file_id: str, doc: Document):
        '''main function for summarization task'''

        logger.info(f"Starting background task {file_id}")
        Summarizer.create_row(doc)
        result = summarize_document(doc) 
        Summarizer.update_summary_to_row(doc, result)
        logger.info(f"Task {file_id} finished")

    


@app.post("/summarize")
async def summarize(doc: Document, background_tasks: BackgroundTasks):

    # 把長時間任務丟給 background_tasks
    background_tasks.add_task(Summarizer.RUN, doc.fileid, doc)
    return {"message": "Summarization task started", "fileid": doc.fileid}

# @app.get("/tasks/{userid}")
# async def get_result(userid: str):
#     user_tasks = [task for task in summarizer.tasks.values() if task["user_id"] == userid]
#     return user_tasks

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)