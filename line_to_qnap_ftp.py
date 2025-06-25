from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, FileMessage
from ftplib import FTP
import os

# <<< กรอกตรงนี้ >>>
CHANNEL_SECRET = '98b6e1fe757f5aeae8feea83939b1709'
CHANNEL_ACCESS_TOKEN = 'cQlwxdQoJBSgD0Dx6XIAFalw0Bc3TqnIss5H7Hf2+2PWnF249+9zHNGP1XxWsn7jNVd6+77IDS5p+ctv1HhLQhUsk0ou15nNF2p0AT5EKFVxo/x79UyFPu11+LGDDVOHFMPEgdQ3MxNVY3h01X8aPAdB04t89/1O/w1cDnyilFU='

QNAP_FTP_HOST = '192.217.18.84'  # เปลี่ยนเป็น IP ของ QNAP ในเครือข่ายของคุณ
QNAP_FTP_PORT = 21
QNAP_FTP_USER = 'admin'
QNAP_FTP_PASS = 'Rr123456789'
QNAP_FTP_FOLDER = '/งานตรวจอากาศ/LineFiles/'  # โฟลเดอร์ปลายทางใน QNAP (ต้องมีสิทธิ์เขียน)
# <<< จบ >>>

app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return 'OK'

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_id = event.message.id
    file_name = event.message.file_name

    # ดึงไฟล์จาก LINE
    file_content = line_bot_api.get_message_content(message_id).content

    # เซฟไฟล์ไว้ชั่วคราว
    with open(file_name, 'wb') as f:
        f.write(file_content)

    # อัปโหลดเข้า QNAP FTP
    try:
        ftp = FTP()
        ftp.connect(QNAP_FTP_HOST, QNAP_FTP_PORT)
        ftp.login(QNAP_FTP_USER, QNAP_FTP_PASS)
        ftp.cwd(QNAP_FTP_FOLDER)

        with open(file_name, 'rb') as f:
            ftp.storbinary(f'STOR {file_name}', f)

        print(f"✅ อัปโหลดไฟล์ {file_name} ไปยัง QNAP สำเร็จ")
        ftp.quit()
    except Exception as e:
        print(f"❌ อัปโหลดล้มเหลว: {e}")

    os.remove(file_name)

if __name__ == "__main__":
    app.run(port=5000)
