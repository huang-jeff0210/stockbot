from openai import OpenAI, OpenAIError
import yfinance as yf
import pandas as pd # 資料處理套件
import numpy as np
import datetime as dt # 時間套件
import requests
from bs4 import BeautifulSoup



import getpass # 保密輸入套件
api_key = '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'  #getpass.getpass("請輸入金鑰：")
client = OpenAI(api_key = api_key) # 建立 OpenAI 物件


def stock_price(stock_id="大盤", days = 10):
    end = dt.date.today() # 資料結束時間
    start = end - dt.timedelta(days=days) # 資料開始時間
    if stock_id == "大盤":
        stock_id="^TWII"
        df = yf.download(stock_id, start=start)

    elif stock_id != "大盤":
        try:
            df = yf.download(f'{stock_id}.TW', start=start)
        except:
            pass
        if len(df) == 0:    
            df = yf.download(f'{stock_id}.TWO', start=start)

    # 更換列名
    df.columns = ['開盤價', '最高價', '最低價',
                    '收盤價', '調整後收盤價', '成交量']

    data = {
        '日期': df.index.strftime('%Y-%m-%d').tolist(),
        '收盤價': df['收盤價'].tolist(),
        '每日報酬': df['收盤價'].pct_change().tolist(),
        '漲跌價差': df['調整後收盤價'].diff().tolist()
        }

    return data

# 基本面資料
def stock_fundamental(stock_id= "大盤"):
    if stock_id == "大盤":
        return None
    else:

        stock = yf.Ticker(f'{stock_id}.TW')

        if len(stock.quarterly_financials) == 0:
            stock = yf.Ticker(f'{stock_id}.TWO')


        # 營收成長率
        quarterly_revenue_growth = np.round(stock.quarterly_financials.loc["Total Revenue"].pct_change(-1).dropna().tolist(), 2)
        # 每季EPS
        quarterly_eps = np.round(stock.quarterly_financials.loc["Basic EPS"].dropna().tolist(), 2)
        # EPS季增率
        quarterly_eps_growth = np.round(stock.quarterly_financials.loc["Basic EPS"].pct_change(-1).dropna().tolist(), 2)

        # 轉換日期
        dates = [date.strftime('%Y-%m-%d') for date in stock.quarterly_financials.columns]

        data = {
            '季日期': dates[:len(quarterly_revenue_growth)],  # 以最短的數據列表長度為准，確保數據對齊
            '營收成長率': quarterly_revenue_growth.tolist(),
            'EPS': quarterly_eps.tolist(),
            'EPS 季增率': quarterly_eps_growth.tolist()
        }

        return data

# 新聞資料
def stock_news(stock_name ="大盤"):
    if stock_name == "大盤":
        stock_name="台股 -盤中速報"

    data=[]
    # 取得 Json 格式資料
    json_data = requests.get(f'https://ess.api.cnyes.com/ess/api/v1/news/keyword?q={stock_name}&limit=5&page=1').json()

    # 依照格式擷取資料
    items=json_data['data']['items']
    for item in items:
        # 網址、標題和日期
        news_id = item["newsId"]
        title = item["title"]
        publish_at = item["publishAt"]
        # 使用 UTC 時間格式
        utc_time = dt.datetime.utcfromtimestamp(publish_at)
        formatted_date = utc_time.strftime('%Y-%m-%d')
        # 前往網址擷取內容
        url = requests.get(f'https://news.cnyes.com/'
                            f'news/id/{news_id}').content
        soup = BeautifulSoup(url, 'html.parser')
        p_elements=soup .find_all('p')
        # 提取段落内容
        p=''
        for paragraph in p_elements[4:]:
            p+=paragraph.get_text()
        data.append([stock_name, formatted_date ,title,p])
    return data

# 新聞連結
def stock_news_link(stock_name ="大盤"):
    if stock_name == "大盤":
        stock_name="台股 -盤中速報"

    json_data = requests.get(f'https://ess.api.cnyes.com/ess/api/v1/news/keyword?q={stock_name}&limit=10&page=1').json()
    items=json_data['data']['items']

    data=[]
    for item in items:
        # 網址、標題和日期
        news_id = item["newsId"]
        title = item["title"]
        summary = item["summary"]
        url = f'https://news.cnyes.com/news/id/{news_id}'
        tag = ','.join(item['keywordForTag'])
        data.append([title, summary ,url,tag])

    df = pd.DataFrame(data,columns=['title','summary','url','tag'])
    df = df[~df['title'].str.contains('盤中速報')].reset_index(drop=True)

    text = ''
    for i in range(len(df)):
        text += '標題:'+ df['title'].iloc[i] + '\n'
        text += '標籤:'+ df['tag'].iloc[i] + '\n'
        text += '網址:'+ df['url'].iloc[i] + '\n'
        text += '---------------'+'\n'
    return text


# 取得全部股票的股號、股名
def stock_name():
    df = pd.read_csv('stock.csv')
    df = df[['stock_id','stock_name']]
    df.columns=['股號', '股名']
    df = df.drop_duplicates()
    return df
name_df = stock_name()


# 取得股票名稱
def get_stock_name(stock_id, name_df):
    return name_df.set_index('股號').loc[stock_id, '股名']


# 建立 GPT 3.5-16k 模型
def get_reply(messages):
    try:
        response = client.chat.completions.create(
            model = "gpt-3.5-turbo-1106",
            messages = messages
        )
        reply = response.choices[0].message.content
    except OpenAIError as err:
        reply = f"發生 {err.type} 錯誤\n{err.message}"
    return reply

# 建立訊息指令(Prompt)
def generate_content_msg(stock_id, name_df):

    stock_name = get_stock_name(
        stock_id, name_df) if stock_id != "大盤" else stock_id
    # print(stock_name)

    price_data = stock_price(stock_id)
    # print(price_data)
    
    news_data = stock_news(stock_name)
    # print(news_data)

    content_msg = f'請依據以下資料來進行分析並給出一份完整的分析報告:\n'

    content_msg += f'近期價格資訊:\n {price_data}\n'

    if stock_id != "大盤":
        stock_value_data = stock_fundamental(stock_id)
        content_msg += f'每季營收資訊：\n {stock_value_data}\n'

    content_msg += f'近期新聞資訊: \n {news_data}\n'
    content_msg += f'請給我{stock_name}近期的趨勢報告,請以詳細、\
      嚴謹及專業的角度撰寫此報告,並提及重要的數字, reply in 繁體中文'

    return content_msg

# StockGPT
def stock_gpt(stock_id, name_df=name_df):
    content_msg = generate_content_msg(stock_id, name_df)

    msg = [{
        "role": "system",
        "content": f"你現在是一位專業的證券分析師, 你會統整近期的股價\
      、基本面、新聞資訊等方面並進行分析, 然後生成一份專業的趨勢分析報告"
    }, {
        "role": "user",
        "content": content_msg
    }]

    reply_data = get_reply(msg)

    return reply_data


