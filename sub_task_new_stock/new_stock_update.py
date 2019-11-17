import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3

from yattag import Doc

dir_temp = os.getcwd()
dir_temp = dir_temp + '/temp_pages'
os.chdir(dir_temp)

filename = 'new_stock.html'
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

#抽籤日期
f.write('<table border=1>')
url1_base = 'https://histock.tw/stock/public.aspx'
res = requests.get(url1_base)
soup = bs4.BeautifulSoup(res.text, "lxml")
td = soup.find(string='抽籤日期')
#print(td.parent.parent)
f.write(str(td.parent.parent))
tds = soup.find_all(string='申購中')
for td in tds:
    #print(td.parent.parent.parent.parent)
    f.write(str(td.parent.parent.parent.parent))
f.write('</table>')

#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()