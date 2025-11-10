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
    def update(sheet_id, worksheet_name, row_idx: int, cols: list, values: list):
        """Update single row for multiple columns"""
        mapping = {
            "user_docs": {
                "_fileId": "A",
                "_fileName": "B", 
                "_summary": "C",
                "_generatedTime": "D",
                "_length": "E",
                "_tag": "F"  
            },
            "user_tags": {
                "_tagId": "A",
                "_tag": "B" 
            },
            "user_info": {
                "_dbURL": "F"
            }
        }

        client = GSDB_Connect.authenticate_google_sheets()
        for col, value in zip(cols, values):
            try:
                sheet = client.open_by_key(sheet_id)
                worksheet = sheet.worksheet(worksheet_name)
                pos = f"{mapping[worksheet_name][col]}{row_idx + 2}"
                worksheet.update_acell(pos, value)
                
            except Exception as e:
                return f"Connection Failed: {e}"
            
    @staticmethod
    def acquire_lock(sheet_id, worksheet_name, file_id, timeout = 10):
        lock_maps = {
            "user_info": "G1",
            "user_docs": "G1",
            "user_tags": "C1",
            "user_chats": "F1"
        }

        """
        Acquire a lock before editing.
        :param worksheet: The gspread worksheet object.
        :param lock_pos: the position of the cell that stores the lock status
        :param timeout: Max time (in seconds) to wait for lock.
        :return: True if lock acquired, False otherwise.
        """
        start_time = time.time()
        client = GSDB_Connect.authenticate_google_sheets()
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet(worksheet_name)
        print("Waiting for lock...")
        while time.time() - start_time < timeout:
            lock_status = worksheet.acell(lock_maps[worksheet_name]).value

            if lock_status == "Unlocked":
                # Acquire the lock
                worksheet.update_acell(lock_maps[worksheet_name], file_id)

                print("Lock acquired.")
                
                return True
            
            elif lock_status == file_id:
                # Already locked by the same task
                print("Lock already held by this task.")
                return True
            
            time.sleep(0.5)
        

        return False
    
    @staticmethod
    def release_lock(sheet_id, worksheet_name, file_id):
        """
        Release the lock after editing.
        :param worksheet: The gspread worksheet object.
        :param user_email: The email of the user trying to release the lock.
        :return: True if lock released, False otherwise.
        """
        lock_maps = {
            "user_info": "G1",
            "user_docs": "G1",
            "user_tags": "C1",
            "user_chats": "F1"
        }

        client = GSDB_Connect.authenticate_google_sheets()
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet(worksheet_name)
        lock_status = worksheet.acell(lock_maps[worksheet_name]).value

        if lock_status == file_id:
            worksheet.update_acell(lock_maps[worksheet_name], "Unlocked")
            return True
        else:
            print("Lock is not held by you!")
            return False
        
    @staticmethod
    def append_row(db_sheet_url, row):    
        client = GSDB_Connect.authenticate_google_sheets()
        sheet_id = GSDB_Connect.extract_sheet_id(db_sheet_url)
        if sheet_id is None:
            return None
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet("user_docs")
        worksheet.freeze(rows = 1)
        worksheet.append_row(row)

        return "Document summary successfully updated to Google Sheet."
    
    

