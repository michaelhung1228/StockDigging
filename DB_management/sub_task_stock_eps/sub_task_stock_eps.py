"""
列出最近一季EPS高於過去八季(n>8)(EPS兩年來新高)的股票
"""
import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3
from yattag import Doc

#進入DBs資料夾開stock_list.db
dir_temp = os.getcwd()
dir_temp = dir_temp + '/DBs'
os.chdir(dir_temp)
conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

stock_url = 'https://tw.stock.yahoo.com/q/ta?s='
#進入stock database資料夾 access個股database
#change path to stock databases
path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)

result_stock = []
result_color = []
colors = [0,0,0,0,0,0,0,0,0,0]

#尋找最新的一季 (所有股票中最近一季有更新的, 最近一季還未更新的將不列入)
#找出資料庫中最近一季是哪一季
latest_date_inDB = datetime.strptime('1990-1', "%Y-%m")
cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business  from stock_list")
for current_entry in cursor:
    if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
        db_name = current_entry[0] + '.db'
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()
        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_quarter')
        date_ID_str = cursor_stock.fetchone()[0]
        if date_ID_str == None:
            continue
        date_inDB = datetime.strptime(date_ID_str, "%Y-%m")
        if date_inDB > latest_date_inDB:
            latest_date_inDB = date_inDB
latest_date_inDB_str = str(latest_date_inDB.year) + '-' + str(latest_date_inDB.month)

#找出EPS創新高的股票
cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business  from stock_list")
for current_entry in cursor:
    if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
        db_name = current_entry[0] + '.db'
        #print(db_name)
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()
        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_quarter')
        date_ID_str = cursor_stock.fetchone()[0]
        #還未公布最近一季資料的股票不列出
        if (date_ID_str == None) or (date_ID_str != latest_date_inDB_str):
            conn_stock.close()
            continue
        #抓出最新一筆資料的rowid
        sql_cmd = 'select rowid from stock_quarter where date_ID =\'' + date_ID_str + '\''
        c_stock.execute(sql_cmd)
        rowid = c_stock.fetchone()
        if rowid == None:
            conn_stock.close()
            continue
        #由rowid抓出最新一筆資料的EPS
        sql_cmd = 'select EPS from stock_quarter where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        EPS_tmp0 = c_stock.fetchone()[0]

        n = 0
        while 1:
            if (rowid[0] - n - 1) < 1:
                break
            sql_cmd = 'select EPS from stock_quarter where rowid =' + str(rowid[0] - n - 1)
            c_stock.execute(sql_cmd)
            EPS_tmp1 = c_stock.fetchone()[0]
            if EPS_tmp0 > EPS_tmp1:
                n = n +1
            else:
                break

        if n > 8:
            print(db_name)
            sql_cmd = 'select EPS from stock_quarter where rowid =' + str(rowid[0] - 1)
            c_stock.execute(sql_cmd)
            EPS_tmp1 = c_stock.fetchone()[0]
            quarter_growth = float(EPS_tmp0) - float(EPS_tmp1)
            quarter_growth = round(quarter_growth, 2)
            sql_cmd = 'select EPS from stock_quarter where rowid =' + str(rowid[0] - 4)
            c_stock.execute(sql_cmd)
            EPS_tmp1 = c_stock.fetchone()[0]
            year_growth = float(EPS_tmp0) - float(EPS_tmp1)
            year_growth = round(year_growth, 2)
            result_stock.append([current_entry[0], current_entry[1], current_entry[4], date_ID_str, str(n+1), EPS_tmp0, year_growth, quarter_growth])
            for i in range(0,7):
                colors[i] = 0

            result_color.append([colors[0], colors[1], colors[2], colors[3], colors[4], colors[5], colors[6], colors[7]])
            print(n+1)
        conn_stock.close()
conn.close()

print(os.getcwd())
os.chdir('..')
print(os.getcwd())
os.chdir('..')
dir_temp = os.getcwd()
dir_temp = dir_temp + '/temp_pages'
os.chdir(dir_temp)
print(os.getcwd())

filename = 'stock_eps.html'
f= open(filename,"w+", encoding="utf-8")
doc, tag, text = Doc().tagtext()


#beginning of the html page
temp_html_content = """
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>亮晶晶乾洗店</title>
</head>
<body>
"""
f.write(temp_html_content)


with tag('table', border = '0'):
    with tag('tr'):
        with tag('td', align = 'center'):
            text('最後資料更新')
        with tag('td', align = 'center'):
            text(latest_date_inDB_str + '季')

doc.asis('<br>')
f.write(doc.getvalue())
doc, tag, text = Doc().tagtext()
f.write('<table border=1>')
with tag('tr'):
    with tag('td', align = 'center'):
        text('代碼')
    with tag('td', align = 'center'):
        text('公司')
    with tag('td', align = 'center'):
        text('產業')
    with tag('td', align = 'center'):
        text('季數新高')
    with tag('td', align = 'center'):
        text('最近一季EPS')
    with tag('td', align = 'center'):
        text('季增')
    with tag('td', align = 'center'):
        text('年增')
cnt = 0
for stock in result_stock:
    with tag('tr'):
        with tag('td', align = 'center'):
            with tag('a', href = stock_url + stock[0], target='_blank'):
                text(stock[0])
        with tag('td', align = 'center'):
            text(stock[1])
        with tag('td', align = 'center'):
            text(stock[2])
        with tag('td', align = 'center'):
            text(stock[4])
        with tag('td', align = 'center'):
            text(stock[5])
        with tag('td', align = 'center'):
            text(stock[6])
        with tag('td', align = 'center'):
            text(stock[7])
    cnt = cnt + 1
f.write(doc.getvalue())
f.write('</table>')
#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()