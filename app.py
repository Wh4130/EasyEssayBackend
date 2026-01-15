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
from schema.schema import Document, Message
from utils import *
load_dotenv()

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


@app.post("/summarize")
async def summarize(doc: Document, background_tasks: BackgroundTasks):
    """
    start a background task to summarize requested document
    use async def because this endpoint is just a registration task, which does not block the main loop
    """
    
    # Summarizer.RUN is a synchronous function
    background_tasks.add_task(Summarizer.RUN, doc.fileid, doc, logger)
    return {"message": "Summarization task started", "fileid": doc.fileid}

@app.post("/upsert_to_pinecone")
async def upsert_to_pinecone(doc: Document, background_tasks: BackgroundTasks):
    """
    start a background task to upsert requested document to pinecone
    use async def because this endpoint is just a registration task, which does not block the main loop
    """

    # async run in background
    background_tasks.add_task(context["pc"].insert_docs, doc.content, doc.fileid, "easyessay")
    return {"message": "Pinecone upsert task started", "fileid": doc.fileid}

@app.post("/query_from_pinecone")
async def pinecone_query_api(msg: Message):
    """search top k most relevant passage from pinecone and return"""

    result = await asyncio.to_thread(context["pc"].search, msg.query, msg.param_k, msg.fileid, "easyessay")
    
    return {"result": result}


@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)