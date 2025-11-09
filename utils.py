import string
import smtplib
import random 
from dotenv import load_dotenv
import os
load_dotenv()

smtp_pw = os.getenv("SMTP_PASSWORD")


def generate_random_index():
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choices(characters, k = 8))


def email_sender(recipient_email, body):
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login('huang0jin@gmail.com', smtp_pw)
    from_addr='huang0jin@gmail.com'
    to_addr=recipient_email
    msg="Subject:[EasyEssay] Your literature summary is prepared.\nHere is the list of literatures:\n" + body
    status=smtp.sendmail(from_addr, to_addr, msg)#加密文件，避免私密信息被截取
    if status=={}:
        return "系統通知信已寄出"
    else:
        return "郵件傳送失敗!"
    smtp.quit()
        