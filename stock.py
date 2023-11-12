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
engine = create_engine("mysql+pymysql://jobuser:1q2w3e4r5t_@127.0.0.1:3306/stock?charset=utf8")
conn = pymysql.connect(host='127.0.0.1',user='jobuser',passwd='1q2w3e4r5t_',db='stock', port = 3306,charset="utf8")


def clean_space(data):
    for col in data.columns:
        if type(data[col][0])==str:
            data[col] = data[col].str.strip()
            data[col] = data[col].str.replace(' ','')
            data[col] = data[col].str.replace('\u3000','')
    return data

def get_invest_buy():
    mycursor = conn.cursor()
    sql = '''
    select Stockcode, Stockname, BuySellvol
    FROM stock.tbl_institutional_investors
    where `Datetime` = (select max(`Datetime`) FROM stock.tbl_institutional_investors) and Tag = '投信'
    order by BuySellvol desc
    limit 10
    '''
    mycursor.execute(sql)

    invest = pd.DataFrame(mycursor.fetchall(),columns=['股號','名稱','股數'])
    invest['張數'] = round(invest['股數']/1000,0).astype(int)
    return invest