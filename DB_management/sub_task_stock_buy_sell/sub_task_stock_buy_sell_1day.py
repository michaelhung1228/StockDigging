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

stock_url = 'https://tw.stock.yahoo.com/q/ta?s='
#change path to stock databases
path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)

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

        sql_cmd = 'select capital_amount from stock_info where rowid in (SELECT max(rowid) FROM stock_info)'
        c_stock.execute(sql_cmd)
        base = c_stock.fetchone()[0]
        #print(base)
        if base == None:
            conn_stock.close()
            continue
        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_day')
        date_ID_str = cursor_stock.fetchone()[0]
        if date_ID_str == None:
            continue
        latest_date_inDB = datetime.strptime(date_ID_str, "%Y-%m-%d")
        sql_cmd = 'select rowid from stock_day where date_ID =\'' + date_ID_str + '\''
        c_stock.execute(sql_cmd)
        rowid = c_stock.fetchone()
        if rowid == None:
            conn_stock.close()
            continue
        sql_cmd = 'select foreign_total from stock_day where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        foreign_total_tmp = c_stock.fetchone()[0]
        #print(foreign_total_tmp)
        sql_cmd = 'select invest_trust_total from stock_day where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        invest_trust_total_tmp = c_stock.fetchone()[0]
        #print(invest_trust_total_tmp)
        sql_cmd = 'select open_price from stock_day where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        open_price_tmp = c_stock.fetchone()[0]
        #print(open_price_tmp)
        sql_cmd = 'select Total from stock_day where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        Total_tmp = c_stock.fetchone()[0]
        #print(Total_tmp)
        conn_stock.close()
        
        foreign_ratio = foreign_total_tmp / base
        foreign_ratio = round(foreign_ratio*100, 2)
        invest_ratio = invest_trust_total_tmp / base
        invest_ratio = round(invest_ratio*100, 2)
        stock_price_ratio = Total_tmp /open_price_tmp
        stock_price_ratio = round(stock_price_ratio*100, 2)
        result_stock.append([current_entry[0], current_entry[1], str(foreign_ratio), str(invest_ratio), str(stock_price_ratio)])

conn.close()

print(os.getcwd())
os.chdir('..')
print(os.getcwd())
os.chdir('..')
dir_temp = os.getcwd()
dir_temp = dir_temp + '/temp_pages'
os.chdir(dir_temp)
print(os.getcwd())

result_stock_tmp = result_stock.copy()
result_stock_sort = []
n = 0
for entry_tmp in result_stock_tmp:
    tmp0 = entry_tmp[0]
    tmp1 = entry_tmp[1]
    tmp2 = entry_tmp[2]
    tmp3 = entry_tmp[3]
    tmp4 = entry_tmp[4]
    for entry in result_stock_tmp:
        if (float(tmp2) +  float(tmp3)) < (float(entry[3]) + float(entry[2])):
            tmp0 = entry[0]
            tmp1 = entry[1]
            tmp2 = entry[2]
            tmp3 = entry[3]
            tmp4 = entry[4]

    result_stock_tmp.remove([tmp0, tmp1, tmp2, tmp3, tmp4])
    tmp2 = str(round(float(tmp2) + float(tmp3), 2))
    result_stock_sort.append([tmp0, tmp1, tmp2, tmp3, tmp4])
    n = n + 1
    if n == 20:
        break

for entry in result_stock_sort:
    print(entry)

filename = 'stock_buy_1day.html'
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
            text(str(latest_date_inDB.year) + '/' + str(latest_date_inDB.month) + '/' + str(latest_date_inDB.day))
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
        text('股本比')
    with tag('td', align = 'center'):
        text('期間漲幅')

for entry in result_stock_sort:
    with tag('tr'):
        with tag('td', align = 'center'):
            with tag('a', href = stock_url + entry[0], target='_blank'):
                text(entry[0])
        with tag('td', align = 'center'):
            text(entry[1])
        with tag('td', align = 'center'):
            text(entry[2] + '%')
        with tag('td', align = 'center'):
            text(entry[4] + '%')


f.write(doc.getvalue())
f.write('</table>')

#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()

print('\n')
result_stock_tmp.clear()
result_stock_tmp = result_stock.copy()
result_stock_sort.clear()
result_stock_sort = []
n = 0
for entry_tmp in result_stock_tmp:
    tmp0 = entry_tmp[0]
    tmp1 = entry_tmp[1]
    tmp2 = entry_tmp[2]
    tmp3 = entry_tmp[3]
    tmp4 = entry_tmp[4]
    for entry in result_stock_tmp:
        if (float(tmp2) +  float(tmp3)) > (float(entry[3]) + float(entry[2])):
            tmp0 = entry[0]
            tmp1 = entry[1]
            tmp2 = entry[2]
            tmp3 = entry[3]
            tmp4 = entry[4]
    result_stock_tmp.remove([tmp0, tmp1, tmp2, tmp3, tmp4])
    tmp2 = str(round(float(tmp2) + float(tmp3), 2))
    result_stock_sort.append([tmp0, tmp1, tmp2, tmp3, tmp4])
    n = n + 1
    if n == 20:
        break

for entry in result_stock_sort:
    print(entry)

filename = 'stock_sell_1day.html'
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
            text(str(latest_date_inDB.year) + '/' + str(latest_date_inDB.month) + '/' + str(latest_date_inDB.day))
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
        text('股本比')
    with tag('td', align = 'center'):
        text('期間漲幅')

for entry in result_stock_sort:
    with tag('tr'):
        with tag('td', align = 'center'):
            with tag('a', href = stock_url + entry[0], target='_blank'):
                text(entry[0])
        with tag('td', align = 'center'):
            text(entry[1])
        with tag('td', align = 'center'):
            text(entry[2] + '%')
        with tag('td', align = 'center'):
            text(entry[4] + '%')


f.write(doc.getvalue())
f.write('</table>')

#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()


os.chdir('..')
dir_temp = os.getcwd()
dir_temp = dir_temp + '/DBs'
os.chdir(dir_temp)
conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

#change path to stock databases
path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)

result_stock.clear()

cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business  from stock_list")
for current_entry in cursor:
    if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
        db_name = current_entry[0] + '.db'
        #print(db_name)
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()

        sql_cmd = 'select capital_amount from stock_info where rowid in (SELECT max(rowid) FROM stock_info)'
        c_stock.execute(sql_cmd)
        base = c_stock.fetchone()[0]
        #print(base)
        if base == None:
            conn_stock.close()
            continue

        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_day')
        date_ID_str = cursor_stock.fetchone()[0]
        if date_ID_str == None:
            continue
        latest_date_inDB = datetime.strptime(date_ID_str, "%Y-%m-%d")
        sql_cmd = 'select rowid from stock_day where date_ID =\'' + date_ID_str + '\''
        c_stock.execute(sql_cmd)
        rowid = c_stock.fetchone()
        if rowid == None:
            conn_stock.close()
            continue

        foreign_total_tmp = 0
        invest_trust_total_tmp = 0
        Total_tmp = 0
        
        #5 days total
        for n in range(0, 5):
            sql_cmd = 'select foreign_total from stock_day where rowid =' + str(rowid[0] - n)
            c_stock.execute(sql_cmd)
            foreign_total_tmp += c_stock.fetchone()[0]
            #print(foreign_total_tmp)
            sql_cmd = 'select invest_trust_total from stock_day where rowid =' + str(rowid[0] - n)
            c_stock.execute(sql_cmd)
            invest_trust_total_tmp += c_stock.fetchone()[0]
            #print(invest_trust_total_tmp)
            sql_cmd = 'select Total from stock_day where rowid =' + str(rowid[0] - n)
            c_stock.execute(sql_cmd)
            Total_tmp += c_stock.fetchone()[0]
            #print(Total_tmp)

        sql_cmd = 'select open_price from stock_day where rowid =' + str(rowid[0] - 4)
        c_stock.execute(sql_cmd)
        open_price_tmp = c_stock.fetchone()[0]
        #print(open_price_tmp)

        conn_stock.close()
        
        foreign_ratio = foreign_total_tmp / base
        foreign_ratio = round(foreign_ratio*100, 2)
        invest_ratio = invest_trust_total_tmp / base
        invest_ratio = round(invest_ratio*100, 2)
        stock_price_ratio = Total_tmp /open_price_tmp
        stock_price_ratio = round(stock_price_ratio*100, 2)
        result_stock.append([current_entry[0], current_entry[1], str(foreign_ratio), str(invest_ratio), str(stock_price_ratio)])

conn.close()

print(os.getcwd())
os.chdir('..')
print(os.getcwd())
os.chdir('..')
dir_temp = os.getcwd()
dir_temp = dir_temp + '/temp_pages'
os.chdir(dir_temp)
print(os.getcwd())


result_stock_tmp.clear()
result_stock_tmp = result_stock.copy()
result_stock_sort.clear()
n = 0
for entry_tmp in result_stock_tmp:
    tmp0 = entry_tmp[0]
    tmp1 = entry_tmp[1]
    tmp2 = entry_tmp[2]
    tmp3 = entry_tmp[3]
    tmp4 = entry_tmp[4]
    for entry in result_stock_tmp:
        if (float(tmp2) +  float(tmp3)) < (float(entry[3]) + float(entry[2])):
            tmp0 = entry[0]
            tmp1 = entry[1]
            tmp2 = entry[2]
            tmp3 = entry[3]
            tmp4 = entry[4]

    result_stock_tmp.remove([tmp0, tmp1, tmp2, tmp3, tmp4])
    tmp2 = str(round(float(tmp2) + float(tmp3), 2))
    result_stock_sort.append([tmp0, tmp1, tmp2, tmp3, tmp4])
    n = n + 1
    if n == 20:
        break

for entry in result_stock_sort:
    print(entry)

filename = 'stock_buy_5day.html'
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
            text(str(latest_date_inDB.year) + '/' + str(latest_date_inDB.month) + '/' + str(latest_date_inDB.day))
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
        text('股本比')
    with tag('td', align = 'center'):
        text('期間漲幅')

for entry in result_stock_sort:
    with tag('tr'):
        with tag('td', align = 'center'):
            with tag('a', href = stock_url + entry[0], target='_blank'):
                text(entry[0])
        with tag('td', align = 'center'):
            text(entry[1])
        with tag('td', align = 'center'):
            text(entry[2] + '%')
        with tag('td', align = 'center'):
            text(entry[4] + '%')


f.write(doc.getvalue())
f.write('</table>')

#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()


print('\n')
result_stock_tmp.clear()
result_stock_tmp = result_stock.copy()
result_stock_sort.clear()
n = 0
for entry_tmp in result_stock_tmp:
    tmp0 = entry_tmp[0]
    tmp1 = entry_tmp[1]
    tmp2 = entry_tmp[2]
    tmp3 = entry_tmp[3]
    tmp4 = entry_tmp[4]
    for entry in result_stock_tmp:
        if (float(tmp2) +  float(tmp3)) > (float(entry[3]) + float(entry[2])):
            tmp0 = entry[0]
            tmp1 = entry[1]
            tmp2 = entry[2]
            tmp3 = entry[3]
            tmp4 = entry[4]
    result_stock_tmp.remove([tmp0, tmp1, tmp2, tmp3, tmp4])
    tmp2 = str(round(float(tmp2) + float(tmp3), 2))
    result_stock_sort.append([tmp0, tmp1, tmp2, tmp3, tmp4])
    n = n + 1
    if n == 20:
        break

for entry in result_stock_sort:
    print(entry)

filename = 'stock_sell_5day.html'
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
            text(str(latest_date_inDB.year) + '/' + str(latest_date_inDB.month) + '/' + str(latest_date_inDB.day))
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
        text('股本比')
    with tag('td', align = 'center'):
        text('期間漲幅')

for entry in result_stock_sort:
    with tag('tr'):
        with tag('td', align = 'center'):
            with tag('a', href = stock_url + entry[0], target='_blank'):
                text(entry[0])
        with tag('td', align = 'center'):
            text(entry[1])
        with tag('td', align = 'center'):
            text(entry[2] + '%')
        with tag('td', align = 'center'):
            text(entry[4] + '%')


f.write(doc.getvalue())
f.write('</table>')

#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()

os.chdir('..')
dir_temp = os.getcwd()
dir_temp = dir_temp + '/DBs'
os.chdir(dir_temp)
conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

#change path to stock databases
path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)

result_stock.clear()

cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business  from stock_list")
for current_entry in cursor:
    if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
        db_name = current_entry[0] + '.db'
        #print(db_name)
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()

        sql_cmd = 'select capital_amount from stock_info where rowid in (SELECT max(rowid) FROM stock_info)'
        c_stock.execute(sql_cmd)
        base = c_stock.fetchone()[0]
        #print(base)
        if base == None:
            conn_stock.close()
            continue

        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_day')
        date_ID_str = cursor_stock.fetchone()[0]
        if date_ID_str == None:
            continue
        latest_date_inDB = datetime.strptime(date_ID_str, "%Y-%m-%d")
        sql_cmd = 'select rowid from stock_day where date_ID =\'' + date_ID_str + '\''
        c_stock.execute(sql_cmd)
        rowid = c_stock.fetchone()
        if rowid == None:
            conn_stock.close()
            continue

        foreign_total_tmp = 0
        invest_trust_total_tmp = 0
        Total_tmp = 0
        
        #20 days total
        for n in range(0, 20):
            sql_cmd = 'select foreign_total from stock_day where rowid =' + str(rowid[0] - n)
            c_stock.execute(sql_cmd)
            foreign_total_tmp += c_stock.fetchone()[0]
            #print(foreign_total_tmp)
            sql_cmd = 'select invest_trust_total from stock_day where rowid =' + str(rowid[0] - n)
            c_stock.execute(sql_cmd)
            invest_trust_total_tmp += c_stock.fetchone()[0]
            #print(invest_trust_total_tmp)
            sql_cmd = 'select Total from stock_day where rowid =' + str(rowid[0] - n)
            c_stock.execute(sql_cmd)
            Total_tmp += c_stock.fetchone()[0]
            #print(Total_tmp)

        sql_cmd = 'select open_price from stock_day where rowid =' + str(rowid[0] - 19)
        c_stock.execute(sql_cmd)
        open_price_tmp = c_stock.fetchone()[0]
        #print(open_price_tmp)

        conn_stock.close()
        
        foreign_ratio = foreign_total_tmp / base
        foreign_ratio = round(foreign_ratio*100, 2)
        invest_ratio = invest_trust_total_tmp / base
        invest_ratio = round(invest_ratio*100, 2)
        stock_price_ratio = Total_tmp /open_price_tmp
        stock_price_ratio = round(stock_price_ratio*100, 2)
        result_stock.append([current_entry[0], current_entry[1], str(foreign_ratio), str(invest_ratio), str(stock_price_ratio)])

conn.close()

print(os.getcwd())
os.chdir('..')
print(os.getcwd())
os.chdir('..')
dir_temp = os.getcwd()
dir_temp = dir_temp + '/temp_pages'
os.chdir(dir_temp)
print(os.getcwd())

result_stock_tmp.clear()
result_stock_tmp = result_stock.copy()
result_stock_sort.clear()
n = 0
for entry_tmp in result_stock_tmp:
    tmp0 = entry_tmp[0]
    tmp1 = entry_tmp[1]
    tmp2 = entry_tmp[2]
    tmp3 = entry_tmp[3]
    tmp4 = entry_tmp[4]
    for entry in result_stock_tmp:
        if (float(tmp2) +  float(tmp3)) < (float(entry[3]) + float(entry[2])):
            tmp0 = entry[0]
            tmp1 = entry[1]
            tmp2 = entry[2]
            tmp3 = entry[3]
            tmp4 = entry[4]

    result_stock_tmp.remove([tmp0, tmp1, tmp2, tmp3, tmp4])
    tmp2 = str(round(float(tmp2) + float(tmp3), 2))
    result_stock_sort.append([tmp0, tmp1, tmp2, tmp3, tmp4])
    n = n + 1
    if n == 20:
        break

for entry in result_stock_sort:
    print(entry)

filename = 'stock_buy_20day.html'
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
            text(str(latest_date_inDB.year) + '/' + str(latest_date_inDB.month) + '/' + str(latest_date_inDB.day))
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
        text('股本比')
    with tag('td', align = 'center'):
        text('期間漲幅')

for entry in result_stock_sort:
    with tag('tr'):
        with tag('td', align = 'center'):
            with tag('a', href = stock_url + entry[0], target='_blank'):
                text(entry[0])
        with tag('td', align = 'center'):
            text(entry[1])
        with tag('td', align = 'center'):
            text(entry[2] + '%')
        with tag('td', align = 'center'):
            text(entry[4] + '%')


f.write(doc.getvalue())
f.write('</table>')

#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()


print('\n')
result_stock_tmp.clear()
result_stock_tmp = result_stock.copy()
result_stock_sort.clear()
result_stock_sort = []
n = 0
for entry_tmp in result_stock_tmp:
    tmp0 = entry_tmp[0]
    tmp1 = entry_tmp[1]
    tmp2 = entry_tmp[2]
    tmp3 = entry_tmp[3]
    tmp4 = entry_tmp[4]
    for entry in result_stock_tmp:
        if (float(tmp2) +  float(tmp3)) > (float(entry[3]) + float(entry[2])):
            tmp0 = entry[0]
            tmp1 = entry[1]
            tmp2 = entry[2]
            tmp3 = entry[3]
            tmp4 = entry[4]
    result_stock_tmp.remove([tmp0, tmp1, tmp2, tmp3, tmp4])
    tmp2 = str(round(float(tmp2) + float(tmp3), 2))
    result_stock_sort.append([tmp0, tmp1, tmp2, tmp3, tmp4])
    n = n + 1
    if n == 20:
        break

for entry in result_stock_sort:
    print(entry)

filename = 'stock_sell_20day.html'
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
            text(str(latest_date_inDB.year) + '/' + str(latest_date_inDB.month) + '/' + str(latest_date_inDB.day))
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
        text('股本比')
    with tag('td', align = 'center'):
        text('期間漲幅')

for entry in result_stock_sort:
    with tag('tr'):
        with tag('td', align = 'center'):
            with tag('a', href = stock_url + entry[0], target='_blank'):
                text(entry[0])
        with tag('td', align = 'center'):
            text(entry[1])
        with tag('td', align = 'center'):
            text(entry[2] + '%')
        with tag('td', align = 'center'):
            text(entry[4] + '%')


f.write(doc.getvalue())
f.write('</table>')

#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()

"""
for entry in result_stock_sort:
    print(entry)
print('\n')
result_stock_tmp.clear()
result_stock_tmp = result_stock.copy()
result_stock_sort.clear()
result_stock_sort = []
n = 0
for entry_tmp in result_stock_tmp:
    tmp0 = entry_tmp[0]
    tmp1 = entry_tmp[1]
    tmp2 = entry_tmp[2]
    tmp3 = entry_tmp[3]
    tmp4 = entry_tmp[4]
    for entry in result_stock_tmp:
        if float(tmp2) < float(entry[2]):
            tmp0 = entry[0]
            tmp1 = entry[1]
            tmp2 = entry[2]
            tmp3 = entry[3]
            tmp4 = entry[4]
    result_stock_sort.append([tmp0, tmp1, tmp2, tmp3, tmp4])
    result_stock_tmp.remove([tmp0, tmp1, tmp2, tmp3, tmp4])
    n = n + 1
    if n == 20:
        break

for entry in result_stock_sort:
    print(entry)
"""


