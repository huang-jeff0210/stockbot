import requests
import time
import pandas as pd
import re
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import Imgur
import mplfinance as mpf

# 设置中文字体
font_path = './msjh.ttc'
font_prop = FontProperties(fname=font_path)
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 修改中文字體
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
def get_price(stock):
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
    

#查融資融券
def MarginPurchaseShortSale(stock):
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

    plt.savefig('MarginPurchaseShortSale.jpg')
    plt.close() # 殺掉記憶體中的圖片
    return Imgur.showImgur("MarginPurchaseShortSale")

#股價走勢
def price_trend(stock):
    date = datetime.now().date() - timedelta(years=1)
    url = "https://api.finmindtrade.com/api/v4/data"
    parameter = {
        "dataset": "TaiwanStockPrice",
        "data_id": f"{stock}",
        "start_date": f"{date}",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRlIjoiMjAyMy0xMS0yNiAxNzo0MDozMiIsInVzZXJfaWQiOiJKZWZmaHVhbmciLCJpcCI6IjYxLjIzMS41LjE3In0.KM9MXxIahnfxhqhKWjzSkGZ7gg0IDeUqGaw5LW7azjY"
    }
    response = requests.get(url, params=parameter)
    data = response.json()
    df = pd.DataFrame(data["data"])
    df["date"] = pd.to_datetime(df["date"])
    df.head(3)

    df = df[["date", "Trading_Volume", "open", "max", "min", "close"]]
    columns = ['Date', 'Volume', 'Open', 'High', 'Low', 'Close']
    df.columns = columns

    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df.set_index('Date', inplace=True)

    df['5MA'] = df['Close'].rolling(window=5).mean()
    df['10MA'] = df['Close'].rolling(window=10).mean()
    df['20MA'] = df['Close'].rolling(window=20).mean()
    df['60MA'] = df['Close'].rolling(window=60).mean()
    df['120MA'] = df['Close'].rolling(window=120).mean()

    df = df.dropna()
    mc = mpf.make_marketcolors(up='r',down='g',edge='',wick='inherit',volume='inherit')

    added_plots = {"5MA" : mpf.make_addplot(df['5MA']),
                "10MA" : mpf.make_addplot(df['10MA']),
                "20MA" : mpf.make_addplot(df['20MA']),
                "60MA" : mpf.make_addplot(df['60MA']),
                "120MA" : mpf.make_addplot(df['120MA']),
    }
    fig, axes = mpf.plot(df, type='candle', style='yahoo', volume=True, addplot=list(added_plots.values()), returnfig=True)

    axes[0].legend([None]*(len(added_plots)+2))
    handles = axes[0].get_legend().legendHandles
    axes[0].legend(handles=handles[:],labels=list(added_plots.keys()))
    fig.tight_layout()
    fig.savefig('pricetrend.jpg')
    return Imgur.showImgur("pricetrend")








