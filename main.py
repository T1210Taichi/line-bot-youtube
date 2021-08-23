from get_youtube_channel_data import get_youtube_channel_data_bp

from flask import Flask, request, abort
import os
import gunicorn

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from linebot.models import (
    ImageMessage, ImageSendMessage
)

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/")
def hello_world():
    return "hello world!"

#1
#Webhookからのリクエストをチェックする
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証のための値を取得する
    signature = request.headers['X-Line-Signature']

    #リクエストボディを取得する
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    #署名を検証し、問題なければhandleに定義されている関数を呼び出す
    try:
        handler.handle(body, signature)
    #署名検証を失敗した場合、例外を出す
    except InvalidSignatureError:
        abort(400)
    #handleの処理を終えればOK
    return 'OK'


#2
#LINEのメッセージの取得と返信無いようの定義

#LINEでMEssageEvent(普通のメッセージを送信された場合)が起こったときに
#def以下の関数を実行する
#reply_messageの第一引数のevent.reply_tokenは、イベントの応答に用いるトークンです
#第二引数には、linebot.modelsに定義されている返信用のTextSendMessageオブジェクトを渡しています。

#テキスト(オウム返し)
#@handler.add(MessageEvent, message=TextMessage)
#def handle_message(event):
#    line_bot_api.reply_message(
#        event.reply_token,
#        TextSendMessage(text=event.message.text))

#画像を返す
#@handler.add(MessageEvent, message=TextMessage)
#def handle_message(event):
#    img_irasutoya = ImageSendMessage(
#        original_content_url="https://1.bp.blogspot.com/-eaDZ7sDP9uY/Xhwqlve5SUI/AAAAAAABXBo/EcI2C2vim7w2WV6EYy3ap0QLirX7RPohgCNcBGAsYHQ/s400/pose_syanikamaeru_man.png",
#        preview_image_url="https://1.bp.blogspot.com/-eaDZ7sDP9uY/Xhwqlve5SUI/AAAAAAABXBo/EcI2C2vim7w2WV6EYy3ap0QLirX7RPohgCNcBGAsYHQ/s400/pose_syanikamaeru_man.png",
#    )
#    
#    line_bot_api.reply_message(event.reply_token,img_irasutoya)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    img_irasutoya = ImageSendMessage(original_content_url="https://1.bp.blogspot.com/-eaDZ7sDP9uY/Xhwqlve5SUI/AAAAAAABXBo/EcI2C2vim7w2WV6EYy3ap0QLirX7RPohgCNcBGAsYHQ/s400/pose_syanikamaeru_man.png",preview_image_url="https://1.bp.blogspot.com/-eaDZ7sDP9uY/Xhwqlve5SUI/AAAAAAABXBo/EcI2C2vim7w2WV6EYy3ap0QLirX7RPohgCNcBGAsYHQ/s400/pose_syanikamaeru_man.png")
    line_bot_api.reply_message(event.reply_token,img_irasutoya)

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)