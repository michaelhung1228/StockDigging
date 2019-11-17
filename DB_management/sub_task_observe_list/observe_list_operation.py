import requests, os, bs4, sys
import re, time
import sqlite3
from datetime import datetime
from datetime import timedelta
from yattag import Doc

import index_computation

input_arg = sys.argv

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

print(input_arg[1])
print(len(input_arg))

result_stock_long = []
result_color_long = []
result_stock_short = []
result_color_short = []
colors = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

if input_arg[1] == 'add-long':
    for i in range(2, len(input_arg)):
        print(input_arg[i])
        sql_cmd = 'UPDATE stock_list set observation = 1 WHERE stock_ID =' + input_arg[i]
        c.execute(sql_cmd)
        conn.commit()
elif input_arg[1] == 'add-short':
    for i in range(2, len(input_arg)):
        print(input_arg[i])
        sql_cmd = 'UPDATE stock_list set observation = 2 WHERE stock_ID =' + input_arg[i]
        c.execute(sql_cmd)
        conn.commit()
elif input_arg[1] == 'delete':
    for i in range(2, len(input_arg)):
        print(input_arg[i])
        sql_cmd = 'UPDATE stock_list set observation = 0 WHERE stock_ID =' + input_arg[i]
        c.execute(sql_cmd)
        conn.commit()
elif input_arg[1] == 'print':
    print(input_arg[1])
    cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business, observation from stock_list")
    for current_entry in cursor:
        if current_entry[5] == 0:
            continue
        db_name = current_entry[0] + '.db'
        print(db_name)
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()
        c_stock.execute('SELECT max(rowid) FROM stock_day')
        rowid = c_stock.fetchone()
        sql_cmd = 'select volume from stock_day where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        volume_tmp0 = c_stock.fetchone()[0]
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
            if volume_tmp0 <= volume_tmp1:
                n = n +1
            else:
                break
        volume_period_low = n
        n = 0
        while 1:
            if (rowid[0] - n - 1) < 1:
                break
            sql_cmd = 'select volume from stock_day where rowid =' + str(rowid[0] - n - 1)
            c_stock.execute(sql_cmd)
            volume_tmp1 = c_stock.fetchone()[0]
            if volume_tmp0 >= volume_tmp1:
                n = n +1
            else:
                break
        volume_period_high = n
        #計算本益比:以及最近一季EPS
        cursor_stock = c_stock.execute('SELECT max(rowid) FROM stock_quarter')
        rowid = cursor_stock.fetchone()
        EPS_total = 0
        EPS_tmp = []
        for n in range(0, 4):
            sql_cmd = 'select EPS from stock_quarter where rowid =' + str(rowid[0] - n)
            c_stock.execute(sql_cmd)
            EPS_tmp0 = c_stock.fetchone()[0]
            if EPS_tmp0 == None:
                EPS_tmp0 = 0
            EPS_tmp.append(EPS_tmp0)
            EPS_total = EPS_total + EPS_tmp[n]
        if EPS_total == 0:
            EPS_total = 0.00001
        EPS = EPS_tmp[0]
        PER = float(close_price_tmp)/float(EPS_total)
        PER = round(PER, 2)
        #毛利率以及營益率
        sql_cmd = 'select gross_margin from stock_quarter where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        gross_margin = c_stock.fetchone()[0]
        sql_cmd = 'select operating_profit_margin from stock_quarter where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        operating_profit_margin = c_stock.fetchone()[0]
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
        #MA direction
        MA3_direction = index_computation.MA_direction_today('stock_day', 3, 0, c_stock)
        if MA3_direction == True:
            MA3_direction = '↑'
        else:
            MA3_direction = '↓'
        MA18_direction = index_computation.MA_direction_today('stock_day', 18, 0, c_stock)
        if MA18_direction == True:
            MA18_direction = '↑'
        else:
            MA18_direction = '↓'
        MA54_direction = index_computation.MA_direction_today('stock_day', 54, 0, c_stock)
        if MA54_direction == True:
            MA54_direction = '↑'
        else:
            MA54_direction = '↓'
        #MA 扣抵
        MA3_gap = index_computation.MA_twist_prediction_today('stock_day', 3, c_stock)
        MA18_gap = index_computation.MA_twist_prediction_today('stock_day', 18, c_stock)
        MA54_gap = index_computation.MA_twist_prediction_today('stock_day', 54, c_stock)
        MA3_gap = round(MA3_gap*100, 2)
        MA18_gap = round(MA18_gap*100, 2)
        MA54_gap = round(MA54_gap*100, 2)
        #MA扭轉
        MA3_twist = index_computation.MA_twist_today('stock_day', 3, c_stock)
        if MA3_twist == 1:
            MA3_twist = '▲'
        elif MA3_twist == 2:
            MA3_twist = '▼'
        else:
            MA3_twist = ' '
        MA18_twist = index_computation.MA_twist_today('stock_day', 18, c_stock)
        if MA18_twist == 1:
            MA18_twist = '▲'
        elif MA18_twist == 2:
            MA18_twist = '▼'
        else:
            MA18_twist = ' '
        MA54_twist = index_computation.MA_twist_today('stock_day', 54, c_stock)
        if MA54_twist == 1:
            MA54_twist = '▲'
        elif MA54_twist == 2:
            MA54_twist = '▼'
        else:
            MA54_twist = ' '
        #MA乖離
        MA3_distance = index_computation.MA_distance_today('stock_day', 3, c_stock)
        MA18_distance = index_computation.MA_distance_today('stock_day', 18, c_stock)
        MA54_distance = index_computation.MA_distance_today('stock_day', 54, c_stock)
        #MACD DIFF
        c_stock.execute('SELECT max(rowid) FROM stock_day')
        rowid = c_stock.fetchone()
        sql_cmd = 'select MACD_DIFF from stock_day where rowid =' + str(rowid[0])
        c_stock.execute(sql_cmd)
        MACD_DIFF_tmp = c_stock.fetchone()[0]
        if MACD_DIFF_tmp == None:
            break
        MACD_DIFF_tmp = round(MACD_DIFF_tmp, 2)
        #MACD方向
        MACD_direction = index_computation.MACD_direction_today('stock_day', c_stock)
        if MACD_direction == 1:
            MACD_direction = '↑'
        else:
            MACD_direction = '↓'
        #MACD轉折
        MACD_twist = index_computation.MACD_twist_today('stock_day', c_stock)
        if MACD_twist == 1:
            MACD_twist = '▲'
        elif MACD_twist == 2:
            MACD_twist = '▼'
        else:
            MACD_twist = ' '

        if current_entry[5] == 1:
            result_stock_long.append([current_entry[0], current_entry[1], close_price_tmp, volume, turnover_rate, volume_period_low, volume_period_high, PER, EPS,\
                gross_margin, operating_profit_margin, quarter_growth, year_growth, total_ratio_1day, total_ratio_5day, total_ratio_20day, increase_ratio_1week, increase_ratio_4week,\
                MA3_direction, MA18_direction, MA54_direction, MA3_gap, MA18_gap, MA54_gap, MA3_twist, MA18_twist, MA54_twist, MA3_distance, MA18_distance, MA54_distance, \
                MACD_DIFF_tmp, MACD_direction, MACD_twist])
        if current_entry[5] == 2:
            result_stock_short.append([current_entry[0], current_entry[1], close_price_tmp, volume, turnover_rate, volume_period_low, volume_period_high, PER, EPS,\
                gross_margin, operating_profit_margin, quarter_growth, year_growth, total_ratio_1day, total_ratio_5day, total_ratio_20day, increase_ratio_1week, increase_ratio_4week,\
                MA3_direction, MA18_direction, MA54_direction, MA3_gap, MA18_gap, MA54_gap, MA3_twist, MA18_twist, MA54_twist, MA3_distance, MA18_distance, MA54_distance, \
                MACD_DIFF_tmp, MACD_direction, MACD_twist])
        conn_stock.close()        
conn.close()

#sorting by the period of the days
for i in range(0, len(result_stock_long) - 1):
    j = i + 1
    largest = int(result_stock_long[i][5])
    k = i
    for j in range(i+1, len(result_stock_long)):
        #print(result_stock_tmp[j][0])
        if largest < int(result_stock_long[j][5]):
            largest = int(result_stock_long[j][5])
            k = j
    tmp = result_stock_long[i]
    result_stock_long[i] = result_stock_long[k]
    result_stock_long[k] = tmp

for entry in result_stock_long:
    for i in range(0,40):
        colors[i] = 0

    if (float(entry[7]) < 25) and (float(entry[7]) > 0):
        colors[7] = 2
    if (float(entry[7]) < 15) and (float(entry[7]) > 0):
        colors[7] = 3

    if float(entry[9]) > 15:
        colors[9] = 2
    if float(entry[9]) > 30:
        colors[9] = 3

    if float(entry[10]) > 10:
        colors[10] = 2
    if float(entry[10]) > 20:
        colors[10] = 3

    if float(entry[11]) > 15:
        colors[11] = 2
    if float(entry[11]) > 25:
        colors[11] = 3

    if float(entry[12]) > 10:
        colors[12] = 2
    if float(entry[12]) > 20:
        colors[12] = 3

    if float(entry[13]) > 0.2:
        colors[13] = 2
    if float(entry[13]) > 0.5:
        colors[13] = 3

    if float(entry[14]) > 0.5:
        colors[14] = 2
    if float(entry[14]) > 1:
        colors[14] = 3

    if float(entry[15]) > 1:
        colors[15] = 2
    if float(entry[15]) > 1.5:
        colors[15] = 3

    if float(entry[16]) > 0.5:
        colors[16] = 2
    if float(entry[16]) > 1:
        colors[16] = 3

    if float(entry[17]) > 1:
        colors[17] = 2
    if float(entry[17]) > 1.5:
        colors[17] = 3

    if (entry[18] == '↓') and (float(entry[21]) < 0):
        colors[18] = 3
    if (entry[24] == '▲'):
        colors[18] = 3

    if (entry[19] == '↓') and (float(entry[22]) < 0):
        colors[19] = 3
    if (entry[25] == '▲'):
        colors[19] = 3

    if (entry[20] == '↓') and (float(entry[23]) < 0):
        colors[20] = 3
    if (entry[26] == '▲'):
        colors[20] = 3

    if (entry[32] == '▲'):
        colors[30] = 3
    result_color_long.append([colors[0], colors[1], colors[2], colors[3], colors[4], colors[5], colors[6], colors[7], colors[8], colors[9], colors[10], colors[11]\
        , colors[12], colors[13], colors[14], colors[15], colors[16], colors[17], colors[18], colors[19], colors[20], colors[21], colors[22], colors[23], colors[24]\
        , colors[25], colors[26], colors[27], colors[28], colors[29], colors[30], colors[31], colors[32], colors[33], colors[34], colors[35], colors[36], colors[37]])
    print(entry)

#sorting by the period of the days
for i in range(0, len(result_stock_short) - 1):
    j = i + 1
    largest = int(result_stock_short[i][6])
    k = i
    for j in range(i+1, len(result_stock_short)):
        #print(result_stock_tmp[j][0])
        if largest < int(result_stock_short[j][6]):
            largest = int(result_stock_short[j][6])
            k = j
    tmp = result_stock_short[i]
    result_stock_short[i] = result_stock_short[k]
    result_stock_short[k] = tmp

for entry in result_stock_short:
    for i in range(0,40):
        colors[i] = 0

    result_color_short.append([colors[0], colors[1], colors[2], colors[3], colors[4], colors[5], colors[6], colors[7], colors[8], colors[9], colors[10], colors[11]\
        , colors[12], colors[13], colors[14], colors[15], colors[16], colors[17], colors[18], colors[19], colors[20], colors[21], colors[22], colors[23], colors[24]\
        , colors[25], colors[26], colors[27], colors[28], colors[29], colors[30], colors[31], colors[32], colors[33], colors[34], colors[35], colors[36], colors[37]])
    print(entry)

print(os.getcwd())
os.chdir('..')
print(os.getcwd())
os.chdir('..')
dir_temp = os.getcwd()
dir_temp = dir_temp + '/observation_page'
os.chdir(dir_temp)
print(os.getcwd())
today_date = datetime.today()

if input_arg[1] == 'print':
    filename = today_date.strftime("%Y%m%d") + '_observation.html'
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
                text(str(datetime.today()))
    
    doc.asis('<br>')
    f.write(doc.getvalue())
    doc, tag, text = Doc().tagtext()
    f.write('<table border=1>')
    with tag('tr'):
        with tag('td', align = 'center'):
            text('多方候選名單')
    with tag('tr'):
        with tag('td', align = 'center'):
            text('代碼')
        with tag('td', align = 'center'):
            text('公司')
        with tag('td', align = 'center'):
            text('成交價')
        with tag('td', align = 'center'):
            text('成交量')
        with tag('td', align = 'center'):
            text('周轉率')
        with tag('td', align = 'center'):
            text('成交量')
            doc.asis('<br>')
            text('日數新低')
        with tag('td', align = 'center'):
            text('成交量')
            doc.asis('<br>')
            text('日數新高')
        with tag('td', align = 'center'):
            text('本益比')
        with tag('td', align = 'center'):
            text('近一季')
            doc.asis('<br>')
            text('EPS')
        with tag('td', align = 'center'):
            text('毛利率')
        with tag('td', align = 'center'):
            text('營利率')
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
        with tag('td', align = 'center'):
            text('400張以上')
            doc.asis('<br>')
            text('大戶持股變化:')
            doc.asis('<br>')
            text('1周 / 4周 ')
        with tag('td', align = 'center'):
            text('MA3')
            doc.asis('<br>')
            text('方向 / 扣抵 / 扭轉 / 乖離')
        with tag('td', align = 'center'):
            text('MA18')
            doc.asis('<br>')
            text('方向 / 扣抵 / 扭轉 / 乖離')
        with tag('td', align = 'center'):
            text('MA54')
            doc.asis('<br>')
            text('方向 / 扣抵 / 扭轉 / 乖離')
        with tag('td', align = 'center'):
            text('MACD')
            doc.asis('<br>')
            text('DIFF值/方向/轉折')
    cnt = 0
    for stock in result_stock_long:
        with tag('tr'):
            with tag('td', align = 'center'):
                with tag('a', href = stock_url + stock[0], target='_blank'):
                    text(stock[0])
            with tag('td', align = 'center'):
                text(stock[1])
            with tag('td', align = 'center'):
                text(stock[2])
            with tag('td', align = 'center'):
                text(stock[3])
            with tag('td', align = 'center'):
                text(str(stock[4]) + '%')
            with tag('td', align = 'center'):
                text(stock[5])
            with tag('td', align = 'center'):
                text(stock[6])
            with tag('td', align = 'center'):
                if result_color_long[cnt][7] == 2:
                    with tag('font', color = '#009100'):
                        text(stock[7])
                elif result_color_long[cnt][7] == 3:
                    with tag('font', color = '#FF0000'):
                        text(stock[7])
                else:
                    text(stock[7])
            with tag('td', align = 'center'):
                text(stock[8])
            with tag('td', align = 'center'):
                if result_color_long[cnt][9] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[9]) + '%')
                elif result_color_long[cnt][9] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[9]) + '%')
                else:
                    text(str(stock[9]) + '%')
            with tag('td', align = 'center'):
                if result_color_long[cnt][10] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[10]) + '%')
                elif result_color_long[cnt][10] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[10]) + '%')
                else:
                    text(str(stock[10]) + '%')
            with tag('td', align = 'center'):
                if result_color_long[cnt][11] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[11]) + '%')
                elif result_color_long[cnt][11] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[11]) + '%')
                else:
                    text(str(stock[11]) + '%')
                doc.asis(' / ')
                if result_color_long[cnt][12] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[12]) + '%')
                elif result_color_long[cnt][12] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[12]) + '%')
                else:
                    text(str(stock[12]) + '%')
            with tag('td', align = 'center'):
                if result_color_long[cnt][13] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[13]) + '%')
                elif result_color_long[cnt][13] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[13]) + '%')
                else:
                    text(str(stock[13]) + '%')
                doc.asis(' / ')
                if result_color_long[cnt][14] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[14]) + '%')
                elif result_color_long[cnt][14] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[14]) + '%')
                else:
                    text(str(stock[14]) + '%')
                doc.asis(' / ')
                if result_color_long[cnt][15] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[15]) + '%')
                elif result_color_long[cnt][15] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[15]) + '%')
                else:
                    text(str(stock[15]) + '%')
            with tag('td', align = 'center'):
                if result_color_long[cnt][16] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[16]) + '%')
                elif result_color_long[cnt][16] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[16]) + '%')
                else:
                    text(str(stock[16]) + '%')
                doc.asis(' / ')
                if result_color_long[cnt][17] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[17]) + '%')
                elif result_color_long[cnt][17] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[17]) + '%')
                else:
                    text(str(stock[17]) + '%')
            with tag('td', align = 'center'):
                if result_color_long[cnt][18] == 3:
                    with tag('font', color = '#FF7575'):
                        text(str(stock[18]) + '/' + str(stock[21])  + '%/' + str(stock[24]) + '/' + str(stock[27]) + '%')
                else:
                    text(str(stock[18]) + '/' + str(stock[21])  + '%/' + str(stock[24]) + '/' + str(stock[27]) + '%')
            with tag('td', align = 'center'):
                if result_color_long[cnt][19] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[19]) + '/' + str(stock[22])  + '%/' + str(stock[25]) + '/' + str(stock[28]) + '%')
                else:
                    text(str(stock[19]) + '/' + str(stock[22])  + '%/' + str(stock[25]) + '/' + str(stock[28]) + '%')
            with tag('td', align = 'center'):
                if result_color_long[cnt][20] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[20]) + '/' + str(stock[23])  + '%/' + str(stock[26]) + '/' + str(stock[29]) + '%')
                else:
                    text(str(stock[20]) + '/' + str(stock[23])  + '%/' + str(stock[26]) + '/' + str(stock[29]) + '%')
            with tag('td', align = 'center'):
                if result_color_long[cnt][30] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[30]) + '/' + str(stock[31])  + '/' +str(stock[32]))
                else:
                    text(str(stock[30]) + '/' + str(stock[31])  + '/' +str(stock[32]))
        cnt = cnt + 1
    
    with tag('tr'):
        with tag('td', align = 'center'):
            text('共' + str(cnt) + '筆')
    f.write(doc.getvalue())
    f.write('</table>')

    doc, tag, text = Doc().tagtext()
    doc.asis('<br>')
    f.write(doc.getvalue())
    f.write('<table border=1>')
    doc, tag, text = Doc().tagtext()
    with tag('tr'):
        with tag('td', align = 'center'):
            text('空方候選名單')
    with tag('tr'):
        with tag('td', align = 'center'):
            text('代碼')
        with tag('td', align = 'center'):
            text('公司')
        with tag('td', align = 'center'):
            text('成交價')
        with tag('td', align = 'center'):
            text('成交量')
        with tag('td', align = 'center'):
            text('周轉率')
        with tag('td', align = 'center'):
            text('成交量')
            doc.asis('<br>')
            text('日數新低')
        with tag('td', align = 'center'):
            text('成交量')
            doc.asis('<br>')
            text('日數新高')
        with tag('td', align = 'center'):
            text('本益比')
        with tag('td', align = 'center'):
            text('近一季')
            doc.asis('<br>')
            text('EPS')
        with tag('td', align = 'center'):
            text('毛利率')
        with tag('td', align = 'center'):
            text('營利率')
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
        with tag('td', align = 'center'):
            text('400張以上')
            doc.asis('<br>')
            text('大戶持股變化:')
            doc.asis('<br>')
            text('1周 / 4周 ')
        with tag('td', align = 'center'):
            text('MA3')
            doc.asis('<br>')
            text('方向 / 扣抵 / 扭轉 / 乖離')
        with tag('td', align = 'center'):
            text('MA18')
            doc.asis('<br>')
            text('方向 / 扣抵 / 扭轉 / 乖離')
        with tag('td', align = 'center'):
            text('MA54')
            doc.asis('<br>')
            text('方向 / 扣抵 / 扭轉 / 乖離')
        with tag('td', align = 'center'):
            text('MACD')
            doc.asis('<br>')
            text('DIFF值/方向/轉折')
    cnt = 0
    for stock in result_stock_short:
        with tag('tr'):
            with tag('td', align = 'center'):
                with tag('a', href = stock_url + stock[0], target='_blank'):
                    text(stock[0])
            with tag('td', align = 'center'):
                text(stock[1])
            with tag('td', align = 'center'):
                text(stock[2])
            with tag('td', align = 'center'):
                text(stock[3])
            with tag('td', align = 'center'):
                text(str(stock[4]) + '%')
            with tag('td', align = 'center'):
                text(stock[5])
            with tag('td', align = 'center'):
                text(stock[6])
            with tag('td', align = 'center'):
                if result_color_short[cnt][7] == 2:
                    with tag('font', color = '#009100'):
                        text(stock[7])
                elif result_color_short[cnt][7] == 3:
                    with tag('font', color = '#FF0000'):
                        text(stock[7])
                else:
                    text(stock[7])
            with tag('td', align = 'center'):
                text(stock[8])
            with tag('td', align = 'center'):
                if result_color_short[cnt][9] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[9]) + '%')
                elif result_color_short[cnt][9] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[9]) + '%')
                else:
                    text(str(stock[9]) + '%')
            with tag('td', align = 'center'):
                if result_color_short[cnt][10] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[10]) + '%')
                elif result_color_short[cnt][10] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[10]) + '%')
                else:
                    text(str(stock[10]) + '%')
            with tag('td', align = 'center'):
                if result_color_short[cnt][11] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[11]) + '%')
                elif result_color_short[cnt][11] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[11]) + '%')
                else:
                    text(str(stock[11]) + '%')
                doc.asis(' / ')
                if result_color_short[cnt][12] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[12]) + '%')
                elif result_color_short[cnt][12] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[12]) + '%')
                else:
                    text(str(stock[12]) + '%')
            with tag('td', align = 'center'):
                if result_color_short[cnt][13] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[13]) + '%')
                elif result_color_short[cnt][13] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[13]) + '%')
                else:
                    text(str(stock[13]) + '%')
                doc.asis(' / ')
                if result_color_short[cnt][14] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[14]) + '%')
                elif result_color_short[cnt][14] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[14]) + '%')
                else:
                    text(str(stock[14]) + '%')
                doc.asis(' / ')
                if result_color_short[cnt][15] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[15]) + '%')
                elif result_color_short[cnt][15] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[15]) + '%')
                else:
                    text(str(stock[15]) + '%')
            with tag('td', align = 'center'):
                if result_color_short[cnt][16] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[16]) + '%')
                elif result_color_short[cnt][16] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[16]) + '%')
                else:
                    text(str(stock[16]) + '%')
                doc.asis(' / ')
                if result_color_short[cnt][17] == 2:
                    with tag('font', color = '#009100'):
                        text(str(stock[17]) + '%')
                elif result_color_short[cnt][17] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[17]) + '%')
                else:
                    text(str(stock[17]) + '%')
            with tag('td', align = 'center'):
                if result_color_short[cnt][18] == 3:
                    with tag('font', color = '#FF7575'):
                        text(str(stock[18]) + '/' + str(stock[21])  + '%/' + str(stock[24]) + '/' + str(stock[27]) + '%')
                else:
                    text(str(stock[18]) + '/' + str(stock[21])  + '%/' + str(stock[24]) + '/' + str(stock[27]) + '%')
            with tag('td', align = 'center'):
                if result_color_short[cnt][19] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[19]) + '/' + str(stock[22])  + '%/' + str(stock[25]) + '/' + str(stock[28]) + '%')
                else:
                    text(str(stock[19]) + '/' + str(stock[22])  + '%/' + str(stock[25]) + '/' + str(stock[28]) + '%')
            with tag('td', align = 'center'):
                if result_color_short[cnt][20] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[20]) + '/' + str(stock[23])  + '%/' + str(stock[26]) + '/' + str(stock[29]) + '%')
                else:
                    text(str(stock[20]) + '/' + str(stock[23])  + '%/' + str(stock[26]) + '/' + str(stock[29]) + '%')
            with tag('td', align = 'center'):
                if result_color_short[cnt][30] == 3:
                    with tag('font', color = '#FF0000'):
                        text(str(stock[30]) + '/' + str(stock[31])  + '/' +str(stock[32]))
                else:
                    text(str(stock[30]) + '/' + str(stock[31])  + '/' +str(stock[32]))
        cnt = cnt + 1
    
    with tag('tr'):
        with tag('td', align = 'center'):
            text('共' + str(cnt) + '筆')
    f.write(doc.getvalue())
    f.write('</table>')

    #print link to yesterday and tomorrow
    delta_1day = timedelta(days = 1) #delta_1day
    yesterday_date = today_date - delta_1day
    tomorrow_date = today_date + delta_1day
    doc, tag, text = Doc().tagtext()
    
    doc.asis('<br>')
    filename_tmp = '<a href="' + yesterday_date.strftime("%Y%m%d") + '_observation.html' + '">前一天的資料</a>'
    doc.asis(filename_tmp)
    doc.asis('<br>')
    filename_tmp = '<a href="' + tomorrow_date.strftime("%Y%m%d") + '_observation.html' + '">後一天的資料</a>'
    doc.asis(filename_tmp)
    f.write(doc.getvalue())

    #end of the html page
    temp_html_content = """
    </body>
    </html>
    """
    f.write(temp_html_content)
    f.close()

    command = 'copy ' + filename + ' today_observation.html'
    os.system(command)
    
    #print temporary file for not happened tomorrow
    filename = tomorrow_date.strftime("%Y%m%d") + '_observation.html'
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
    filename_tmp = '<a href="' + today_date.strftime("%Y%m%d") + '_observation.html' + '">回到今天</a>'
    doc.asis(filename_tmp)
    f.write(doc.getvalue())
    
    temp_html_content = """
    </body>
    </html>
    """
    f.write(temp_html_content)
    f.close()
