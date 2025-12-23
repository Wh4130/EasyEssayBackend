import google.generativeai as genai
import datetime as dt
import json
from prompts.summarize import *
from dotenv import load_dotenv, dotenv_values
from scripts.db_conn import *
from utils import *
from litellm import completion
from schema.schema import Document
import os

load_dotenv()
os.environ["CEREBRAS_API_KEY"] = os.getenv('CEREBRAS_API_KEY')





def generate_response(messages):
    """
    Call LLM and return message that contents both tool usage and chat content
    """
    response = completion(
        model="cerebras/gpt-oss-120b",
        messages=messages,
        max_tokens=30000
    )
    
    # 直接回傳 Message 物件，這是 LiteLLM 內部的標準格式
    # 它包含了 .content 和 .tool_calls
    return response.choices[0].message.content

    




class Summarizer:
    

    @staticmethod
    def summarize_document(doc: Document):

        """call LLM to summarize the document content"""
        
        system_prompt = summarize_prompt(doc.lang, doc.additional_prompt)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": doc.content}
        ]
        summary = generate_response(messages)

        return summary

    @staticmethod
    def create_row(doc: Document, logger):
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
    def update_summary_to_row(doc: Document, summary: str, logger):
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
    def RUN(file_id: str, doc: Document, logger):
        '''main function for summarization task'''

        logger.info(f"Starting background task {file_id}")
        Summarizer.create_row(doc, logger)
        result = Summarizer.summarize_document(doc) 
        Summarizer.update_summary_to_row(doc, result, logger)
        logger.info(f"Task {file_id} finished")