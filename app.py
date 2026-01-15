from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
import asyncio
from pydantic import BaseModel
import time
import datetime as dt
import pandas 
import uuid
import logging
import uvicorn 
import os
from dotenv import load_dotenv

from scripts.summarize import Summarizer
from scripts.db_conn import *
from scripts.pinecone_manager import Pinecone_Upsert_RUN, PineconeManager
from models.models import Document, Message, TestDB
from utils import *
load_dotenv()

from celery_app import c_app, c_summarize_task, c_upsert_to_pinecone

# --- initialize logger
logger = logging.getLogger("uvicorn")

# --- initialize global variable container
context = {}

async def lifespan(*args, **kwargs):
    """
    lifespan manager for FastAPI app.
    """
    # --- initialize pinecone instance
    print("Initializing pinecone manager...")
    context['pc'] = PineconeManager()

    yield

    print("Cleaning resources...")
    context.clear()
    print("Done!")

# --- initialize FastAPI app
app = FastAPI(lifespan = lifespan)


    
# *** ---------------------------------------------------------------------------------------------------------
# --- APIs


@app.get("/")
async def index():
    """
    Entry point
    """
    return {"status": "ok"}


@app.post("/summarize")
async def summarize(doc: Document):
    """
    start a background task to summarize requested document
    use async def because this endpoint is just a registration task, which does not block the main loop
    """
    
    # Summarizer.RUN is a synchronous function
    task = c_summarize_task.delay(doc.model_dump())

    return {"message": "Summarization task started", "fileid": doc.fileid, "task_id": task.id}

@app.post("/upsert_to_pinecone")
async def upsert_to_pinecone(doc: Document):
    """
    start a background task to upsert requested document to pinecone
    use async def because this endpoint is just a registration task, which does not block the main loop
    """

    task = c_upsert_to_pinecone.delay(doc.model_dump())

    return {"message": "Pinecone upsert task started", "fileid": doc.fileid, "task_id": task.id}

@app.post("/query_from_pinecone")
async def pinecone_query_api(msg: Message):
    """search top k most relevant passage from pinecone and return"""

    result = await asyncio.to_thread(context["pc"].search, msg.query, msg.param_k, msg.fileid, "easyessay")
    
    return {"result": result}


@app.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    task = c_app.AsyncResult(task_id)

    if task.state == "PENDING":
        return {"status": "pending"}
    elif task.state == "SUCCESS":
        return {"status": "completed", "result": task.result}
    else:
        return {"status": "failed", "error": task.info}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)