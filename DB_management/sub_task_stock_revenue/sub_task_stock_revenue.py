import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3
from yattag import Doc

dir_temp = os.getcwd()
dir_temp = dir_temp + '/DBs'
os.chdir(dir_temp)
conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

def is_number(num):
  pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
  result = pattern.match(num)
  if result:
    return True
  else:
    return False

#the latest date of stock market for P/E ratio
url1 = 'http://www.twse.com.tw/exchangeReport/BWIBBU_d?response=html&date=---yearmonthdate---&selectType=ALL' #P/E ration
url2 = 'https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/pera_result.php?l=zh-tw&o=htm&d=---yearmonthdate---&c=&s=0,asc'
stock_url = 'https://tw.stock.yahoo.com/q/ta?s='
#fetch the latest date according to TAI index
conn_tmp = sqlite3.connect('TAIEX.db')
c_tmp = conn_tmp.cursor()
cursor_tmp = c_tmp.execute('SELECT max(date_ID) FROM TAIEX')
latest_date_ID_str = cursor_tmp.fetchone()[0]
conn_tmp.close()

#transfer date from AC to ROC and fetch the webpage of P/E ratio
date_tmp1 = latest_date_ID_str.replace('-','')
DateSearch = re.compile(r'(\d\d\d\d)-(\d\d)-(\d\d)')
date_tmp = DateSearch.search(latest_date_ID_str)
date_tmp2 = str(int(date_tmp.group(1)) - 1911) + '/' + date_tmp.group(2) + '/' + date_tmp.group(3)
url1 = url1.replace('---yearmonthdate---', date_tmp1)
url2 = url2.replace('---yearmonthdate---', date_tmp2)
print('Cool down for requesting web content')
time.sleep(5)
res1 = requests.get(url1)
soup1 = bs4.BeautifulSoup(res1.text, "lxml")
print('Cool down for requesting web content')
time.sleep(5)
res2 = requests.get(url2)
soup2 = bs4.BeautifulSoup(res2.text, "lxml")

#change path to stock databases
path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)

#the current date is last month
Current_date = datetime.today()
Current_date = Current_date.replace(month = Current_date.month - 1, day = 1)
result_stock = []
result_color = []
colors = [0,0,0,0,0,0,0,0,0,0]
cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business  from stock_list")
for current_entry in cursor:
    if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
        db_name = current_entry[0] + '.db'
        #print(db_name)
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()
        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_month')
        date_ID_str = cursor_stock.fetchone()[0]
        if date_ID_str == None:
            conn_stock.close()
            continue
        #last date in stock_month, only print the latest data
        latest_date_inDB = datetime.strptime(date_ID_str, "%Y-%m")
        if (latest_date_inDB.year == Current_date.year) and (latest_date_inDB.month == Current_date.month):
            n = 0
            sql_cmd = 'select rowid from stock_month where date_ID =\'' + date_ID_str + '\''
            c_stock.execute(sql_cmd)
            rowid = c_stock.fetchone()
            if rowid == None:
                conn_stock.close()
                continue
            sql_cmd = 'select revenue from stock_month where rowid =' + str(rowid[0] - n)
            c_stock.execute(sql_cmd)
            volume_tmp0 = c_stock.fetchone()[0]
            #count the period
            while 1:
                if (rowid[0] - n - 1) < 1:
                    break
                sql_cmd = 'select revenue from stock_month where rowid =' + str(rowid[0] - n - 1)
                c_stock.execute(sql_cmd)
                volume_tmp1 = c_stock.fetchone()[0]
                if volume_tmp0 > volume_tmp1:
                    n = n +1
                else:
                    break
            if n > 24:
                if current_entry[3] == '上市':
                    td = soup1.find(string=str(current_entry[0]))
                    if td == None:
                        conn_stock.close()
                        continue
                    soup_temp = bs4.BeautifulSoup(str(td.parent.parent), "lxml")
                    tds = soup_temp.find_all('td')
                    PER = tds[4].getText().strip()
                    PBR = tds[5].getText().strip()
                elif current_entry[3] == '上櫃':
                    td = soup2.find(string=str(current_entry[0]))
                    if td == None:
                        conn_stock.close()
                        continue
                    soup_temp = bs4.BeautifulSoup(str(td.parent.parent), "lxml")
                    tds = soup_temp.find_all('td')
                    PER = tds[2].getText().strip()
                    PBR = tds[6].getText().strip()

                sql_cmd = 'select revenue from stock_month where rowid =' + str(rowid[0])
                c_stock.execute(sql_cmd)
                volume_tmp0 = c_stock.fetchone()[0]
                #fetch the revenue of last month
                sql_cmd = 'select revenue from stock_month where rowid =' + str(rowid[0] - 1)
                c_stock.execute(sql_cmd)
                volume_tmp1 = c_stock.fetchone()[0]
                #fetch the revenue of last year
                sql_cmd = 'select revenue from stock_month where rowid =' + str(rowid[0] - 12)
                c_stock.execute(sql_cmd)
                volume_tmp2 = c_stock.fetchone()[0]
                #年增率計算, 以防去年沒有營收的公司
                if float(volume_tmp2) == 0:
                    annual_growth = 10
                else:
                    annual_growth = float(volume_tmp0)/float(volume_tmp2) - 1
                #月增率
                if float(volume_tmp1) == 0:
                    monthly_growth = 10
                else:
                    monthly_growth = float(volume_tmp0)/float(volume_tmp1) - 1
                annual_growth = round(annual_growth*100, 2)
                monthly_growth = round(monthly_growth*100, 2)
                result_stock.append([current_entry[0], current_entry[1], current_entry[4], str(n+1), PER, PBR, str(annual_growth) + '%' , str(monthly_growth) + '%'])
                for i in range(0,9):
                    colors[i] = 0
                if (current_entry[4] == '建材營造業') or (current_entry[4] == '生技醫療業'):
                    colors[2] = 1
                if is_number(PER):
                    if float(PER) < 15:
                        colors[4] = 1
                if annual_growth > 15:
                    colors[6] = 1
                if monthly_growth > 30:
                    colors[7] = 1
                result_color.append([colors[0], colors[1], colors[2], colors[3], colors[4], colors[5], colors[6], colors[7]])
                print(db_name)
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

filename = 'stock_revenue.html'
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
            text(str(Current_date.year) + '/' + str(Current_date.month))
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
        text('月數新高')
    with tag('td', align = 'center'):
        text('本益比')
    with tag('td', align = 'center'):
        text('淨值比')
    with tag('td', align = 'center'):
        text('年增率')
    with tag('td', align = 'center'):
        text('月增率')

cnt = 0
for stock in result_stock:
    with tag('tr'):
        with tag('td', align = 'center'):
            with tag('a', href = stock_url + stock[0], target='_blank'):
                text(stock[0])
        with tag('td', align = 'center'):
            text(stock[1])
        with tag('td', align = 'center'):
            if result_color[cnt][2] == 1:
                with tag('font', color = '#ffaf60'):
                    text(stock[2])
            else:
                text(stock[2])
        with tag('td', align = 'center'):
            text(stock[3])
        with tag('td', align = 'center'):
            if result_color[cnt][4] == 1:
                with tag('font', color = '#ff0000'):
                    text(stock[4])
            else:
                text(stock[4])
        with tag('td', align = 'center'):
            text(stock[5])
        with tag('td', align = 'center'):
            if result_color[cnt][6] == 1:
                with tag('font', color = '#ff0000'):
                    text(stock[6])
            else:
                text(stock[6])
        with tag('td', align = 'center'):
            if result_color[cnt][7] == 1:
                with tag('font', color = '#ff0000'):
                    text(stock[7])
            else:
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