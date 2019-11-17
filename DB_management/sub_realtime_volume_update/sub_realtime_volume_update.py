import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3
from yattag import Doc
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

def is_number(num):
  #pattern = re.compile(r'^/d{4}$')
  #result = pattern.match(num)
  if len(num) == 4:
    return True
  else:
    return False

def is_number2(num):
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

#https://histock.tw/twstock

url_tse_array = ['01-水泥工業', '02-食品工業', '03-塑膠工業', '04-紡織纖維', '05-電機機械', '06-電器電纜', '08-玻璃陶瓷', '09-造紙工業', '10-鋼鐵工業', '11-橡膠工業', '12-汽車工業', '14-建材營造',\
                   '15-航運業', '16-觀光事業', '17-金融保險', '18-貿易百貨', '20-其他', '21-化學工業', '22-生技醫療業', '23-油電燃氣業', '24-半導體業', '25-電腦及週邊設備業', '26-光電業',\
                   '27-通信網路業', '28-電子零組件業', '29-電子通路業', '30-資訊服務業', '31-其他電子業', 'Q0-海外第一上市']

url_otc_array = ['02-食品工業', '03-塑膠工業', '04-紡織纖維', '05-電機機械', '06-電器電纜', '10-鋼鐵工業', '11-橡膠工業', '14-建材營造',\
                   '15-航運業', '16-觀光事業', '17-金融業', '18-貿易百貨', '20-其他', '21-化學工業', '22-生技醫療', '23-油電燃氣業', '24-半導體業', '25-電腦及週邊設備業', '26-光電業',\
                   '27-通信網路業', '28-電子零組件業', '29-電子通路業', '30-資訊服務業', '31-其他電子業', '32-文化創意業', '33-農業科技業', '34-電子商務', 'Q0-海外第一上櫃']

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

conn.close()

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
soup2 = bs4.BeautifulSoup(res1.text, "lxml")
print('Cool down for requesting web content')
time.sleep(5)
res2 = requests.get(url2)
soup3 = bs4.BeautifulSoup(res2.text, "lxml")

# 创建chrome启动选项
chrome_options = webdriver.ChromeOptions()
# 指定chrome启动类型为headless 并且禁用gpu
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_path = "C:\chromedriver\chromedriver.exe"
# 如果没有在环境变量指定Chrome位置
web = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_path)
#web = webdriver.Chrome(chrome_path)
web.get('https://mis.twse.com.tw/stock/group.jsp?ex=tse&type=all&ind=01&lang=zh_tw')
time.sleep(10)
s1 = Select(web.find_element_by_id('prePage'))
s1.select_by_value('3')
s1 = Select(web.find_element_by_id('tseSelect'))

stock_list_all = []
result_stock = []
result_color = []
colors = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
n = 0
for item in url_tse_array:
    s1 = Select(web.find_element_by_id('tseSelect'))
    s1.select_by_value(item)
    time.sleep(3)
    soup = bs4.BeautifulSoup(web.page_source, 'lxml')
    stock_items = soup.find_all('a', class_="linkTip")

    for stock in stock_items:
        n = n + 1
        if is_number(stock.getText()) == False:
            continue
        soup1 = bs4.BeautifulSoup(str(stock.parent.parent), "lxml")
        titles = soup1.find_all('a')
        print(titles[0].getText())
        tds = soup1.find_all('td')
        stock_list_all.append([titles[0].getText(), titles[1].getText(), tds[1].getText(), tds[2].getText(),\
                               tds[4].getText().replace(',',''), tds[14].getText().replace(',',''), 'tse'])


for item in url_otc_array:
    s1 = Select(web.find_element_by_id('otcSelect'))
    s1.select_by_value(item)
    time.sleep(3)
    soup = bs4.BeautifulSoup(web.page_source, 'lxml')
    stock_items = soup.find_all('a', class_="linkTip")

    for stock in stock_items:
        n = n + 1
        if is_number(stock.getText()) == False:
            continue
        soup1 = bs4.BeautifulSoup(str(stock.parent.parent), "lxml")
        titles = soup1.find_all('a')
        print(titles[0].getText())
        tds = soup1.find_all('td')
        stock_list_all.append([titles[0].getText(), titles[1].getText(), tds[1].getText(), tds[2].getText(),\
                               tds[4].getText().replace(',',''), tds[14].getText().replace(',',''), 'otc'])

web.close()

for stock in stock_list_all:
    db_name = stock[0] + '.db'
    conn_stock = sqlite3.connect(db_name)
    c_stock = conn_stock.cursor()
    cursor_stock = c_stock.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='stock_day'")
    if cursor_stock.fetchone()[0] != 1:
        conn_stock.close()
        continue
    #print(db_name)
    cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_day')
    date_ID_str = cursor_stock.fetchone()[0]
    if date_ID_str == None:
        conn_stock.close()
        continue
    #get the rowid of the last data
    sql_cmd = 'select rowid from stock_day where date_ID =\'' + date_ID_str + '\''
    c_stock.execute(sql_cmd)
    rowid = c_stock.fetchone()
    if rowid == None:
        conn_stock.close()
        continue
    if is_number2(stock[4]) == False:
        conn_stock.close()
        continue
    volume_tmp0 = int(stock[4])

    #predict volume
    time_open = datetime.strptime("09:00", "%H:%M")
    time_now = datetime.now()
    time_open = time_open.replace(year = time_now.year, month = time_now.month, day = time_now.day)
    time_delta = time_now - time_open
    current_minute = time_delta.total_seconds()/60
    if (current_minute > 0) and (current_minute < 270):
        volume_predict = int(volume_tmp0*(270/current_minute))
    else:
        volume_predict = volume_tmp0

    #check the period
    n = 0
    m = 0
    while 1:
        if (rowid[0] - n) < 1:
            break
        sql_cmd = 'select volume from stock_day where rowid =' + str(rowid[0] - n)
        c_stock.execute(sql_cmd)
        volume_tmp1 = c_stock.fetchone()[0]
        volume_tmp1 = int(volume_tmp1 / 1000)
        if volume_tmp0 >= volume_tmp1:
            n = n + 1
        else:
            break
    while 1:
        if (rowid[0] - m) < 1:
            break
        sql_cmd = 'select volume from stock_day where rowid =' + str(rowid[0] - m)
        c_stock.execute(sql_cmd)
        volume_tmp1 = c_stock.fetchone()[0]
        volume_tmp1 = int(volume_tmp1 / 1000)
        if volume_predict >= volume_tmp1:
            m = m + 1
        else:
            break
    volume_period = n
    #add to the list if volume of today is the highest over 30 days
    if (volume_period > 55) or (m > 107):
        #抓出該股票本益比
        if stock[6] == 'tse':
            td = soup2.find(string=str(stock[0]))
            if td == None:
                conn_stock.close()
                continue
            soup_temp = bs4.BeautifulSoup(str(td.parent.parent), "lxml")
            tds = soup_temp.find_all('td')
            PER = tds[4].getText().strip()
            PBR = tds[5].getText().strip()
        elif stock[6] == 'otc':
            td = soup3.find(string=str(stock[0]))
            if td == None:
                conn_stock.close()
                continue
            soup_temp = bs4.BeautifulSoup(str(td.parent.parent), "lxml")
            tds = soup_temp.find_all('td')
            PER = tds[2].getText().strip()
            PBR = tds[6].getText().strip()
        #毛利率
        cursor_stock = c_stock.execute('SELECT max(rowid) FROM stock_quarter')
        rowid = cursor_stock.fetchone()
        sql_cmd = 'select gross_margin from stock_quarter where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        gross_margin = c_stock.fetchone()[0]
        #抓取股本, 計算周轉率, 預估周轉率
        sql_cmd = 'select capital_amount from stock_info where rowid in (SELECT max(rowid) FROM stock_info)'
        c_stock.execute(sql_cmd)
        base = c_stock.fetchone()[0]
        if base == None:
            conn_stock.close()
            continue
        turnover_rate = volume_tmp0*1000 / base
        turnover_rate = round(turnover_rate*100, 2)
        turnover_rate_predict = volume_predict*1000 / base
        turnover_rate_predict = round(turnover_rate_predict*100, 2)
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
        result_stock.append([stock[0],stock[1],volume_period,stock[2],stock[3],stock[4], volume_predict, m, stock[5], PER, quarter_growth, year_growth, turnover_rate, \
            turnover_rate_predict, gross_margin, total_ratio_1day, total_ratio_5day, total_ratio_20day])
    conn_stock.close()

for result in result_stock:
    print(result[0] + ' ' + result[1] + ' ' + str(result[2]))

print('\n')
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

for result in result_stock:
    print(result[0] + ' ' + result[1] + ' ' + str(result[2]))
    #print(result[4][0])

for result in result_stock:
    for i in range(0,16):
        colors[i] = 0
    if result[4][0] == '▲':
        colors[4] = 1
    elif result[4][0] == '▼':
        colors[4] = 2
    result_color.append([colors[0], colors[1], colors[2], colors[3], colors[4], colors[5], colors[6], colors[7], colors[8], colors[9], colors[10], colors[11]\
        , colors[12], colors[13], colors[14]])
print(os.getcwd())
os.chdir('..')
print(os.getcwd())
os.chdir('..')
dir_temp = os.getcwd()
dir_temp = dir_temp + '/temp_pages'
os.chdir(dir_temp)
print(os.getcwd())

filename = 'stock_volume_realtime.html'
f= open(filename,"w+", encoding="utf-8")
doc, tag, text = Doc().tagtext()

#beginning of the html page
temp_html_content = """
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>亮晶晶乾洗店_盤中即時更新</title>
</head>
<body>
"""
f.write(temp_html_content)

with tag('table', border = '0'):
    with tag('tr'):
        with tag('td', align = 'center'):
            text('最後資料更新')
        with tag('td', align = 'center'):
            text(str(datetime.today()))

doc.asis('<br>')
f.write(doc.getvalue())
doc, tag, text = Doc().tagtext()
f.write('<table border=1>')
with tag('tr'):
    with tag('td', align = 'center'):
        text('代碼')
    with tag('td', align = 'center'):
        text('公司')
    #with tag('td', align = 'center'):
    #    text('日數新高')
    with tag('td', align = 'center'):
        text('成交量\周轉率')
    with tag('td', align = 'center'):
        text('預估')
        doc.asis('<br>')
        text('日數新高')
    with tag('td', align = 'center'):
        text('成交價')
    with tag('td', align = 'center'):
        text('漲跌(漲跌幅)')
    #with tag('td', align = 'center'):
    #    text('預估')
    #    doc.asis('<br>')
    #    text('成交量\周轉率')
    with tag('td', align = 'center'):
        text('時間')
    with tag('td', align = 'center'):
        text('本益比')
    with tag('td', align = 'center'):
        text('毛利率')
    with tag('td', align = 'center'):
        text('最近月營收:')
        doc.asis('<br>')
        text('最近季度平均營收')
        doc.asis('<br>')
        text('最近年度平均營收')
    with tag('td', align = 'center'):
        text('外投本比買超:')
        doc.asis('<br>')
        text('1日 / 5日 / 20日')

cnt = 0
for stock in result_stock:
    with tag('tr'):
        with tag('td', align = 'center'):
            with tag('a', href = stock_url + stock[0], target='_blank'):
                text(stock[0])
        with tag('td', align = 'center'):
            text(stock[1])
        #with tag('td', align = 'center'):
        #    text(str(stock[2]))
        with tag('td', align = 'center'):
            text(str(stock[5]) + ' \ ' + str(stock[12]) + '%')
        with tag('td', align = 'center'):
            text(stock[7])
        with tag('td', align = 'center'):
            text(stock[3])
        with tag('td', align = 'center'):
            if result_color[cnt][4] == 1:
                with tag('font', color = '#FF0000'):
                    text(stock[4])
            elif result_color[cnt][4] == 2:
                with tag('font', color = '#00A600'):
                    text(stock[4])
            else:
                with tag('font', color = '#000000'):
                    text(stock[4])
        #with tag('td', align = 'center'):
        #    text(str(stock[6]) + ' \ ' + str(stock[13]) + '%')
        with tag('td', align = 'center'):
            text(stock[8])
        with tag('td', align = 'center'):
            text(stock[9])
        with tag('td', align = 'center'):
            text(str(stock[14]))
        with tag('td', align = 'center'):
            text(str(stock[10]) + '%')
            doc.asis(' / ')
            text(str(stock[11]) + '%')
        with tag('td', align = 'center'):
            text(str(stock[15]) + '%')
            doc.asis(' / ')
            text(str(stock[16]) + '%')
            doc.asis(' / ')
            text(str(stock[17]) + '%')
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