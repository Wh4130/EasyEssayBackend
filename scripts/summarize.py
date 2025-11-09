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



class LlmManager:

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
    


    

def summarize_document(doc: Document):
    
    LlmManager.gemini_config()
    
    system_prompt = summarize_prompt(doc.lang, doc.additional_prompt)

    model = LlmManager.init_gemini_model(system_prompt)

    in_message = doc.content

    summary = LlmManager.gemini_api_call(model, in_message)

    return summary

# **** main function
def update_summary_to_db(doc: Document):
    """summarize the document and update summary to gsheet db"""

    # summarize
    summary = summarize_document(doc)

    # update to gsheet
    instance = [
        doc.fileid,
        doc.filename,
        summary,
        dt.datetime.now().strftime("%I:%M%p on %B %d, %Y"),
        doc.length,
        doc.user_id,
        doc.tag
    ]

    result = GSDB_Connect.update_to_sheet(instance)
    
    return instance