# -*- coding: utf-8 -*-
"""
Created on Sat Aug 18 01:00:17 2018

@author: linzino
"""


from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import re, os
import stock_srapy

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('7r0ld9JH1KvogGMRzjJZxSvzdSVtYu6gPF9bFMkhY/vi9YDhsBiXVagSyOOWsg2IlIV28Sc/glVyd7i+UdYFvyIgUq3L+Uz0wnyxJX8h4ziDjuu0aPckSts7Vdo7BxKZd2cNru97p0xUIHNm162OTQdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('391ca1cd0b1c3bdd969dd9b4c99f6429')


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    ### 抓到顧客的資料 ###
    profile = line_bot_api.get_profile(event.source.user_id)
    uid = profile.user_id #使用者ID
    print(uid)

    usespeak=str(event.message.text) #使用者講的話
    print(usespeak)

    if re.match('新增[0-9]{4}',usespeak): # 先判斷是否是使用者要用來存股票的
        line_bot_api.push_message(uid, TextSendMessage(usespeak+'已經儲存成功'))
        return 0
    
    elif re.match('刪除[0-9]{4}',usespeak): # 刪除存在資料庫裡面的股票
        line_bot_api.push_message(uid, TextSendMessage(usespeak+'已經刪除成功'))
        return 0
    
    elif re.match('投信買超',usespeak):
        answer = stock_srapy.get_invest(usespeak)
        line_bot_api.push_message(uid, TextSendMessage(answer))
        return 0

    elif re.match('投信賣超',usespeak):
        answer = stock_srapy.get_invest(usespeak)
        line_bot_api.push_message(uid, TextSendMessage(answer))
        return 0
    
    elif re.match('[0-9]{4}融資融券',usespeak):
        img_url = stock_srapy.MarginPurchaseShortSale(usespeak[:4])
        line_bot_api.push_message(uid, ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))
        return 0
    
    elif re.match('[0-9]{4}配息',usespeak):
        img_url = stock_srapy.dividend_cash(usespeak[:4])
        line_bot_api.push_message(uid, ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))
        return 0

    elif re.match('[0-9]{4}走勢',usespeak):
        img_url = stock_srapy.price_trend(usespeak[:4])
        line_bot_api.push_message(uid, ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))
        return 0
    
    elif re.match('[0-9]{4}',usespeak):
        answer = stock_srapy.get_price(usespeak)
        line_bot_api.push_message(uid, TextSendMessage(answer))
        return 0
    
    else:
        message = TextSendMessage(text=event.message.text)
        line_bot_api.reply_message(event.reply_token,message)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)