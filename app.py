from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import time
import datetime as dt
import pandas 
import uuid
import logging
import uvicorn 
import os
from dotenv import load_dotenv
from scripts.summarize import LlmManager, Summarizer
from scripts.db_conn import *
from scripts.pinecone_manager import Pinecone_Upsert_RUN
from schema.schema import Document
from utils import *
load_dotenv()

# --- initialize GEMINI api key
key = os.getenv("GEMINI_KEY")

# --- initialize logger
logger = logging.getLogger("uvicorn")

# --- initialize FastAPI app
app = FastAPI()



    
# *** ---------------------------------------------------------------------------------------------------------
# --- APIs


@app.post("/summarize")
async def summarize(doc: Document, background_tasks: BackgroundTasks):
    """start a background task to summarize requested document"""

    # async run in background
    background_tasks.add_task(Summarizer.RUN, doc.fileid, doc, logger)
    return {"message": "Summarization task started", "fileid": doc.fileid}

@app.post("/upsert_to_pinecone")
async def upsert_to_pinecone(doc: Document, background_tasks: BackgroundTasks):
    """start a background task to upsert requested document to pinecone"""

    # async run in background
    background_tasks.add_task(Pinecone_Upsert_RUN, doc.content, doc.fileid, "easyessay", logger)
    return {"message": "Pinecone upsert task started", "fileid": doc.fileid}


@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)