from celery import Celery


import time 
from scripts.db_conn import GSDB_Connect

from models.models import Document, Message


c_app = Celery()
c_app.config_from_object("config")


from scripts.summarize import Summarizer
from scripts.pinecone_manager import PineconeManager
from scripts.chat import ChatBot


@c_app.task()
def c_summarize_task(doc_dict):
    doc = Document(**doc_dict)
    Summarizer.RUN(doc.fileid, doc)

@c_app.task()
def c_upsert_to_pinecone(doc_dict):
    doc = Document(**doc_dict)
    pc = PineconeManager()
    pc.insert_docs(doc.content, doc.fileid, "easyessay" )

@c_app.task()
def c_delete_from_pinecone(namespace):
    pc = PineconeManager()
    pc.delete_from_pinecone(namespace, "easyessay")