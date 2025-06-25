from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, FileMessage

import os
import tempfile
from ftplib import FTP

# ใส่ Token ที่ได้จาก LINE Developer
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET", "98b6e1fe757f5aeae8feea83939b1709")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN", "cQlwxdQoJBSgD0Dx6XIAFalw0Bc3TqnIss5H7Hf2+2PWnF249+9zHNGP1XxWsn7jNVd6+77IDS5p+ctv1HhLQhUsk0ou15nNF2p0AT5EKFVxo/x79UyFPu11+LGDDVOHFMPEgdQ3MxNVY3h01X8aPAdB04t89/1O/w1cDnyilFU=")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_content = line_bot_api.get_message_content(event.message.id).content
    filename = event.message.file_name

    # Save temporarily
    with open(filename, 'wb') as f:
        f.write(message_content)

    # FTP Upload
    try:
        ftp = FTP()
        ftp.connect('192.217.18.84', 21)  # เปลี่ยนเป็น IP จริง
        ftp.login('admin', 'Rr123456789')
        ftp.cwd('/งานตรวจอากาศ/LineFiles/')  # เปลี่ยนโฟลเดอร์ปลายทาง
        with open(filename, 'rb') as f:
            ftp.storbinary(f'STOR {filename}', f)
        print(f"✅ อัปโหลดไฟล์ {filename} สำเร็จ")
        ftp.quit()
    except Exception as e:
        print(f"❌ อัปโหลดล้มเหลว: {e}")

    os.remove(filename)

if __name__ == "__main__":
    app.run()
