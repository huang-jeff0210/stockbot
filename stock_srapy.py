import requests
import time
import pandas as pd
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import plotly.express as px
import Imgur
import mplfinance as mpf
import matplotlib.ticker as ticker
import plotly.graph_objects as go
import yfinance as yf

# 设置中文字体
font_path = './msjh.ttc'
font_prop = FontProperties(fname=font_path)
# plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 修改中文字體
plt.rcParams['axes.unicode_minus'] = False # 顯示負號

# 股票代碼與股票名稱
df = pd.read_csv('stock.csv')
stock_dict = dict(zip(df['stock_id'],df['stock_name']))

def clean_space(data):
    for col in data.columns:
        if type(data[col][0])==str:
            data[col] = data[col].str.strip()
            data[col] = data[col].str.replace(' ','')
            data[col] = data[col].str.replace('\u3000','')
    return data

#最近工作日投信買賣超
def get_invest(text):
    millisec = int(round(time.time() * 1000))
    url = f'https://www.twse.com.tw/rwd/zh/fund/TWT44U?response=json&_={millisec}'
    resp = requests.get(url)
    data = resp.json()

    date = data['date']
    today = date[:4]+'-'+date[4:6]+'-'+date[6:]
    columns = ['Datetime', 'Stockcode', 'Stockname', 'Buyvol', 'Sellvol', 'BuySellvol']
    df = pd.DataFrame(data['data'],columns=columns)
    df['Datetime'] = today
    df['Tag'] = '投信'
    df['Buyvol'] = round(pd.to_numeric(df['Buyvol'].str.replace(',', ''))/1000,0)
    df['Sellvol'] = round(pd.to_numeric(df['Sellvol'].str.replace(',', ''))/1000,0)
    df['BuySellvol'] = round(pd.to_numeric(df['BuySellvol'].str.replace(',', ''))/1000,0)
    clean_space(df)
    # df.to_sql(name = 'tbl_institutional_investors',con=engine, if_exists = 'append',index = False)


    millisec = int(round(time.time() * 1000))
    url = f'https://www.tpex.org.tw/web/stock/3insti/sitc_trading/sitctr_result.php?l=zh-tw&t=D&type=buy&_={millisec}'
    resp = requests.get(url)
    data = resp.json()
    columns = ['Datetime', 'Stockcode', 'Stockname', 'Buyvol', 'Sellvol', 'BuySellvol']
    df2 = pd.DataFrame(data['aaData'],columns=columns)
    df2['Datetime'] = today
    df2['Tag'] = '投信'
    try:
        df2['Buyvol'] = pd.to_numeric(df2['Buyvol'].str.replace(',', ''))
    except:
        df2['Buyvol'] = pd.to_numeric(df2['Buyvol'])
        pass
    try:
        df2['Sellvol'] = pd.to_numeric(df2['Sellvol'].str.replace(',', ''))
    except:
        df2['Sellvol'] = pd.to_numeric(df2['Sellvol'])
        pass
    try:
        df2['BuySellvol'] = pd.to_numeric(df2['BuySellvol'].str.replace(',', ''))
    except:
        df2['BuySellvol'] = pd.to_numeric(df2['BuySellvol'])
        pass
    clean_space(df2)

    # df.to_sql(name = 'tbl_institutional_investors',con=engine, if_exists = 'append',index = False)

    url = f'https://www.tpex.org.tw/web/stock/3insti/sitc_trading/sitctr_result.php?l=zh-tw&t=D&type=sell&_={millisec}'
    resp = requests.get(url)
    data = resp.json()
    columns = ['Datetime', 'Stockcode', 'Stockname', 'Buyvol', 'Sellvol', 'BuySellvol']
    df3 = pd.DataFrame(data['aaData'],columns=columns)
    df3['Datetime'] = today
    df3['Tag'] = '投信'
    try:
        df3['Buyvol'] = pd.to_numeric(df3['Buyvol'].str.replace(',', ''))
    except:
        df3['Buyvol'] = pd.to_numeric(df3['Buyvol'])
        pass
    try:
        df3['Sellvol'] = pd.to_numeric(df3['Sellvol'].str.replace(',', ''))
    except:
        df3['Sellvol'] = pd.to_numeric(df3['Sellvol'])
        pass
    try:
        df3['BuySellvol'] = pd.to_numeric(df3['BuySellvol'].str.replace(',', ''))
    except:
        df3['BuySellvol'] = pd.to_numeric(df3['BuySellvol'])
        pass
    clean_space(df3)

    # df.to_sql(name = 'tbl_institutional_investors',con=engine, if_exists = 'append',index = False)

    if text == '投信買超':
        invest = pd.concat([df,df2,df3],axis=0, ignore_index=True)
        invest = invest.sort_values(by='BuySellvol',ascending=False).reset_index(drop=True)
        invest.index += 1
        invest_return = invest[['Stockcode','Stockname','BuySellvol']].head(10)
        columns = ['股號','名稱','買賣超']
        invest_return.columns = columns
        invest_return['買賣超'] = invest_return['買賣超'].astype(int)
        invest_return['買賣超'] = invest_return['買賣超'].astype(str) + '張'

        # 将DataFrame转换为字符串，包含索引
        result_str = invest_return.to_string(index=True)
        return result_str
    
    elif text == '投信賣超':
        invest = pd.concat([df,df2,df3],axis=0, ignore_index=True)
        invest = invest.sort_values(by='BuySellvol',ascending=True).reset_index(drop=True)
        invest.index += 1
        invest_return = invest[['Stockcode','Stockname','BuySellvol']].head(10)
        columns = ['股號','名稱','買賣超']
        invest_return.columns = columns
        invest_return['買賣超'] = invest_return['買賣超'].astype(int)
        invest_return['買賣超'] = invest_return['買賣超'].astype(str) + '張'

        # 将DataFrame转换为字符串，包含索引
        result_str = invest_return.to_string(index=True)
        return result_str

#即時報價
def get_price_old(stock):
    url = f'https://srvsolgw.capital.com.tw/info/Query.aspx?stocks={stock}&types=Open,High,Low,Deal,DQty,YDay'
    resp = requests.get(url)
    data = resp.text
    pattern = re.compile(r'StockID=(\d+),Open=([\d.]+),High=([\d.]+),Low=([\d.]+),Deal=([\d.]+),DQty=(\d+),YDay=([\d.]+)')

    matches = pattern.findall(data)

    columns = ['股號', '開盤價', '最高價', '最低價', '現價', '成交量', '昨日收盤價']
    df = pd.DataFrame(matches, columns=columns)
    df['漲跌幅'] = round((df['現價'].astype(float) - df['昨日收盤價'].astype(float))/df['昨日收盤價'].astype(float)*100,2)

    numeric_columns = ['開盤價', '最高價', '最低價', '現價', '成交量', '昨日收盤價','漲跌幅']
    df[numeric_columns] = df[numeric_columns].astype(float)

    stock_id = df['股號'].iloc[0]
    current_price = df['現價'].iloc[0]
    trade_volume = df['成交量'].iloc[0]
    highlow = df['漲跌幅'].iloc[0]

    if highlow > 0:
        text = f"股號:{stock_id}\n現價:{current_price}元\n成交量:{trade_volume}張\n漲跌幅:▲{highlow}%"
    elif highlow < 0:
        text = f"股號:{stock_id}\n現價:{current_price}元\n成交量:{trade_volume}張\n漲跌幅:▼{highlow}%"
    else:
        text = f"股號:{stock_id}\n現價:{current_price}元\n成交量:{trade_volume}張\n漲跌幅:{highlow}%"
    
    return text

def get_price(stock_id):
    url = f"https://tw.quote.finance.yahoo.net/quote/q?type=ta&perd=d&mkt=10&sym={stock_id}&v=1&callback=jQuery111302872649618000682_1649814120914&_=1649814120915"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36'}
    res = requests.get(url,headers=headers)

    # 最新價格
    current = [l for l in res.text.split('{') if len(l)>=58][-1]
    current = current.replace('"','').split(',')
    # 昨日價格
    yday = float(re.search(':.*',[l for l in res.text.split('{') if len(l)>=58][-2].split(',')[4]).group()[1:])

    df = pd.DataFrame({
        '開盤價':float(re.search(':.*',current[1]).group()[1:]),
        '最高價':float(re.search(':.*',current[2]).group()[1:]),
        '最低價':float(re.search(':.*',current[3]).group()[1:]),
        '現價':float(re.search(':.*',current[4]).group()[1:]),
        '成交量':float(re.search(':.*',current[5].replace('}]','')).group()[1:]),
        '漲跌幅':round((float(re.search(':.*',current[4]).group()[1:])/yday-1)*100,2)
    },index=[stock_id]).reset_index()
    df['名稱'] = df['index'].map(stock_dict)
    print(df)

    numeric_columns = ['開盤價', '最高價', '最低價', '現價', '成交量','漲跌幅']
    df[numeric_columns] = df[numeric_columns].astype(float)

    stock_id = df['index'].iloc[0]
    stock_name = df['名稱'].iloc[0]
    current_price = df['現價'].iloc[0]
    trade_volume = df['成交量'].iloc[0]
    highlow = df['漲跌幅'].iloc[0]

    if highlow > 0:
        text = f"股號:{stock_id}\n名稱:{stock_name}\n現價:{current_price}元\n成交量:{trade_volume}張\n漲跌幅:▲{highlow}%"
    elif highlow < 0:
        text = f"股號:{stock_id}\n名稱:{stock_name}\n現價:{current_price}元\n成交量:{trade_volume}張\n漲跌幅:▼{highlow}%"
    else:
        text = f"股號:{stock_id}\n名稱:{stock_name}\n現價:{current_price}元\n成交量:{trade_volume}張\n漲跌幅:{highlow}%"
    print(text)
    return text
    

#查個股融資融券
def stock_MarginPurchaseShortSale(stock):
    date = datetime.now().date() - timedelta(days=30)
    url = "https://api.finmindtrade.com/api/v4/data"
    parameter = {
        "dataset": "TaiwanStockMarginPurchaseShortSale",
        "data_id": f"{stock}",
        "start_date": f"{date}",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRlIjoiMjAyMy0xMS0yNCAxOTo1NTo1NSIsInVzZXJfaWQiOiJKZWZmaHVhbmciLCJpcCI6IjYxLjIzMS41Ljc1In0.g86TUOTpETIiRWvYQdBGXXP3LugXYI0I5arWVTYa3TY", # 參考登入，獲取金鑰
    }
    data = requests.get(url, params=parameter)
    data = data.json()
    data = pd.DataFrame(data['data'])

    fig, axs = plt.subplots(2)
    data['date'] = pd.to_datetime(data['date'])

    axs[0].plot(data['date'].dt.strftime('%d'), data['MarginPurchaseBuy']-data['MarginPurchaseCashRepayment']-data['MarginPurchaseSell'], label='融資')
    axs[0].plot(data['date'].dt.strftime('%d'), data['ShortSaleSell']-data['ShortSaleBuy']-data['ShortSaleCashRepayment'], label='融券')
    axs[0].set_title(f'{stock_dict[stock]}({stock})近一個月融資融券增減', fontproperties=font_prop)
    axs[0].set_xticks([])  # 隐藏 x 轴刻度

    axs[1].plot(data['date'].dt.strftime('%d'), data['MarginPurchaseTodayBalance'], label='融資')
    axs[1].plot(data['date'].dt.strftime('%d'), data['ShortSaleTodayBalance'], label='融券')
    axs[1].set_title(f'{stock_dict[stock]}({stock})近一個月融資融券餘額', fontproperties=font_prop)

    axs[0].legend(prop=font_prop)
    axs[1].legend(prop=font_prop)

    plt.savefig('stockMarginPurchaseShortSale.jpg')
    plt.close() # 殺掉記憶體中的圖片
    return Imgur.showImgur("stockMarginPurchaseShortSale")

def MarginPurchaseShortSale():
    date = datetime.now().date() - relativedelta(months=6)
    date_first = datetime(date.year, 1, 1).strftime('%Y-%m-%d')
    url = "https://api.finmindtrade.com/api/v4/data"
    parameter = {
        "dataset": "TaiwanStockTotalMarginPurchaseShortSale",
        "start_date": f"{date_first}",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRlIjoiMjAyMy0xMS0yNCAxOTo1NTo1NSIsInVzZXJfaWQiOiJKZWZmaHVhbmciLCJpcCI6IjYxLjIzMS41Ljc1In0.g86TUOTpETIiRWvYQdBGXXP3LugXYI0I5arWVTYa3TY", # 參考登入，獲取金鑰
    }
    data = requests.get(url, params=parameter)
    data = data.json()
    data = pd.DataFrame(data['data'])
    data.head(3)
    df = data[['TodayBalance','date','name']]

    fig, axs = plt.subplots(2)
    df['date'] = pd.to_datetime(df['date'])
    axs[0].plot(df[df['name'] == 'ShortSale']['date'].dt.strftime('%m/%d'), df[df['name'] == 'ShortSale']['TodayBalance'],label='融券餘額(張)', color='#02DF82')
    axs[1].plot(df[df['name'] == 'MarginPurchaseMoney']['date'].dt.strftime('%m/%d'), df[df['name'] == 'MarginPurchaseMoney']['TodayBalance']/100000000,label='融資餘額(億)',color='#FF5151')

    axs[0].set_xticks([])
    axs[1].xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xticks(rotation=45,fontsize=8)
    axs[1].ticklabel_format(style='sci',scilimits=(-1,4),axis='y')
    axs[0].legend(prop=font_prop)
    axs[1].legend(prop=font_prop)


    for a,b in zip(df[df['name'] == 'MarginPurchaseMoney'].iloc[::10]['date'].dt.strftime('%m/%d'), round(df[df['name'] == 'MarginPurchaseMoney'].iloc[::10]['TodayBalance']/100000000,0)):
        axs[1].text(a,b,b, ha='center', va='bottom', fontsize= 6)


    plt.savefig('MarginPurchaseShortSale.jpg')
    plt.close() # 殺掉記憶體中的圖片
    return Imgur.showImgur("MarginPurchaseShortSale")



#股價走勢
def price_trend(stock):
    end = datetime.now().date() # 資料結束時間
    start = datetime.now().date() - relativedelta(months=6) # 資料開始時間
    df = yf.download(f'{stock}.TW', start=start, end=end).reset_index()
    #MA
    df['5MA'] = df['Close'].rolling(window=5).mean()
    df['10MA'] = df['Close'].rolling(window=10).mean()
    df['20MA'] = df['Close'].rolling(window=20).mean()
    df['60MA'] = df['Close'].rolling(window=60).mean()
    df['13MA'] = df['Close'].rolling(window=13).mean()
    #MACD
    df['EMA'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['Close'].ewm(span=12).mean() - df['EMA']
    df['MACD Histogram'] = df['MACD'] - df['MACD'].ewm(span=9).mean()
    # #RSI
    # df['Up Move'] = df['Close'].diff().apply(lambda x: x if x > 0 else 0)
    # df['Down Move'] = df['Close'].diff().apply(lambda x: -x if x < 0 else 0)
    
    # df['Avg Gain'] = df['Up Move'].rolling(window=14).mean()
    # df['Avg Loss'] = df['Down Move'].rolling(window=14).mean()
    
    # df['RS'] = df['Avg Gain'] / df['Avg Loss']
    # df['RSI'] = 100 - (100 / (1 + df['RS']))
    
    #布林
    df['Upper Band'] = df['13MA'] + (1.5 * df['Close'].std())
    df['Lower Band'] = df['13MA'] - (1.5 * df['Close'].std())
    df.drop(['13MA'], axis=1, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])  # Convert Date column to datetime
    
    # 繪製圖表函式
    bk_df = df
    bk_df.index = bk_df["Date"].dt.strftime('%Y-%m-%d')
    fig = go.Figure(data=[go.Candlestick(x=bk_df.index,
                        open=bk_df['Open'],
                        high=bk_df['High'],
                        low=bk_df['Low'],
                        close=bk_df['Close'],
                        increasing_line_color='red',
                        decreasing_line_color='green',
                        name = "K 線")])

    # 交易量
    fig.add_trace(go.Bar(x=bk_df.index, y=bk_df['Volume'],
                        marker={'color': 'green'}, yaxis='y2',
                            name = "交易量"))

    # 找出需要繪製的欄位
    columns = bk_df.columns
    exclude_columns = ['index','Date', 'Open', 'High',
                        'Low', 'Close', 'Adj Close', 'Volume']
    remain_columns = [col for col in columns if
                        col not in exclude_columns]
    min_close = bk_df['Close'].min() - bk_df['Close'].std()
    max_close = bk_df['Close'].max() + bk_df['Close'].std()
    # 繪製技術指標
    for i in remain_columns:
        if min_close <= bk_df[i].mean() <= max_close:
            fig.add_trace(go.Scatter(x=bk_df.index, y=bk_df[i],
                                    mode='lines', name=i))
        else:
            fig.add_trace(go.Scatter(x=bk_df.index, y=bk_df[i],
                                    mode='lines', yaxis='y3', name=i))

    # 加入懸停十字軸
    fig.update_xaxes(showspikes=True, spikecolor="gray",
                    spikemode="toaxis")
    fig.update_yaxes(showspikes=True, spikecolor="gray",
                    spikemode="across")
    # 更新畫布大小並增加範圍選擇
    fig.update_layout(
        height=800,
        width=1200,
        yaxis={'domain': [0.35, 1]},
        yaxis2={'domain': [0.15, 0.3]},
        # 若要重疊 y1 和 y3, 可以改成
        # yaxis3=dict(overlaying='y', side='right')
        yaxis3={'domain': [0, 0.15]},
        title=f"{stock}",
        xaxis={
            # 範圍選擇格
            'rangeselector': {
                'buttons': [
                    {'count': 1, 'label': '1M',
                    'step': 'month', 'stepmode': 'backward'},
                    {'count': 6, 'label': '6M',
                    'step': 'month', 'stepmode': 'backward'},
                    {'count': 1, 'label': '1Y',
                    'step': 'year', 'stepmode': 'backward'},
                    {'step': 'all'}
                ]
            },
            # 範圍滑動條
            'rangeslider': {
                'visible': True,
                'thickness': 0.01,  # 滑動條的高度
                'bgcolor': "#E4E4E4"  # 背景色
            },
            'type': 'date'
        }
    )

    # 移除非交易日空值
    # 生成該日期範圍內的所有日期
    all_dates = pd.date_range(start=bk_df.index.min(),
                                end=bk_df.index.max())
    # 找出不在資料中的日期
    breaks = all_dates[~all_dates.isin(bk_df.index)]
    dt_breaks = breaks.tolist() # 轉換成列表格式
    fig.update_xaxes(rangebreaks=[{'values': dt_breaks}])
    fig.write_image('pricetrend.jpg')
    return Imgur.showImgur("pricetrend")

#股票股利
def dividend_cash(stock):
    date = datetime.now().date() - relativedelta(years=6)
    date_first = datetime(date.year, 1, 1).strftime('%Y-%m-%d')
    url = "https://api.finmindtrade.com/api/v4/data"
    parameter = {
        "dataset": "TaiwanStockDividend",
        "data_id": f"{stock}",
        "start_date": f"{date_first}",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRlIjoiMjAyMy0xMS0yNyAxMTowMzowMCIsInVzZXJfaWQiOiJKZWZmaHVhbmciLCJpcCI6IjYwLjI1MC4xMTYuMTE4In0.Cv-EZoBQb7o1J9N7noD5AFWoaWN2jvcOsyUYb7qoIzQ", # 參考登入，獲取金鑰
    }
    data = requests.get(url, params=parameter)
    data = data.json()
    data = pd.DataFrame(data['data'])
    df = data[['stock_id','date','StockEarningsDistribution','CashEarningsDistribution']]
    df['date'] = pd.to_datetime(data['date'])

    # 按照年份進行分組並對StockEarningsDistribution和CashEarningsDistribution進行求和
    grouped_data = df.groupby(df['date'].dt.year)[['StockEarningsDistribution', 'CashEarningsDistribution']].sum().reset_index()
    grouped_data.columns = ['日期','股票股利','現金股利']


    fig = plt.figure(figsize=(10, 6))
    plt.bar(grouped_data['日期'], grouped_data['現金股利'], color=['#84C1FF'], label='現金股利',width=0.4,align='edge')
    plt.bar(grouped_data['日期'], grouped_data['股票股利'], color=['#FF5151'], label='股票股利',width=0.4)
    plt.xlabel('月份', fontproperties=font_prop)
    plt.ylabel('營收', fontproperties=font_prop)
    plt.title(f'{stock_dict[stock]}({stock})股票股利', fontproperties=font_prop)
    plt.legend(prop=font_prop)
    plt.tight_layout()
    fig.savefig('dividendcash.jpg')
    return Imgur.showImgur("dividendcash")

#月營收
def get_revenue(stock):
    date = datetime.now().date() - relativedelta(years=2)
    date_first = datetime(date.year, 1, 1).strftime('%Y-%m-%d')
    url = "https://api.finmindtrade.com/api/v4/data"
    parameter = {
        "dataset": "TaiwanStockMonthRevenue",
        "data_id": f"{stock}",
        "start_date": f"{date_first}",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRlIjoiMjAyMy0xMS0yNyAxMTowMzowMCIsInVzZXJfaWQiOiJKZWZmaHVhbmciLCJpcCI6IjYwLjI1MC4xMTYuMTE4In0.Cv-EZoBQb7o1J9N7noD5AFWoaWN2jvcOsyUYb7qoIzQ", # 參考登入，獲取金鑰
    }
    data = requests.get(url, params=parameter)
    data = data.json()
    data = pd.DataFrame(data['data'])
    data['date'] = pd.to_datetime(data['date'])
    fig = plt.figure(figsize=(10, 6))
    plt.bar(data['date'].dt.strftime('%Y/%m'), data['revenue'], color=['#B8B8DC'], label='月營收')
    plt.xlabel('月份', fontproperties=font_prop)
    plt.ylabel('營收', fontproperties=font_prop)
    plt.title(f'{stock_dict[stock]}({stock})月營收', fontproperties=font_prop)
    plt.xticks(rotation=45)  # 如果日期比較長，可以旋轉 x 軸標籤
    plt.legend(prop=font_prop)
    plt.tight_layout()  # 自動調整圖表布局，以避免標籤被截斷
    fig.savefig('revenue.jpg')
    return Imgur.showImgur("revenue")




