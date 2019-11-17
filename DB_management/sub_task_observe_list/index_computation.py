
#MA有向上
def MA_direction_today(table_input, MA_num, offset, c):
    sql_cmd = 'SELECT max(rowid) FROM ' + table_input
    c.execute(sql_cmd)
    rowid = c.fetchone()
    if rowid != None:
        sql_cmd = 'select MA' + str(MA_num) + ' from ' + table_input  + ' where rowid =' + str(rowid[0] - offset)
        c.execute(sql_cmd)
        ma_temp0 = c.fetchone()
        sql_cmd = 'select MA' + str(MA_num) + ' from ' + table_input  + ' where rowid =' + str(rowid[0] - 1 - offset)
        c.execute(sql_cmd)
        ma_temp1 = c.fetchone()
        if (ma_temp0[0] == None) or (ma_temp1[0] == None):
            return False
        if (ma_temp0[0] >= ma_temp1[0]):
            return True
        else:
            return False

#回傳扣抵值以收盤價%數表示
def MA_twist_prediction_today(table_input, MA_num, c):
    sql_cmd = 'SELECT max(rowid) FROM ' + table_input
    c.execute(sql_cmd)
    rowid = c.fetchone()
    if (rowid != None):
        if (rowid[0] - MA_num) > 0:
            sql_cmd = 'select close_price from ' + table_input  + ' where rowid =' + str(rowid[0])
            c.execute(sql_cmd)
            ma_temp0 = c.fetchone()
            sql_cmd = 'select close_price from ' + table_input  + ' where rowid =' + str(rowid[0] - MA_num + 1)
            c.execute(sql_cmd)
            close_index = c.fetchone()
            gap = ((close_index[0] - ma_temp0[0])/ma_temp0[0])
            return gap


#扭轉MA向上
def MA_twist_today(table_input, MA_num, c):
    sql_cmd = 'SELECT max(rowid) FROM ' + table_input
    c.execute(sql_cmd)
    rowid = c.fetchone()
    if rowid != None:
        if (rowid[0] - MA_num) > 0:
            sql_cmd = 'select MA' + str(MA_num) + ' from ' + table_input  + ' where rowid =' + str(rowid[0])
            c.execute(sql_cmd)
            ma_temp0 = c.fetchone()
            sql_cmd = 'select MA' + str(MA_num) + ' from ' + table_input  + ' where rowid =' + str(rowid[0] - 1)
            c.execute(sql_cmd)
            ma_temp1 = c.fetchone()
            sql_cmd = 'select MA' + str(MA_num) + ' from ' + table_input  + ' where rowid =' + str(rowid[0] - 2)
            c.execute(sql_cmd)
            ma_temp2 = c.fetchone()
            if (ma_temp0[0] == None) or (ma_temp1[0] == None) or (ma_temp2[0] == None):
                return 0
            if (ma_temp0[0] >= ma_temp1[0]) and (ma_temp1[0]<=ma_temp2[0]):
                return 1
            elif (ma_temp0[0] <= ma_temp1[0]) and (ma_temp1[0]>=ma_temp2[0]):
                return 2
            else:
                return 0

#MA乖離
def MA_distance_today(table_input, MA_num, c):
    sql_cmd = 'SELECT max(rowid) FROM ' + table_input
    c.execute(sql_cmd)
    rowid = c.fetchone()
    if rowid != None:
        sql_cmd = 'select MA' + str(MA_num) + ' from ' + table_input  + ' where rowid =' + str(rowid[0])
        c.execute(sql_cmd)
        ma_temp0 = c.fetchone()
        sql_cmd = 'select close_price from ' + table_input  + ' where rowid =' + str(rowid[0])
        c.execute(sql_cmd)
        close_price_temp0 = c.fetchone()
        if (ma_temp0[0] == None) or (close_price_temp0[0] == None):
            return 0
        else:
            result = (close_price_temp0[0] - ma_temp0[0]) / close_price_temp0[0]
            result = round(result*100, 2)
            return result

#MACD方向
def MACD_direction_today(table_input, c):
    sql_cmd = 'SELECT max(rowid) FROM ' + table_input
    c.execute(sql_cmd)
    rowid = c.fetchone()
    if rowid != None:
        sql_cmd = 'select MACD_DIFF from ' + table_input  + ' where rowid =' + str(rowid[0])
        c.execute(sql_cmd)
        macd_temp0 = c.fetchone()
        sql_cmd = 'select MACD_DIFF from ' + table_input  + ' where rowid =' + str(rowid[0] - 1)
        c.execute(sql_cmd)
        macd_temp1 = c.fetchone()
        if (macd_temp0[0] == None) or (macd_temp1[0] == None):
            return 0
        if (macd_temp0[0] >= macd_temp1[0]):
            return 1
        else:
            return 0

#MACD轉折
def MACD_twist_today(table_input, c):
    sql_cmd = 'SELECT max(rowid) FROM ' + table_input
    c.execute(sql_cmd)
    rowid = c.fetchone()
    if rowid != None:
        sql_cmd = 'select MACD_DIFF from ' + table_input  + ' where rowid =' + str(rowid[0])
        c.execute(sql_cmd)
        macd_temp0 = c.fetchone()
        sql_cmd = 'select MACD_DIFF from ' + table_input  + ' where rowid =' + str(rowid[0] - 1)
        c.execute(sql_cmd)
        macd_temp1 = c.fetchone()
        sql_cmd = 'select MACD_DIFF from ' + table_input  + ' where rowid =' + str(rowid[0] - 2)
        c.execute(sql_cmd)
        macd_temp2 = c.fetchone()
        if (macd_temp0[0] == None) or (macd_temp1[0] == None) or (macd_temp2[0] == None):
            return 0
        if (macd_temp0[0] >= macd_temp1[0]) and (macd_temp1[0]<=macd_temp2[0]):
            return 1
        elif (macd_temp0[0] <= macd_temp1[0]) and (macd_temp1[0]>=macd_temp2[0]):
            return 2
        else:
            return 0
