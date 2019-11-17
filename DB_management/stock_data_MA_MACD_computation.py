import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3

import index_computation

DateSearch = re.compile(r'(\d\d\d\d)(\d\d)(\d\d)')

dir_temp = os.getcwd()
dir_temp = dir_temp + '/DBs'
os.chdir(dir_temp)
conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)
print(os.getcwd())

delta_1day = timedelta(days = 1) #delta_1day
End_date = datetime.today()

cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business  from stock_list")
for current_entry in cursor:
    if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
        db_name = current_entry[0] + '.db'
        print(db_name)
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()
        #MA computation
        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_day where MA3 IS NOT NULL')
        max_id = cursor_stock.fetchone()[0]
        date_delta_tmp = delta_1day
        if max_id == None:
            cursor_stock = c_stock.execute('SELECT min(date_ID) FROM stock_day')
            max_id = cursor_stock.fetchone()[0]
            date_delta_tmp = timedelta(days = 0)
        max_id = max_id.replace('-','')
        Date = DateSearch.search(max_id)
        Start_date = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))
        Start_date = Start_date + date_delta_tmp
        index_computation.MA_computation('stock_day', Start_date, End_date, delta_1day, c_stock, conn_stock, 1)
        #MACD computation
        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_day where DI IS NOT NULL')
        max_id = cursor_stock.fetchone()[0]
        date_delta_tmp = delta_1day
        if max_id == None:
            cursor_stock = c_stock.execute('SELECT min(date_ID) FROM stock_day')
            max_id = cursor_stock.fetchone()[0]
            date_delta_tmp = timedelta(days = 0)
        max_id = max_id.replace('-','')
        Date = DateSearch.search(max_id)
        Start_date = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))
        Start_date = Start_date + date_delta_tmp
        index_computation.MACD_computation('stock_day', Start_date, End_date, delta_1day, c_stock, conn_stock, 1)
        conn_stock.close()

conn.close()