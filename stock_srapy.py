import requests
import time
import pandas as pd
import re
import datetime
import pymysql
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings("ignore")


# 數據庫連接訊息
#engine = create_engine("mysql+pymysql://user:password@host:port/databasename?charset=utf8") 
# engine = create_engine("mysql+pymysql://admin:1q2w3e4r5t_@mysql00.cboucftgvuzl.ap-northeast-1.rds.amazonaws.com:3306/stock?charset=utf8")
# conn = pymysql.connect(host='mysql00.cboucftgvuzl.ap-northeast-1.rds.amazonaws.com',user='admin',passwd='1q2w3e4r5t_',db='stock', port = 3306,charset="utf8")


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
    

