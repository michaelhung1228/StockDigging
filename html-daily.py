import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3

from yattag import Doc

dir_temp = os.getcwd()
dir_temp = dir_temp + '/daily_page'
os.chdir(dir_temp)

doc, tag, text = Doc().tagtext()

today_date = datetime.today()
filename = today_date.strftime("%Y%m%d") + '.html'
f= open(filename,"w+", encoding="utf-8")

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

#title table
with tag('table', border = '0'):
    with tag('tr'):
        with tag('td', align = 'center'):
            text('歡迎光臨亮晶晶乾洗店')

with tag('table', border = '0'):
    with tag('tr'):
        with tag('td', align = 'center'):
            text('最後更新時間')
        with tag('td', align = 'center'):
            text(str(datetime.today()))

doc.asis('<br>')
f.write(doc.getvalue())

#當日成交量創近日新高個股
f.write('<font><b>當日成交量創近日新高個股: </b></font><font color="#0000e3"><b>54日新高 </b></font><font color="#009100"><b>108日新高 </b></font><font color="#FF0000"><b>216日新高 </b></font><br>')
temp_page = open('../temp_pages/stock_volume.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()

f.write('<br>')

#外資投信買超佔股本比前20名
f.write('<table border="0"><tr><td align="center">')

f.write('<font><b>今日外資投信買超佔股本比前20名 </b></font><br>')
temp_page = open('../temp_pages/stock_buy_1day.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()
f.write('</td>')
#外資投信買超佔股本比前20名
f.write('<td align="center">')

f.write('<font><b>近五日外資投信買超佔股本比前20名 </b></font><br>')
temp_page = open('../temp_pages/stock_buy_5day.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()

f.write('</td>')
#外資投信買超佔股本比前20名
f.write('<td align="center">')

f.write('<font><b>近二十日外資投信買超佔股本比前20名 </b></font><br>')
temp_page = open('../temp_pages/stock_buy_20day.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()
f.write('</td>')
#外資投信賣超佔股本比前20名
f.write('<td align="center">')
f.write('<font><b>今日外資投信賣超佔股本比前20名 </b></font><br>')
temp_page = open('../temp_pages/stock_sell_1day.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()

f.write('</td>')
#外資投信買超佔股本比前20名
f.write('<td align="center">')
f.write('<font><b>近五日外資投信賣超佔股本比前20名 </b></font><br>')
temp_page = open('../temp_pages/stock_sell_5day.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()

f.write('</td>')
#外資投信買超佔股本比前20名
f.write('<td align="center">')

f.write('<font><b>近二十日外資投信賣超佔股本比前20名 </b></font><br>')
temp_page = open('../temp_pages/stock_sell_20day.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()

f.write('</td></tr></table>')
f.write('<br>')

#doc, tag, text = Doc().tagtext()
#抽籤日期
f.write('<font><b>股市抽籤提醒</b></font><br>')
temp_page = open('../temp_pages/new_stock.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()

f.write('<br>')

#400張以上大戶籌碼集中度增加佔股本比前20名
f.write('<table border="0"><tr><td align="center">')

f.write('<font><b>一周間400張以上大戶籌碼')
f.write('<br>')
f.write('集中度增加佔股本比前20名 </b></font><br>')
temp_page = open('../temp_pages/stock_holder_ratio_increase_1week.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()
f.write('</td>')
#400張以上大戶籌碼集中度增加佔股本比前20名
f.write('<td align="center">')
f.write('<font><b>四周間400張以上大戶籌碼')
f.write('<br>')
f.write('集中度增加佔股本比前20名 </b></font><br>')
temp_page = open('../temp_pages/stock_holder_ratio_increase_4week.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()
f.write('</td>')
#400張以上大戶籌碼集中度減少佔股本比前20名
f.write('<td align="center">')
f.write('<font><b>一周間400張以上大戶籌碼')
f.write('<br>')
f.write('集中度減少佔股本比前20名 </b></font><br>')
temp_page = open('../temp_pages/stock_holder_ratio_decrease_1week.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()
f.write('</td>')
#400張以上大戶籌碼集中度減少佔股本比前20名
f.write('<td align="center">')
f.write('<font><b>四周間400張以上大戶籌碼')
f.write('<br>')
f.write('集中度減少佔股本比前20名 </b></font><br>')
temp_page = open('../temp_pages/stock_holder_ratio_decrease_4week.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()
f.write('</td></tr></table>')

#營收創兩年來新高個股
f.write('<font><b>營收創兩年來新高個股</b></font><font color="#ffaf60"><b>建材營造業或生技醫療業</b></font><br>')
f.write('<font color="#ff0000"><b>本益比小於15倍</b></font><br>')
f.write('<font color="#ff0000"><b>年增率大於15%</b></font><br>')
f.write('<font color="#ff0000"><b>月增率大於30%</b></font><br>')
temp_page = open('../temp_pages/stock_revenue.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()

f.write('<br>')

#EPS創兩年來新高個股
f.write('<font><b>EPS創兩年來新高個股</b></font><br>')
temp_page = open('../temp_pages/stock_eps.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()

f.write('<br>')

#三率創兩年來新高個股
f.write('<font><b>三率創兩年來新高個股</b></font><br>')
temp_page = open('../temp_pages/stock_gross_margin.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()

f.write('<br>')

#今日上榜多次個股 
today_list = []
temp_page = open('../temp_pages/stock_revenue.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
temp_page.close()
tds = soup.find_all('td')
DateSearch = re.compile(r'(^\d\d\d\d$)')
for td in tds:
    tmp = td.getText().strip()
    result = DateSearch.search(tmp)
    if result != None:
        today_list.append(result.group(1))

temp_page = open('../temp_pages/stock_volume.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
temp_page.close()
tds = soup.find_all('td')
for td in tds:
    tmp = td.getText().strip()
    result = DateSearch.search(tmp)
    if result != None:
        today_list.append(result.group(1))

temp_page = open('../temp_pages/stock_eps.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
temp_page.close()
tds = soup.find_all('td')
for td in tds:
    tmp = td.getText().strip()
    result = DateSearch.search(tmp)
    if result != None:
        today_list.append(result.group(1))

temp_page = open('../temp_pages/stock_buy_1day.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
temp_page.close()
tds = soup.find_all('td')
for td in tds:
    tmp = td.getText().strip()
    result = DateSearch.search(tmp)
    if result != None:
        today_list.append(result.group(1))

today_list_result = []
while len(today_list) != 0:
    tmp = today_list[0]
    n = 0
    for entry in today_list:
        if tmp == entry:
            n = n + 1
            today_list.remove(tmp)
    if n > 1:
        today_list_result.append([tmp, n])
f.write('<font><b>今日上榜多次個股</b></font><br>')
doc, tag, text = Doc().tagtext()
f.write('<table border=1>')
with tag('tr'):
    with tag('td', align = 'center'):
        text('代碼')
    with tag('td', align = 'center'):
        text('上榜次數')
for entry_tmp in today_list_result:
    with tag('tr'):
        with tag('td', align = 'center'):
            text(entry_tmp[0])
        with tag('td', align = 'center'):
            text(entry_tmp[1])
f.write(doc.getvalue())
f.write('</table>')

f.write('<br>')
#電影發行日期
f.write('<font><b>本月勁片</b></font><br>')
temp_page = open('../temp_pages/new_movie.html',"r", encoding="utf-8")
page_content = temp_page.read()
soup = bs4.BeautifulSoup(page_content, "lxml")
tables = soup.find_all('table')
for table in tables:
    f.write(str(table))
temp_page.close()

#print link to yesterday and tomorrow
delta_1day = timedelta(days = 1) #delta_1day
yesterday_date = today_date - delta_1day
tomorrow_date = today_date + delta_1day
doc, tag, text = Doc().tagtext()

doc.asis('<br>')
filename_tmp = '<a href="' + yesterday_date.strftime("%Y%m%d") + '.html' + '">前一天的資料</a>'
doc.asis(filename_tmp)
doc.asis('<br>')
filename_tmp = '<a href="' + tomorrow_date.strftime("%Y%m%d") + '.html' + '">後一天的資料</a>'
doc.asis(filename_tmp)
f.write(doc.getvalue())

#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()

command = 'copy ' + filename + ' today.html'
os.system(command)

#print temporary file for not happened tomorrow
filename = tomorrow_date.strftime("%Y%m%d") + '.html'
f= open(filename,"w+", encoding="utf-8")
temp_html_content = """
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>亮晶晶乾洗店</title>
</head>
"""
f.write(temp_html_content)
doc, tag, text = Doc().tagtext()
with tag('table', border = '0'):
    with tag('tr'):
        with tag('td', align = 'center'):
            text('啊明天就還沒到啊')
filename_tmp = '<a href="' + today_date.strftime("%Y%m%d") + '.html' + '">回到今天</a>'
doc.asis(filename_tmp)
f.write(doc.getvalue())

temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()