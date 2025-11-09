from dotenv import dotenv_values, load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
import pandas as pd
import time
import os

load_dotenv()

gs_key = os.getenv('GSHEET_CREDENTIALS')
db_worksheet = os.getenv('DB_WORKSHEET')

class GSDB_Connect:

    @staticmethod
    def authenticate_google_sheets():
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(gs_key), scope)
        client = gspread.authorize(creds)
        return client
    
    @staticmethod
    def extract_sheet_id(sheet_url):
        try:
            return sheet_url.split("/d/")[1].split("/")[0]
        except IndexError:
            print("無效的試算表連結，請檢查 URL 格式。")
            return None
        
    @staticmethod
    def fetch(db_sheet_url):
        sheet_id = GSDB_Connect.extract_sheet_id(db_sheet_url)
        client = GSDB_Connect.authenticate_google_sheets()
        try:
            sheet = client.open_by_key(sheet_id)
            ws = sheet.worksheet(db_worksheet)
            data = ws.get_all_records()
            
            return pd.DataFrame(data)
        except:
            return "Connection Failed"
        
    @staticmethod
    def update_to_sheet(db_sheet_url, row):    
        client = GSDB_Connect.authenticate_google_sheets()
        sheet_id = GSDB_Connect.extract_sheet_id(db_sheet_url)
        if sheet_id is None:
            return None
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet("user_docs")
        worksheet.freeze(rows = 1)
        worksheet.append_row(row)

        return "Document summary successfully updated to Google Sheet."
    
    

