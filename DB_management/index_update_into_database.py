import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3

import index_computation

input_arg = sys.argv

dir_temp = os.getcwd()
dir_temp = dir_temp + '/DBs'
os.chdir(dir_temp)

conn = sqlite3.connect('TAIEX.db')
c = conn.cursor()

sql_cmd = 'DELETE FROM TAIEX WHERE TEMP = 1'
c.execute(sql_cmd)
conn.commit()

url1_base = 'http://www.twse.com.tw/exchangeReport/FMTQIK?response=html&date=' #成交金額, 收盤指數, 漲跌點數
url2_base = 'http://www.twse.com.tw/indicesReport/MI_5MINS_HIST?response=html&date=' #開盤, 最高, 最低, 收盤指數
DateSearch = re.compile(r'(\d\d\d\d)(\d\d)(\d\d)')
delta_1day = timedelta(days = 1) #delta_1day
cursor = c.execute('SELECT max(date_ID) FROM TAIEX')
max_id = cursor.fetchone()[0]
max_id = max_id.replace('-','')

Date = DateSearch.search(max_id)
Start_date = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))
Start_date = Start_date + delta_1day

former_url = None
Start_date_ptr = Start_date
End_date = datetime.today()
print('Print index from ' + str(Start_date) + ' to ' + str(End_date))

while Start_date_ptr <= End_date:
    
    url = url2_base + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m")
    if url != former_url:
        url = url2_base + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m%d")
        print('Cool down for requesting web content')
        time.sleep(3)
        res = requests.get(url)
        former_url = url2_base + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m")
        if res.raise_for_status() != None:
            continue
    soup = bs4.BeautifulSoup(res.text, "lxml")
    trs = soup.find_all('tr')
    #print(trs[0])
    for tr in trs:
        soup1 = bs4.BeautifulSoup(str(tr), "lxml")
        tds = soup1.find_all('td')
        if tds == []:
        	continue
        #print(tds[0].getText().strip())
        date_str_from_table = tds[0].getText().strip()
        date_str = str(Start_date_ptr.year - 1911) + '/' + Start_date_ptr.strftime("%m") + '/' + Start_date_ptr.strftime("%d")
        if date_str == date_str_from_table:
            sql_cmd = 'INSERT INTO TAIEX (date_ID, open_index, highest_index, lowest_index, close_index) VALUES (\'' + str(Start_date_ptr.year) + '-' + \
            Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d") + '\',' + tds[1].getText().strip().replace(',','') + ',' \
                                                                                + tds[2].getText().strip().replace(',','') + ',' \
                                                                                + tds[3].getText().strip().replace(',','') + ',' \
                                                                                + tds[4].getText().strip().replace(',','') + ')'
            print(sql_cmd)
            c.execute(sql_cmd)
            conn.commit()
            print(date_str + ' ' + tds[1].getText().strip() + ' ' + tds[2].getText().strip() + ' ' + tds[3].getText().strip() + ' ' + tds[4].getText().strip())
            break

    Start_date_ptr = Start_date_ptr + delta_1day

cursor = c.execute('SELECT max(date_ID) FROM TAIEX where Volume IS NOT NULL')
max_id = cursor.fetchone()[0]
max_id = max_id.replace('-','')

Date = DateSearch.search(max_id)
Start_date = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))
Start_date = Start_date + delta_1day
Start_date_ptr = Start_date

cursor = c.execute('SELECT max(date_ID) FROM TAIEX')
max_id = cursor.fetchone()[0]
max_id = max_id.replace('-','')

Date = DateSearch.search(max_id)
End_date = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))

former_url = None
while Start_date_ptr <= End_date:
    url = url1_base + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m")
    if url != former_url:
        url = url1_base + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m%d")
        print('Cool down for requesting web content')
        time.sleep(3)
        res = requests.get(url)
        former_url = url1_base + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m")
        if res.raise_for_status() != None:
            continue
    soup = bs4.BeautifulSoup(res.text, "lxml")
    trs = soup.find_all('tr')
    for tr in trs:
        soup1 = bs4.BeautifulSoup(str(tr), "lxml")
        tds = soup1.find_all('td')
        if tds == []:
            continue
        date_str_from_table = tds[0].getText().strip()
        date_str = str(Start_date_ptr.year - 1911) + '/' + Start_date_ptr.strftime("%m") + '/' + Start_date_ptr.strftime("%d")
        if date_str == date_str_from_table:
            sql_cmd = 'UPDATE TAIEX set Volume =' + tds[2].getText().strip().replace(',','') +\
                                  ',Total =' + tds[5].getText().strip().replace(',','') + ' where date_ID =\''\
                                   + str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d") + '\''
            print(sql_cmd)
            c.execute(sql_cmd)
            conn.commit()
            print(date_str + ' ' + tds[2].getText().strip() + ' ' + tds[5].getText().strip())
            break
    Start_date_ptr = Start_date_ptr + delta_1day


#MA computation
cursor = c.execute('SELECT max(date_ID) FROM TAIEX where MA3 IS NOT NULL')
max_id = cursor.fetchone()[0]
date_delta_tmp = delta_1day
if max_id == None:
    cursor = c.execute('SELECT min(date_ID) FROM TAIEX')
    max_id = cursor.fetchone()[0]
    date_delta_tmp = timedelta(days = 0)
max_id = max_id.replace('-','')
Date = DateSearch.search(max_id)
Start_date = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))
Start_date = Start_date + date_delta_tmp
index_computation.MA_computation('TAIEX', Start_date, End_date, delta_1day, c, conn, 0)

#MACD computation
cursor = c.execute('SELECT max(date_ID) FROM TAIEX where DI IS NOT NULL')
max_id = cursor.fetchone()[0]
date_delta_tmp = delta_1day
if max_id == None:
    cursor = c.execute('SELECT min(date_ID) FROM TAIEX')
    max_id = cursor.fetchone()[0]
    date_delta_tmp = timedelta(days = 0)
max_id = max_id.replace('-','')
Date = DateSearch.search(max_id)
Start_date = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))
Start_date = Start_date + date_delta_tmp
index_computation.MACD_computation('TAIEX', Start_date, End_date, delta_1day, c, conn, 0)

conn.close()
