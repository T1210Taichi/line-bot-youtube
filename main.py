#youtubeチャンネル情報
#from get_youtube_channel_data import get_ycd_bp

from googleapiclient.discovery import build

from flask import Flask, request, abort
import os
import gunicorn

import pandas as pd
import matplotlib.pyplot as plt

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



#get_youtube_channel_data.pyを使うため
#app.register_blueprint(get_ycd_bp)

#環境変数取得
#YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
#YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
YOUR_CHANNEL_ACCESS_TOKEN = "9yCdvg0MDclAYuc1tSEjcN2qZfjRAeSb4LqU/meK38NA9Aj6E4f3EC7DZaQ1xtYjWPgmKVsDp0FbvCyA9MpNR+YdQIJxPhuTUi4gajvZ/pZupTKRUwnOh767NaK6KZTza/kmAtBNQZsrIwX40zMbYwdB04t89/1O/w1cDnyilFU="
YOUR_CHANNEL_SECRET = "2e576afd75097ad7804ee18ab9f3e776"

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

#自分のAPIキーを入力
YOUTUBE_API_KEY = 'AIzaSyD78RLvTFeJPw3qDwYpaJWlNX99tQtUvn4'
#YOUTuBe_API_KEY = os.environ["YOUTUBE_API_KEY"]
#YouDataAPI
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/test1")
def test1():
    return "test1 OK!"

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

#画像を返す(イラストや)
#@handler.add(MessageEvent, message=TextMessage)
#def handle_message(event):
#    img_irasutoya = ImageSendMessage(original_content_url="https://1.bp.blogspot.com/-eaDZ7sDP9uY/Xhwqlve5SUI/AAAAAAABXBo/EcI2C2vim7w2WV6EYy3ap0QLirX7RPohgCNcBGAsYHQ/s400/pose_syanikamaeru_man.png",preview_image_url="https://1.bp.blogspot.com/-eaDZ7sDP9uY/Xhwqlve5SUI/AAAAAAABXBo/EcI2C2vim7w2WV6EYy3ap0QLirX7RPohgCNcBGAsYHQ/s400/pose_syanikamaeru_man.png")
#    line_bot_api.reply_message(event.reply_token,img_irasutoya)

#画像を返す(youtubeチャンネルの情報)
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #チャンネル情報のpngのパス
    path_youtube_channel_info = get_channel_info_png(event.message.text)
    #チャンネル情報のpng
    img_youtube_channel_info = ImageSendMessage("https://line-bot-youtube.herokuapp.com/"+original_content_url=path_youtube_channel_info,preview_image_url="https://line-bot-youtube.herokuapp.com/"+path_youtube_channel_info)
    #pngを送信
    line_bot_api.reply_message(event.reply_token,img_youtube_channel_info)


#キーワードを受け取り、そのキーワードについて動画を調べる
#その動画のyoutubeチャンネルの名前とIDのdfを返す
#get_youtube_channel_id(キーワード)
def get_youtube_channel_id(keyword):
    #キーワードについて動画を調べる
    search_response = youtube.search().list(
        part='snippet',
        #検索したい文字列を指定
        q=keyword,
        #視聴回数が多い順に取得
        #order='date',
        #type='video',
        #maxResults=5,
    ).execute()

    #itemsだけ抜きだす
    video_data = search_response["items"]

    #全体
    df = pd.DataFrame(video_data)
    #動画ごとの一意のvideoIdを取得
    df_videoId = pd.DataFrame(list(df['id']))['videoId']
    #動画ごとの投稿チャンネル名channelTitleを取得
    df_channelTitle = pd.DataFrame(list(df['snippet']))['channelTitle']
    #動画を投稿しているchannelIdを取得
    df_channelId = pd.DataFrame(list(df["snippet"]))["channelId"]
    #チャンネル名とチャンネルIDを結合
    df_channel_title_id = pd.concat([df_channelTitle,df_channelId],axis=1)
    #重複を削除
    df_channel_title_id = df_channel_title_id[~df_channel_title_id.duplicated()]

    return df_channel_title_id

#youtubeチャンネルの名前とIDのdfを受け取り
#そのチャンネルの「名前、公開日、登録者数、合計視聴時間、合計投稿数、説明」のdfを返す
def get_youtube_channel_infomation(df_channel_title_id):
    channel_response = []
    for chan in df_channel_title_id["channelId"]:
        channel_response.append(youtube.channels().list(
                                    part='statistics,snippet',
                                    id = chan,
                                    ).execute()    
        )
    #itemsの情報をまとめる
    channel_items = []
    for chan in channel_response:
        channel_items.append(chan["items"])

    #itemの情報をdfにし、それぞれ配列に格納
    chan_info_df = []
    for chan in channel_items:
        chan_info_df.append(pd.DataFrame(chan))

    #チャンネルの情報を一行にまとめる
    df_chan_info = chan_info_df[0]
    df_chan_info = df_chan_info.append(chan_info_df[:])

    #チャンネル名,チャンネル開設時間,説明
    df_channel_title_publishedAt = pd.DataFrame(list(df_chan_info['snippet']))[['title','publishedAt']]
    #df_channel_description = pd.DataFrame(list(df_chan_info['snippet']))['description']

    #チャンネル登録数、総再生回数,動画数
    df_channel_statistics = pd.DataFrame(list(df_chan_info["statistics"]))[['subscriberCount','viewCount','videoCount']]

    #チャンネルの情報を結合
    df_channel_info =  pd.concat([df_channel_title_publishedAt,df_channel_statistics],axis=1)
    #重複を削除
    df_channel_info = df_channel_info[~df_channel_info.duplicated()]

    return df_channel_info

#呼び出し用
def get_channel_info_png(keyword):
    #キーワードを指定
    #チャンネル名とIDのdfを受け取る
    df_channel_title_id = get_youtube_channel_id(keyword)
    #print("get video Success")
    #チャンネルの情報を受け取る
    df_channel_info = get_youtube_channel_infomation(df_channel_title_id)
    #print("get channel info Success")

    #ラベルを日本語表記
    df_channel_info = df_channel_info.rename(columns={"title":"チャンネル名",
                                                 "publishedAt":"公開日",
                                                 "subscriberCount":"チャンネル登録者数",
                                                 "viewCount":"総再生回数",
                                                 "videoCount":"総動画数",})

    # フォントの種類とサイズを設定する。
    plt.rcParams['font.family'] = 'MS Gothic'
    plt.rcParams["font.size"] = 30

    #画像(png)で出力する
    #dpiを大きくすると表が大きくなる
    fig,ax = plt.subplots(figsize=((len(df_channel_info.columns)+1)*1.2, (len(df_channel_info)+1)*0.4),dpi=200)
    #軸を表示しない
    ax.axis("off")
    ax.axis("tight")
    #表の設定
    ax.table(cellText=df_channel_info.values,
            colLabels = df_channel_info.columns
            ,rowLabels = df_channel_info.index
            ,colColours =['#96ABA0'] * 5
            ,rowColours =['#96ABA0'] * 5
            ,loc="center"
            )
    #余白をなくす
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    #pngで保存
    plt.savefig("./static/"+ keyword + "_youtube_channel_info.png",dpi=200)
    #画像のファイルパス
    img = "./static/"+ keyword + "_youtube_channel_info.png"
    return img

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)