import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3
from yattag import Doc

def is_number(num):
  pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
  result = pattern.match(num)
  if result:
    return True
  else:
    return False

dir_temp = os.getcwd()
dir_temp = dir_temp + '/DBs'
os.chdir(dir_temp)
conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

#change path to stock databases
path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)

#the latest date of stock market for P/E ratio
url1 = 'http://www.twse.com.tw/exchangeReport/BWIBBU_d?response=html&date=---yearmonthdate---&selectType=ALL' #P/E ration
url2 = 'https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/pera_result.php?l=zh-tw&o=htm&d=---yearmonthdate---&c=&s=0,asc'
stock_url = 'https://tw.stock.yahoo.com/q/ta?s='

cursor = c.execute("SELECT stock_id, start_date, stock_type, business  from stock_list")
#find the last date in stock database
latest_date = datetime.strptime('1999-12-12', "%Y-%m-%d")
for current_entry in cursor:
    if ((current_entry[2] == '上櫃') or (current_entry[2] == '上市')) and (current_entry[3] != 'ETF'):
        db_name = current_entry[0] + '.db'
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()
        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_day')
        data_ID_str = cursor_stock.fetchone()[0]
        if data_ID_str == None:
            continue
        latest_date_tmp = datetime.strptime(data_ID_str, "%Y-%m-%d")
        if latest_date < latest_date_tmp:
            latest_date = latest_date_tmp
            latest_date_str = data_ID_str
        conn_stock.close()

#transfer date from AC to ROC and fetch the webpage of P/E ratio
date_tmp1 = latest_date_str.replace('-','')
DateSearch = re.compile(r'(\d\d\d\d)-(\d\d)-(\d\d)')
date_tmp = DateSearch.search(latest_date_str)
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


result_stock = []
result_color = []
colors = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business, observation  from stock_list")
for current_entry in cursor:
    if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
        db_name = current_entry[0] + '.db'
        #print(db_name)
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()
        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_day')
        date_ID_str = cursor_stock.fetchone()[0]
        if date_ID_str == None:
            conn_stock.close()
            continue
        #pass if the last data is not the latest
        latest_date_inDB = datetime.strptime(date_ID_str, "%Y-%m-%d")
        if latest_date != latest_date_inDB:
            conn_stock.close()
            continue
        #get the rowid of the last data
        sql_cmd = 'select rowid from stock_day where date_ID =\'' + date_ID_str + '\''
        c_stock.execute(sql_cmd)
        rowid = c_stock.fetchone()
        if rowid == None:
            conn_stock.close()
            continue
        #get volume, highest_price, lowest_price, close_price of the last date
        sql_cmd = 'select volume from stock_day where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        volume_tmp0 = c_stock.fetchone()[0]
        sql_cmd = 'select highest_price from stock_day where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        highest_price_tmp0 = c_stock.fetchone()[0]
        sql_cmd = 'select lowest_price from stock_day where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        lowest_price_tmp0 = c_stock.fetchone()[0]
        sql_cmd = 'select close_price from stock_day where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        close_price_tmp = c_stock.fetchone()[0]
        #check the period
        n = 0
        while 1:
            if (rowid[0] - n - 1) < 1:
                break
            sql_cmd = 'select volume from stock_day where rowid =' + str(rowid[0] - n - 1)
            c_stock.execute(sql_cmd)
            volume_tmp1 = c_stock.fetchone()[0]
            if volume_tmp0 > volume_tmp1:
                n = n +1
            else:
                break
            sql_cmd = 'select highest_price from stock_day where rowid =' + str(rowid[0] - n)
            c_stock.execute(sql_cmd)
            highest_price_tmp1 = c_stock.fetchone()[0]
            if highest_price_tmp1 > highest_price_tmp0:
                highest_price_tmp0 = highest_price_tmp1
            sql_cmd = 'select lowest_price from stock_day where rowid =' + str(rowid[0] - n)
            c_stock.execute(sql_cmd)
            lowest_price_tmp1 = c_stock.fetchone()[0]
            if lowest_price_tmp0 > lowest_price_tmp1:
                lowest_price_tmp0 = lowest_price_tmp1
        volume_period = n
        #add to the list if volume of today is the highest over 30 days
        if n > 29:
            #抓出該股票本益比
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
            #當日成交量
            volume = int(volume_tmp0/1000)
            #抓取股本, 計算周轉率
            sql_cmd = 'select capital_amount from stock_info where rowid in (SELECT max(rowid) FROM stock_info)'
            c_stock.execute(sql_cmd)
            base = c_stock.fetchone()[0]
            if base == None:
                conn_stock.close()
                continue
            turnover_rate = volume_tmp0 / base
            turnover_rate = round(turnover_rate*100, 2)
            #計算股價:最近一季EPS
            c_stock.execute('SELECT EPS FROM stock_quarter where rowid in (SELECT max(rowid) FROM stock_quarter)')
            EPS = c_stock.fetchone()[0]
            if EPS == None:
                EPS = 0
            #stock_quarter的最新一欄
            cursor_stock = c_stock.execute('SELECT max(rowid) FROM stock_quarter')
            rowid = cursor_stock.fetchone()
            if rowid[0] < 4:
                gross_margin_diff0 = 0
                gross_margin_diff1 = 0
                gross_margin_diff2 = 0
                operating_profit_margin_diff0 = 0
                operating_profit_margin_diff1 = 0
                operating_profit_margin_diff2 = 0
            else:
                #計算近三季毛利率變化
                sql_cmd = 'SELECT gross_margin FROM stock_quarter WHERE rowid = ' + str(rowid[0])
                c_stock.execute(sql_cmd)
                gross_margin_tmp0 = c_stock.fetchone()[0]
                sql_cmd = 'SELECT gross_margin FROM stock_quarter WHERE rowid = ' + str(rowid[0] - 1)
                c_stock.execute(sql_cmd)
                gross_margin_tmp1 = c_stock.fetchone()[0]
                sql_cmd = 'SELECT gross_margin FROM stock_quarter WHERE rowid = ' + str(rowid[0] - 2)
                c_stock.execute(sql_cmd)
                gross_margin_tmp2 = c_stock.fetchone()[0]
                sql_cmd = 'SELECT gross_margin FROM stock_quarter WHERE rowid = ' + str(rowid[0] - 3)
                c_stock.execute(sql_cmd)
                gross_margin_tmp3 = c_stock.fetchone()[0]
                if (gross_margin_tmp0 == None) or (gross_margin_tmp1 == None) or (gross_margin_tmp2 == None) or (gross_margin_tmp3 == None):
                    gross_margin_diff0 = 0
                    gross_margin_diff1 = 0
                    gross_margin_diff2 = 0
                else:
                    gross_margin_diff0 = gross_margin_tmp0 - gross_margin_tmp1
                    gross_margin_diff1 = gross_margin_tmp1 - gross_margin_tmp2
                    gross_margin_diff2 = gross_margin_tmp2 - gross_margin_tmp3
                    gross_margin_diff0 = round(gross_margin_diff0, 2)
                    gross_margin_diff1 = round(gross_margin_diff1, 2)
                    gross_margin_diff2 = round(gross_margin_diff2, 2)
                #計算近三季營益率變化
                sql_cmd = 'SELECT operating_profit_margin FROM stock_quarter WHERE rowid = ' + str(rowid[0])
                c_stock.execute(sql_cmd)
                operating_profit_margin_tmp0 = c_stock.fetchone()[0]
                sql_cmd = 'SELECT operating_profit_margin FROM stock_quarter WHERE rowid = ' + str(rowid[0] - 1)
                c_stock.execute(sql_cmd)
                operating_profit_margin_tmp1 = c_stock.fetchone()[0]
                sql_cmd = 'SELECT operating_profit_margin FROM stock_quarter WHERE rowid = ' + str(rowid[0] - 2)
                c_stock.execute(sql_cmd)
                operating_profit_margin_tmp2 = c_stock.fetchone()[0]
                sql_cmd = 'SELECT operating_profit_margin FROM stock_quarter WHERE rowid = ' + str(rowid[0] - 3)
                c_stock.execute(sql_cmd)
                operating_profit_margin_tmp3 = c_stock.fetchone()[0]
                if (operating_profit_margin_tmp0 == None) or (operating_profit_margin_tmp1 == None) or (operating_profit_margin_tmp2 == None) or (operating_profit_margin_tmp3 == None):
                    operating_profit_margin_diff0 = 0
                    operating_profit_margin_diff1 = 0
                    operating_profit_margin_diff2 = 0
                else:
                    operating_profit_margin_diff0 = operating_profit_margin_tmp0 - operating_profit_margin_tmp1
                    operating_profit_margin_diff1 = operating_profit_margin_tmp1 - operating_profit_margin_tmp2
                    operating_profit_margin_diff2 = operating_profit_margin_tmp2 - operating_profit_margin_tmp3
                    operating_profit_margin_diff0 = round(operating_profit_margin_diff0, 2)
                    operating_profit_margin_diff1 = round(operating_profit_margin_diff1, 2)
                    operating_profit_margin_diff2 = round(operating_profit_margin_diff2, 2)
            #計算最近一年以及最近一個季度的月平均營收
            #最近一個月營收
            sql_cmd = 'select revenue from stock_month where rowid in (SELECT max(rowid) FROM stock_month)'
            c_stock.execute(sql_cmd)
            revenue_latest = c_stock.fetchone()[0]
            #最近一個財務季度最後一個月
            c_stock.execute('SELECT date_ID FROM stock_quarter where rowid in (SELECT max(rowid) FROM stock_quarter)')
            date_ID_tmp = c_stock.fetchone()[0]
            date_quarter = datetime.strptime(date_ID_tmp, "%Y-%m")
            date_quarter = date_quarter.replace(month = ((date_quarter.month - 1)*3 + 1))
            date_ID_tmp = str(date_quarter.year) + '-' + str(date_quarter.month + 2).zfill(2)
            #print(date_ID_tmp)
            sql_cmd = 'select rowid from stock_month where date_ID =\'' + date_ID_tmp + '\''
            c_stock.execute(sql_cmd)
            rowid = c_stock.fetchone()
            n = 0
            revenue_total = 0
            #最近一季營收月平均
            while 1:
                sql_cmd = 'select revenue from stock_month where rowid =' + str(rowid[0] - n)
                if (rowid[0] - n) > 0:
                    c_stock.execute(sql_cmd)
                    revenue_tmp = c_stock.fetchone()[0]
                else:
                    revenue_tmp = revenue_total / (n + 1)
                revenue_total = revenue_total + revenue_tmp
                n = n + 1
                if n == 3:
                    break
            revenue_quarter = revenue_total/3
            #print(revenue_quarter)
            n = 0
            revenue_total = 0
            #最近一年營收月平均
            while 1:
                sql_cmd = 'select revenue from stock_month where rowid =' + str(rowid[0] - n)
                if (rowid[0] - n) > 0:
                    c_stock.execute(sql_cmd)
                    revenue_tmp = c_stock.fetchone()[0]
                else:
                    revenue_tmp = revenue_total / (n + 1)
                revenue_total = revenue_total + revenue_tmp
                n = n + 1
                if n == 12:
                    break
            revenue_year = revenue_total/12
            #print(revenue_year)
            if float(revenue_quarter) == 0:
                quarter_growth = 10
            else:
                quarter_growth = float(revenue_latest)/float(revenue_quarter) - 1
            if float(revenue_year) == 0:
                year_growth = 10
            else:
                year_growth = float(revenue_latest)/float(revenue_year) - 1
            quarter_growth = round(quarter_growth*100, 2)
            year_growth = round(year_growth*100, 2)
            #毛利率
            sql_cmd = 'select gross_margin from stock_quarter where rowid in (SELECT max(rowid) FROM stock_quarter)'
            c_stock.execute(sql_cmd)
            gross_margin_latest = c_stock.fetchone()[0]
            if gross_margin_latest == None:
                gross_margin_latest = 'N/A'
            #外本比買超計算
            sql_cmd = 'select capital_amount from stock_info where rowid in (SELECT max(rowid) FROM stock_info)'
            c_stock.execute(sql_cmd)
            base = c_stock.fetchone()[0]
            #print(base)
            if base == None:
                conn_stock.close()
                continue
            #stock_day 最大row_id
            sql_cmd = 'select max(rowid) from stock_day'
            c_stock.execute(sql_cmd)
            rowid = c_stock.fetchone()
            if rowid == None:
                conn_stock.close()
                continue
            #1日外本比買超
            foreign_total_1day = 0
            invest_trust_total_1day = 0
            for n in range(0, 1):
                sql_cmd = 'select foreign_total from stock_day where rowid =' + str(rowid[0] - n)
                c_stock.execute(sql_cmd)
                foreign_total_tmp = c_stock.fetchone()[0]
                if foreign_total_tmp == None:
                    break
                foreign_total_1day += foreign_total_tmp
                #print(foreign_total_tmp)
                sql_cmd = 'select invest_trust_total from stock_day where rowid =' + str(rowid[0] - n)
                c_stock.execute(sql_cmd)
                invest_trust_total_tmp = c_stock.fetchone()[0]
                if invest_trust_total_tmp == None:
                    break
                invest_trust_total_1day += invest_trust_total_tmp
            total_ratio_1day = (foreign_total_1day + invest_trust_total_1day)/base
            total_ratio_1day = round(total_ratio_1day*100, 2)
            #5日外本比買超
            foreign_total_5day = 0
            invest_trust_total_5day = 0
            for n in range(0, 5):
                sql_cmd = 'select foreign_total from stock_day where rowid =' + str(rowid[0] - n)
                c_stock.execute(sql_cmd)
                foreign_total_tmp = c_stock.fetchone()[0]
                if foreign_total_tmp == None:
                    break
                foreign_total_5day += foreign_total_tmp
                #print(foreign_total_tmp)
                sql_cmd = 'select invest_trust_total from stock_day where rowid =' + str(rowid[0] - n)
                c_stock.execute(sql_cmd)
                invest_trust_total_tmp = c_stock.fetchone()[0]
                if invest_trust_total_tmp == None:
                    break
                invest_trust_total_5day += invest_trust_total_tmp
            total_ratio_5day = (foreign_total_5day + invest_trust_total_5day)/base
            total_ratio_5day = round(total_ratio_5day*100, 2)
            #20日外本比買超
            foreign_total_20day = 0
            invest_trust_total_20day = 0
            for n in range(0, 20):
                sql_cmd = 'select foreign_total from stock_day where rowid =' + str(rowid[0] - n)
                c_stock.execute(sql_cmd)
                foreign_total_tmp = c_stock.fetchone()[0]
                if foreign_total_tmp == None:
                    break
                foreign_total_20day += foreign_total_tmp
                #print(foreign_total_tmp)
                sql_cmd = 'select invest_trust_total from stock_day where rowid =' + str(rowid[0] - n)
                c_stock.execute(sql_cmd)
                invest_trust_total_tmp = c_stock.fetchone()[0]
                if invest_trust_total_tmp == None:
                    break
                invest_trust_total_20day += invest_trust_total_tmp
            total_ratio_20day = (foreign_total_20day + invest_trust_total_20day)/base
            total_ratio_20day = round(total_ratio_20day*100, 2)
            #400張以上大戶比例
            cursor_stock = c_stock.execute('SELECT max(rowid) FROM stock_week')
            rowid = cursor_stock.fetchone()
            if rowid == None:
                conn_stock.close()
                continue
            #400張以上大戶比例一周變化
            n = 1
            if (rowid[0] - n) <= 0:
                conn_stock.close()
                continue
            sql_cmd = 'select holder400_per from stock_week where rowid =' + str(rowid[0])
            c_stock.execute(sql_cmd)
            holder400_per_tmp = c_stock.fetchone()[0]
            sql_cmd = 'select holder400_per from stock_week where rowid =' + str(rowid[0] - n)
            c_stock.execute(sql_cmd)
            holder400_per_tmp_before = c_stock.fetchone()[0]
            increase_ratio_1week = holder400_per_tmp - holder400_per_tmp_before
            increase_ratio_1week = round(increase_ratio_1week, 2)
            #400張以上大戶比例一周變化
            n = 4
            if (rowid[0] - n) <= 0:
                conn_stock.close()
                continue
            sql_cmd = 'select holder400_per from stock_week where rowid =' + str(rowid[0])
            c_stock.execute(sql_cmd)
            holder400_per_tmp = c_stock.fetchone()[0]
            sql_cmd = 'select holder400_per from stock_week where rowid =' + str(rowid[0] - n)
            c_stock.execute(sql_cmd)
            holder400_per_tmp_before = c_stock.fetchone()[0]
            increase_ratio_4week = holder400_per_tmp - holder400_per_tmp_before
            increase_ratio_4week = round(increase_ratio_4week, 2)
            #是否在觀察名單上 1:做多名單 2:做空名單
            mark_type = current_entry[5]
            result_stock.append([current_entry[0], current_entry[1], str(volume_period+1), str(highest_price_tmp0), str(lowest_price_tmp0), str(close_price_tmp), PER, EPS, quarter_growth\
                , year_growth, gross_margin_latest, total_ratio_1day, total_ratio_5day, volume, turnover_rate, total_ratio_20day, increase_ratio_1week, increase_ratio_4week\
                , gross_margin_diff0, gross_margin_diff1, gross_margin_diff2, operating_profit_margin_diff0, operating_profit_margin_diff1, operating_profit_margin_diff2, mark_type])
        conn_stock.close()
conn.close()

print(len(result_stock))
#sorting by the period of the days
for i in range(0, len(result_stock) - 1):
    j = i + 1
    largest = int(result_stock[i][2])
    k = i
    for j in range(i+1, len(result_stock)):
        #print(result_stock_tmp[j][0])
        if largest < int(result_stock[j][2]):
            largest = int(result_stock[j][2])
            k = j
    tmp = result_stock[i]
    result_stock[i] = result_stock[k]
    result_stock[k] = tmp

#colored each item in the list by the length of the period
for entry in result_stock:
    for i in range(0,30):
        colors[i] = 0
    if int(entry[2]) > 53:
        colors[2] = 1
    if int(entry[2]) > 107:
        colors[2] = 2
    if int(entry[2]) > 215:
        colors[2] = 3
    if is_number(entry[6]):
        if float(entry[6]) < 25:
            colors[6] = 2
        if float(entry[6]) < 15:
            colors[6] = 3
    if float(entry[11]) > 0.3:
        colors[11] = 1
    if float(entry[12]) > 1:
        colors[12] = 1
    if float(entry[15]) > 1.5:
        colors[15] = 1  
    result_color.append([colors[0], colors[1], colors[2], colors[3], colors[4], colors[5], colors[6], colors[7], colors[8], colors[9], colors[10], colors[11]\
        , colors[12], colors[13], colors[14], colors[15], colors[16], colors[17], colors[18], colors[19], colors[20], colors[21], colors[22], colors[23], colors[24]\
        , colors[25], colors[26], colors[27], colors[28], colors[29]])
print(os.getcwd())
os.chdir('..')
print(os.getcwd())
os.chdir('..')
dir_temp = os.getcwd()
dir_temp = dir_temp + '/temp_pages'
os.chdir(dir_temp)
print(os.getcwd())

filename = 'stock_volume.html'
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
            text(date_ID_str)

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
        text('成交量\周轉率')
    with tag('td', align = 'center'):
        text('日數新高')
    with tag('td', align = 'center'):
        text('期間')
        doc.asis('<br>')
        text('最高價')
    with tag('td', align = 'center'):
        text('期間')
        doc.asis('<br>')
        text('最低價')
    with tag('td', align = 'center'):
        text('收盤價')
    with tag('td', align = 'center'):
        text('本益比')
    with tag('td', align = 'center'):
        text('近一季')
        doc.asis('<br>')
        text('EPS')
    with tag('td', align = 'center'):
        text('最近月營收:')
        doc.asis('<br>')
        text('最近季度平均營收')
        doc.asis('<br>')
        text('最近年度平均營收')
    with tag('td', align = 'center'):
        text('毛利率')
    with tag('td', align = 'center'):
        text('近三季毛利率變化')
    with tag('td', align = 'center'):
        text('近三季營益率變化')
    with tag('td', align = 'center'):
        text('外投本比買超:')
        doc.asis('<br>')
        text('1日 / 5日 / 20日')
    with tag('td', align = 'center'):
        text('400張以上')
        doc.asis('<br>')
        text('大戶持股變化:')
        doc.asis('<br>')
        text('1周 / 4周 ')
    with tag('td', align = 'center'):
        text('觀察中')
cnt = 0
for stock in result_stock:
    with tag('tr'):
        with tag('td', align = 'center'):
            with tag('a', href = stock_url + stock[0], target='_blank'):
                text(stock[0])
        with tag('td', align = 'center'):
            text(stock[1])
        with tag('td', align = 'center'):
            text(str(stock[13]) + ' \ ' + str(stock[14]) + '%')
        with tag('td', align = 'center'):
            if result_color[cnt][2] == 1:
                with tag('font', color = '#0000e3'):
                    text(stock[2])
            elif result_color[cnt][2] == 2:
                with tag('font', color = '#009100'):
                    text(stock[2])
            elif result_color[cnt][2] == 3:
                with tag('font', color = '#FF0000'):
                    text(stock[2])
            else:
                text(stock[2])
        with tag('td', align = 'center'):
            text(stock[3])
        with tag('td', align = 'center'):
            text(stock[4])
        with tag('td', align = 'center'):
            text(stock[5])
        with tag('td', align = 'center'):
            if result_color[cnt][6] == 2:
                with tag('font', color = '#009100'):
                    text(stock[6])
            elif result_color[cnt][6] == 3:
                with tag('font', color = '#FF0000'):
                    text(stock[6])
            else:
                text(stock[6])
        with tag('td', align = 'center'):
            text(stock[7])
        with tag('td', align = 'center'):
            text(str(stock[8])+ '%')
            doc.asis(' / ')
            text(str(stock[9])+ '%')
        with tag('td', align = 'center'):
            text(str(stock[10]) + '%')
        with tag('td', align = 'center'):
            text(str(stock[18]) + '%')
            doc.asis(' / ')
            text(str(stock[19]) + '%')
            doc.asis(' / ')
            text(str(stock[20]) + '%')
        with tag('td', align = 'center'):
            text(str(stock[21]) + '%')
            doc.asis(' / ')
            text(str(stock[22]) + '%')
            doc.asis(' / ')
            text(str(stock[23]) + '%')
        with tag('td', align = 'center'):
            if result_color[cnt][11] == 1:
                with tag('font', color = '#FF0000'):
                    text(str(stock[11]) + '%')
            else:
                text(str(stock[11]) + '%')
            doc.asis(' / ')
            if result_color[cnt][12] == 1:
                with tag('font', color = '#FF0000'):
                    text(str(stock[12]) + '%')
            else:
                text(str(stock[12]) + '%')
            doc.asis(' / ')
            if result_color[cnt][15] == 1:
                with tag('font', color = '#FF0000'):
                    text(str(stock[15]) + '%')
            else:
                text(str(stock[15]) + '%')
        with tag('td', align = 'center'):
            text(str(stock[16]) + '%')
            doc.asis(' / ')
            text(str(stock[17]) + '%')
        with tag('td', align = 'center'):
            if str(stock[24]) == '1':
                text('↑')
            elif str(stock[24]) == '2':
                text('↓')
            else:
                text(' ')
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