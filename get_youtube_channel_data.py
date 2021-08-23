from googleapiclient.discovery import build
#from apiclient.discovery import build

import os
import pandas as pd
import matplotlib.pyplot as plt

from flask import Blueprint

#APIで使用する
#get_youtube_channel_data_bp = Blueprint("get_youtube_channel_data",__name__)

#自分のAPIキーを入力
YOUTUBE_API_KEY = 'AIzaSyD78RLvTFeJPw3qDwYpaJWlNX99tQtUvn4'
#YouDataAPI
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

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


#メインループ
if __name__ == "__main__":
    #キーワードを指定
    keyword = "ぺこら"
    #チャンネル名とIDのdfを受け取る
    df_channel_title_id = get_youtube_channel_id(keyword)
    print("get video Success")
    #チャンネルの情報を受け取る
    df_channel_info = get_youtube_channel_infomation(df_channel_title_id)
    print("get channel info Success")

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
    plt.savefig("./output/" + keyword + "_youtube_channel_info.png",dpi=200)
    #保存のための保険
    #plt.show()

    #デプロイするときには、画像ファイルを削除するようにする
    #os.remove("./output/" + keyword + "_youtube_channel_info.png")

    #完了
    print("All Success")