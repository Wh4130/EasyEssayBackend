import google.generativeai as genai
import datetime as dt
import json
from prompts.summarize import *
from dotenv import load_dotenv, dotenv_values
from scripts.db_conn import *
from utils import *
from schema.schema import Document
import os

load_dotenv()
api_key = os.getenv('GEMINI_KEY')



class LlmManager():

    @staticmethod
    def gemini_config():
        try:
            genai.configure(api_key = api_key)
        except:
            print("Please set GEMINI API Key")
    
    @staticmethod
    def init_gemini_model(system_prompt, max_output_tokens = 40000, temperature = 0.00):
        model = genai.GenerativeModel("gemini-2.5-flash",
                                    system_instruction = system_prompt,
                                    generation_config = genai.GenerationConfig(
                                            max_output_tokens = max_output_tokens,
                                            temperature = temperature,
                                        ))
        return model
        
    @staticmethod
    def gemini_api_call(model, in_message):

        response = model.generate_content(in_message)

        return response.text
    


    




class Summarizer:

    @staticmethod
    def summarize_document(doc: Document):
    
        LlmManager.gemini_config()
        
        system_prompt = summarize_prompt(doc.lang, doc.additional_prompt)

        model = LlmManager.init_gemini_model(system_prompt)

        in_message = doc.content

        summary = LlmManager.gemini_api_call(model, in_message)

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