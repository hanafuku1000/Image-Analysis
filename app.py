
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time

import json


#キーを別途ファイルから取得する場合(Secret.jsonより読み込む)
#with open("secret.json") as f:
#    secret = json.load(f)  

# Set API key.
#KEY = secret["KEY"]
#ENDPOINT = secret["ENDPOINT"]

# 環境変数からキーとエンドポイントを取得
KEY = os.getenv("VISION_KEY")
ENDPOINT = os.getenv("VISION_ENDPOINT")

#クライアントを認証する
computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))


#＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
def get_tags(filepath):
#＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
    print("===== タグ an Image - local =====")

    local_image = open(filepath, "rb")  #読み込み + バイナリ形式で読み込む


    # Call API
    #computervision_clientの中の、tag_imageメソッドを呼び出す 
    # ローカルの場合は、メソッド名に「_in_stream」が付く 
    tags_result = computervision_client.tag_image_in_stream(local_image)

    #下記の代入は、特に強い意味はないみたい。ただtags_resultという変数名が長いから、とかその程度の理由っぽいﾖ
    tags = tags_result.tags #tags_result.tagsは、nameとconfidenceの2つの要素を持つリスト形式

    tags_names = []

    for tag in tags:
        tags_names.append(tag.name) #tags_namesにtag.nameのみの情報をtags_namesに追加取得していく
    
    return tags_names

#＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
def detect_objects(filepath):
#＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

    print("===== 物体検出 an Image - local =====")
    local_image = open(filepath, "rb")  #読み込み + バイナリ形式で読み込む

    #remote_image_url_objects = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/objects.jpg" 

    #Call API
    #computervision_clientの中の、detect_objects_im_streamメソッドを呼び出す
    #ローカルの場合は、メソッド名に「_in_stream」が付く 
    #引数名もremoteのままではないので注意
    detect_objects_results = computervision_client.detect_objects_in_stream(local_image)

    #表示ではなく、リスト形式で取得する
    # objectsに入る値は、情報が格納されたアドレスのリスト
    objects = detect_objects_results.objects #名前や位置、信頼度などの情報を取得

    return objects  #objectsを返す


#＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
#フォルダの存在確認と自動作成(ローカル及びクラウド環境下でも動作)
#＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
def ensure_folder_exists(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# フォルダの存在確認と自動作成
folder_name = "img"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
    print(f"フォルダ '{folder_name}' を作成しました。")


#＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
#画面構成：streamlit
#＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
import streamlit as st
from PIL import ImageDraw #画像に図形を描画するためのモジュール
from PIL import ImageFont #画像に文字を描画するためのモジュール

#タイトル
st.title("画像解析アプリ")

#ファイルをアップロードする
uploaded_file = st.file_uploader("ここに画像をドラッグ＆ドロップしてください", type=["jpg", "png"])

#uploaded_fileがある場合
if uploaded_file is not None: #uploaded_fileがある(not None)場合
    img = Image.open(uploaded_file) #Pillow（python imageライブラリ)のImegeメソッドを使って画像を読み込む

    #detect_objectsの呼び出しのために必要なfilepathを取得するには、保存されている場所（path）を引数として渡す必要がある
    #しかしst.file_uploaderからは直接、filepathを取得できない。
    #→filepathを取得するため、一旦保存する
    
    #image_path = f"img/{uploaded_file.name}" #画像の保存先パス（フォルダとファイル名）を作成。ファイル名は元々の名前を使う
    
    # 画像の保存先パス。名前は固定にする
    # アップロードされたファイルの拡張子（.jpg または .png）を取得
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()  
    image_path = f"img/file01{file_extension}"
    
    img.save(image_path) #画像を上記filepathを使い実際に保存する。img_saveは、Pillowのメソッド

    #detect_objects関数を呼び出す。引数は、画像を一旦保存した先のパス
    #objectsには、物体検出の情報が格納されたアドレスのリストが返ってくる
    objects = detect_objects(image_path) 

    #画像に図形を描画する
    #draw：ImageDrawオブジェクト。このオブジェクトの型は、PIL.ImageDraw.ImageDraw
    #引数で渡したimgに対して、図形を描画するためのオブジェクト
    draw = ImageDraw.Draw(img) #画像に図形を描画するためのメソッド…をdrow変数へ入れることで、具体的に書き込むのではなく書き込む準備をした感じになる
    
    for obj in objects: #objectsの情報を1つずつ取り出す
        x= obj.rectangle.x #rectangle（長方形という意味）は、物体の位置情報を持つ
        y= obj.rectangle.y #rectangle.yは、物体の位置情報のy軸情報を持つ
        w =  obj.rectangle.w
        h =  obj.rectangle.h
        caption = obj.object_property #物体の名前を取得する

        
               

        #長方形を書き込む
        #drowは上記で設定した変数
        #[(始点のxy座標)(終点のxy座標)]  ←リスト型の中に、タプル型の座標情報を入れる
        draw.rectangle([(x, y), (x+w, y+h)], fill=None, outline="green", width=5)  
        
        #文字情報の準備
        font_1 = ImageFont.truetype("./ARIAL.TTF", size =50)
        padding = 18  # 余白を設定
        
        #captionの文字の高さと幅の情報を取得
        #txt_w,txt_h = draw.textsize(caption, font=font_1) #文字のサイズはfontで指定
        bbox = draw.textbbox((0, 0), caption, font=font_1)  # 外接矩形を取得
        txt_w = bbox[2] - bbox[0]  # 横幅（右端 - 左端）
        txt_h = bbox[3] - bbox[1] + padding  # 高さ（下端 - 上端）
                
        draw.rectangle([(x, y), (x+txt_w, y+txt_h)], fill="red") #文字の背景を赤色にする
        draw.text((x, y), caption, fill="white", font=font_1)  #文字を描画する

       



    #st.image(img, caption="アップロード画像", use_column_width=True) #画像を表示する
    st.image(img) #画像を表示する

    tags_name = get_tags(image_path) #画像解析のタグを取得する
    tags_name = ", ".join(tags_name)




    st.markdown("**認識されたコンテンツﾀｸﾞ**")
    st.markdown(f"{tags_name}")


    #画像を保存する
    #with open("img/tmp.jpg", "wb") as f:
    #    f.write(uploaded_file.getbuffer()) #getbuffer:データ全体をバイナリ形式で取得するためのメソッド

    #画像解析
    #タグ情報を取得
    #tags = get_tags("tmp.jpg")
    #st.write("## タグ情報")
    #st.write(tags)

    #物体検出
    #objects = detect_objects("tmp.jpg")
    #st.write("## 物体検出")
    #st.write(objects)