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

#change path to stock databases
path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)

stock_url = 'https://tw.stock.yahoo.com/q/ta?s='

delta_1day = timedelta(days = 1) #delta_1day

result_stock = []
result_color = []
colors = [0,0,0,0,0,0,0,0,0,0]
cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business  from stock_list")
for current_entry in cursor:
    if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
        db_name = current_entry[0] + '.db'
        print(db_name)
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()

        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_week')
        date_ID_str = cursor_stock.fetchone()[0]
        if date_ID_str == None:
            conn_stock.close()
            continue
        latest_date_inDB = datetime.strptime(date_ID_str, "%Y-%m-%d")
        sql_cmd = 'select rowid from stock_week where date_ID =\'' + date_ID_str + '\''
        c_stock.execute(sql_cmd)
        rowid = c_stock.fetchone()
        if rowid == None:
            conn_stock.close()
            continue

        sql_cmd = 'select holder400_per from stock_week where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        holder400_per_tmp = c_stock.fetchone()[0]
        #print(foreign_total_tmp)
        sql_cmd = 'select total_people from stock_week where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        total_people_tmp = c_stock.fetchone()[0]
        #print(invest_trust_total_tmp)
        n = 1
        
        if (rowid[0] - n) <= 0:
            conn_stock.close()
            continue
        sql_cmd = 'select holder400_per from stock_week where rowid =' + str(rowid[0] - n)
        c_stock.execute(sql_cmd)
        holder400_per_tmp_before = c_stock.fetchone()[0]
        #print(foreign_total_tmp)
        sql_cmd = 'select total_people from stock_week where rowid =' + str(rowid[0] - n)
        c_stock.execute(sql_cmd)
        total_people_tmp_before = c_stock.fetchone()[0]

        sql_cmd = 'select date_ID from stock_week where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        date_ID_str_0 = cursor_stock.fetchone()[0]
        sql_cmd = 'select date_ID from stock_week where rowid =' + str(rowid[0] - n)
        c_stock.execute(sql_cmd)
        date_ID_str_1 = cursor_stock.fetchone()[0]

        fetch_date = datetime.strptime(date_ID_str_0, "%Y-%m-%d")
        while 1:
            sql_cmd = 'select close_price from stock_day where date_ID = \'' + date_ID_str_0 + '\''
            c_stock.execute(sql_cmd)
            close_price_0 = cursor_stock.fetchone()
            if close_price_0 == None:
                fetch_date = fetch_date - delta_1day
                date_ID_str_0 = str(fetch_date.year) + '-' + fetch_date.strftime("%m") + '-' + fetch_date.strftime("%d")
                continue
            else:
                break

        fetch_date = datetime.strptime(date_ID_str_1, "%Y-%m-%d")
        while 1:
            sql_cmd = 'select close_price from stock_day where date_ID = \'' + date_ID_str_1 + '\''
            c_stock.execute(sql_cmd)
            close_price_1 = cursor_stock.fetchone()
            if close_price_1 == None:
                fetch_date = fetch_date - delta_1day
                date_ID_str_1 = str(fetch_date.year) + '-' + fetch_date.strftime("%m") + '-' + fetch_date.strftime("%d")
                continue
            else:
                break
        conn_stock.close()
        
        increase_ratio = holder400_per_tmp - holder400_per_tmp_before
        stock_price_ratio = (close_price_0[0] - close_price_1[0])/close_price_1[0]
        stock_price_ratio = round(stock_price_ratio*100, 2)
        result_stock.append([current_entry[0], current_entry[1], str(increase_ratio), str(stock_price_ratio)])

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
    for entry in result_stock_tmp:
        if (float(tmp2)) < (float(entry[2])):
            tmp0 = entry[0]
            tmp1 = entry[1]
            tmp2 = entry[2]
            tmp3 = entry[3]
    result_stock_tmp.remove([tmp0, tmp1, tmp2, tmp3])
    tmp2 = str(round(float(tmp2), 2))
    result_stock_sort.append([tmp0, tmp1, tmp2, tmp3])
    print(n)
    n = n + 1
    if n == 20:
        break

for entry in result_stock_sort:
    print(entry)

filename = 'stock_holder_ratio_increase_1week.html'
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
        text('增加比')
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
            text(entry[3] + '%')


f.write(doc.getvalue())
f.write('</table>')

#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()

result_stock_tmp.clear()
result_stock_tmp = result_stock.copy()
result_stock_sort.clear()
n = 0

for entry_tmp in result_stock_tmp:
    tmp0 = entry_tmp[0]
    tmp1 = entry_tmp[1]
    tmp2 = entry_tmp[2]
    tmp3 = entry_tmp[3]
    for entry in result_stock_tmp:
        if (float(tmp2)) > (float(entry[2])):
            tmp0 = entry[0]
            tmp1 = entry[1]
            tmp2 = entry[2]
            tmp3 = entry[3]
    result_stock_tmp.remove([tmp0, tmp1, tmp2, tmp3])
    tmp2 = str(round(float(tmp2), 2))
    result_stock_sort.append([tmp0, tmp1, tmp2, tmp3])
    n = n + 1
    if n == 20:
        break

for entry in result_stock_sort:
    print(entry)

filename = 'stock_holder_ratio_decrease_1week.html'
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
        text('增加比')
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
            text(entry[3] + '%')


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

        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_week')
        date_ID_str = cursor_stock.fetchone()[0]
        if date_ID_str == None:
            continue
        latest_date_inDB = datetime.strptime(date_ID_str, "%Y-%m-%d")
        sql_cmd = 'select rowid from stock_week where date_ID =\'' + date_ID_str + '\''
        c_stock.execute(sql_cmd)
        rowid = c_stock.fetchone()
        if rowid == None:
            conn_stock.close()
            continue

        sql_cmd = 'select holder400_per from stock_week where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        holder400_per_tmp = c_stock.fetchone()[0]
        #print(foreign_total_tmp)
        sql_cmd = 'select total_people from stock_week where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        total_people_tmp = c_stock.fetchone()[0]
        #print(invest_trust_total_tmp)
        n = 4

        if (rowid[0] - n) <= 0:
            conn_stock.close()
            continue
        sql_cmd = 'select holder400_per from stock_week where rowid =' + str(rowid[0] - n)
        c_stock.execute(sql_cmd)
        holder400_per_tmp_before = c_stock.fetchone()[0]
        #print(foreign_total_tmp)
        sql_cmd = 'select total_people from stock_week where rowid =' + str(rowid[0] - n)
        c_stock.execute(sql_cmd)
        total_people_tmp_before = c_stock.fetchone()[0]

        sql_cmd = 'select date_ID from stock_week where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        date_ID_str_0 = cursor_stock.fetchone()[0]
        sql_cmd = 'select date_ID from stock_week where rowid =' + str(rowid[0] - n)
        c_stock.execute(sql_cmd)
        date_ID_str_1 = cursor_stock.fetchone()[0]

        fetch_date = datetime.strptime(date_ID_str_0, "%Y-%m-%d")
        while 1:
            sql_cmd = 'select close_price from stock_day where date_ID = \'' + date_ID_str_0 + '\''
            c_stock.execute(sql_cmd)
            close_price_0 = cursor_stock.fetchone()
            if close_price_0 == None:
                fetch_date = fetch_date - delta_1day
                date_ID_str_0 = str(fetch_date.year) + '-' + fetch_date.strftime("%m") + '-' + fetch_date.strftime("%d")
                continue
            else:
                break

        fetch_date = datetime.strptime(date_ID_str_1, "%Y-%m-%d")
        while 1:
            sql_cmd = 'select close_price from stock_day where date_ID = \'' + date_ID_str_1 + '\''
            c_stock.execute(sql_cmd)
            close_price_1 = cursor_stock.fetchone()
            if close_price_1 == None:
                fetch_date = fetch_date - delta_1day
                date_ID_str_1 = str(fetch_date.year) + '-' + fetch_date.strftime("%m") + '-' + fetch_date.strftime("%d")
                continue
            else:
                break
        conn_stock.close()
        
        increase_ratio = holder400_per_tmp - holder400_per_tmp_before
        stock_price_ratio = (close_price_0[0] - close_price_1[0])/close_price_1[0]
        stock_price_ratio = round(stock_price_ratio*100, 2)
        result_stock.append([current_entry[0], current_entry[1], str(increase_ratio), str(stock_price_ratio)])

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
    for entry in result_stock_tmp:
        if (float(tmp2)) < (float(entry[2])):
            tmp0 = entry[0]
            tmp1 = entry[1]
            tmp2 = entry[2]
            tmp3 = entry[3]
    result_stock_tmp.remove([tmp0, tmp1, tmp2, tmp3])
    tmp2 = str(round(float(tmp2), 2))
    result_stock_sort.append([tmp0, tmp1, tmp2, tmp3])
    n = n + 1
    if n == 20:
        break

for entry in result_stock_sort:
    print(entry)

filename = 'stock_holder_ratio_increase_4week.html'
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
        text('增加比')
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
            text(entry[3] + '%')


f.write(doc.getvalue())
f.write('</table>')

#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()

result_stock_tmp.clear()
result_stock_tmp = result_stock.copy()
result_stock_sort.clear()
n = 0

for entry_tmp in result_stock_tmp:
    tmp0 = entry_tmp[0]
    tmp1 = entry_tmp[1]
    tmp2 = entry_tmp[2]
    tmp3 = entry_tmp[3]
    for entry in result_stock_tmp:
        if (float(tmp2)) > (float(entry[2])):
            tmp0 = entry[0]
            tmp1 = entry[1]
            tmp2 = entry[2]
            tmp3 = entry[3]
    result_stock_tmp.remove([tmp0, tmp1, tmp2, tmp3])
    tmp2 = str(round(float(tmp2), 2))
    result_stock_sort.append([tmp0, tmp1, tmp2, tmp3])
    n = n + 1
    if n == 20:
        break

for entry in result_stock_sort:
    print(entry)

filename = 'stock_holder_ratio_decrease_4week.html'
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
        text('增加比')
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
            text(entry[3] + '%')


f.write(doc.getvalue())
f.write('</table>')

#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()