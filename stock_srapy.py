import requests
import time
import pandas as pd
import datetime
import pymysql
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings("ignore")


# 數據庫連接訊息
#engine = create_engine("mysql+pymysql://user:password@host:port/databasename?charset=utf8") 
engine = create_engine("mysql+pymysql://admin:1q2w3e4r5t_@mysql00.cboucftgvuzl.ap-northeast-1.rds.amazonaws.com:3306/stock?charset=utf8")
conn = pymysql.connect(host='mysql00.cboucftgvuzl.ap-northeast-1.rds.amazonaws.com',user='admin',passwd='1q2w3e4r5t_',db='stock', port = 3306,charset="utf8")


def clean_space(data):
    for col in data.columns:
        if type(data[col][0])==str:
            data[col] = data[col].str.strip()
            data[col] = data[col].str.replace(' ','')
            data[col] = data[col].str.replace('\u3000','')
    return data


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
df['Buyvol'] = pd.to_numeric(df['Buyvol'].str.replace(',', ''))
df['Sellvol'] = pd.to_numeric(df['Sellvol'].str.replace(',', ''))
df['BuySellvol'] = pd.to_numeric(df['BuySellvol'].str.replace(',', ''))
clean_space(df)
df.to_sql(name = 'tbl_institutional_investors',con=engine, if_exists = 'append',index = False)


millisec = int(round(time.time() * 1000))
url = f'https://www.tpex.org.tw/web/stock/3insti/sitc_trading/sitctr_result.php?l=zh-tw&t=D&type=buy&_={millisec}'
resp = requests.get(url)
data = resp.json()
columns = ['Datetime', 'Stockcode', 'Stockname', 'Buyvol', 'Sellvol', 'BuySellvol']
df = pd.DataFrame(data['aaData'],columns=columns)
df['Datetime'] = today
df['Tag'] = '投信'
df['Buyvol'] = pd.to_numeric(df['Buyvol'].str.replace(',', ''))
df['Sellvol'] = pd.to_numeric(df['Sellvol'].str.replace(',', ''))
df['BuySellvol'] = pd.to_numeric(df['BuySellvol'].str.replace(',', ''))
clean_space(df)
df.to_sql(name = 'tbl_institutional_investors',con=engine, if_exists = 'append',index = False)

url = f'https://www.tpex.org.tw/web/stock/3insti/sitc_trading/sitctr_result.php?l=zh-tw&t=D&type=sell&_={millisec}'
resp = requests.get(url)
data = resp.json()
columns = ['Datetime', 'Stockcode', 'Stockname', 'Buyvol', 'Sellvol', 'BuySellvol']
df = pd.DataFrame(data['aaData'],columns=columns)
df['Datetime'] = today
df['Tag'] = '投信'
df['Buyvol'] = pd.to_numeric(df['Buyvol'].str.replace(',', ''))
df['Sellvol'] = pd.to_numeric(df['Sellvol'].str.replace(',', ''))
df['BuySellvol'] = pd.to_numeric(df['BuySellvol'].str.replace(',', ''))
clean_space(df)
df.to_sql(name = 'tbl_institutional_investors',con=engine, if_exists = 'append',index = False)

