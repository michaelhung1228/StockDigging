
def MA_computation(table_input, Start_date, End_date, delta_1day, c, conn, is_stock):
    MA_list = [3,6,18,54,108,216]
    for mean_average in MA_list:
        Start_date_ptr = Start_date
        while Start_date_ptr <= End_date:
            cur_date_str = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
            sql_cmd = 'select rowid from ' + table_input + ' where date_ID =\'' + cur_date_str + '\''
            c.execute(sql_cmd)
            rowid = c.fetchone()
            if rowid != None:
                #print(str(rowid[0]) + ' ' + cur_date_str)
                total = 0.0
                for i in range(mean_average):
                    #print(i)
                    if rowid[0] < mean_average:
                        break
                    if is_stock:
                        sql_cmd = 'select close_price from ' + table_input + ' where rowid =' + str(rowid[0] - i)
                    else:
                        sql_cmd = 'select close_index from ' + table_input + ' where rowid =' + str(rowid[0] - i)
                    #print(sql_cmd)
                    c.execute(sql_cmd)
                    total = total + c.fetchone()[0]
                    #print(total)
                if rowid[0] < mean_average:
                    Start_date_ptr = Start_date_ptr + delta_1day
                    continue
                total = total / mean_average
                print(str(rowid[0]) + ' ' + cur_date_str + ' ' + str(total))
                sql_cmd = 'UPDATE ' + table_input + ' set MA' + str(mean_average) + '=' + str(total) + ' where rowID =' + str(rowid[0])
                #print(sql_cmd)
                c.execute(sql_cmd)
                conn.commit()
            Start_date_ptr = Start_date_ptr + delta_1day

def MACD_computation(table_input, Start_date, End_date, delta_1day, c, conn, is_stock):
    Start_date_ptr = Start_date
    # DI computation
    while Start_date_ptr <= End_date:
        cur_date_str = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
        sql_cmd = 'select rowid from ' + table_input + ' where date_ID =\'' + cur_date_str + '\''
        c.execute(sql_cmd)
        rowid = c.fetchone()
        if rowid != None:
            if is_stock:
                sql_cmd = 'select highest_price from ' + table_input + ' where rowid =' + str(rowid[0])
            else:
                sql_cmd = 'select highest_index from ' + table_input + ' where rowid =' + str(rowid[0])
            c.execute(sql_cmd)
            highest_index = c.fetchone()[0]
            if is_stock:
                sql_cmd = 'select lowest_price from ' + table_input + ' where rowid =' + str(rowid[0])
            else:
                sql_cmd = 'select lowest_index from ' + table_input + ' where rowid =' + str(rowid[0])
            c.execute(sql_cmd)
            lowest_index = c.fetchone()[0]
            if is_stock:
                sql_cmd = 'select close_price from ' + table_input + ' where rowid =' + str(rowid[0])
            else:
                sql_cmd = 'select close_index from ' + table_input + ' where rowid =' + str(rowid[0])
            c.execute(sql_cmd)
            close_index = c.fetchone()[0]
            DI = (highest_index + lowest_index + close_index*2)/4
            sql_cmd = 'UPDATE ' + table_input + ' set DI =' + str(DI) + ' where rowID =' + str(rowid[0])
            c.execute(sql_cmd)
            conn.commit()
        Start_date_ptr = Start_date_ptr + delta_1day
    #EMA12 computation
    Start_date_ptr = Start_date
    while Start_date_ptr <= End_date:
        cur_date_str = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
        sql_cmd = 'select rowid from ' + table_input + ' where date_ID =\'' + cur_date_str + '\''
        c.execute(sql_cmd)
        rowid = c.fetchone()
        if rowid != None:
            sql_cmd = 'select EMA12 from ' + table_input + ' where rowid =' + str(rowid[0] - 1)
            c.execute(sql_cmd)
            EMA12_preday = c.fetchone()
            print(EMA12_preday)
            if (EMA12_preday != None) and (EMA12_preday[0] != None):
                sql_cmd = 'select DI from ' + table_input + ' where rowid =' + str(rowid[0])
                c.execute(sql_cmd)
                DI = c.fetchone()[0]
                EMA12 = (EMA12_preday[0]*11 + DI*2)/13
                sql_cmd = 'UPDATE ' + table_input + ' set EMA12 =' + str(EMA12) + ' where rowID =' + str(rowid[0])
                c.execute(sql_cmd)
                conn.commit() 
                print(EMA12)
            else:
                if rowid[0] < 12:
                    Start_date_ptr = Start_date_ptr + delta_1day
                    continue
                DI_total = 0.0
                for i in range(12):
                    sql_cmd = 'select DI from ' + table_input + ' where rowid =' + str(rowid[0] - i)
                    print(sql_cmd)
                    c.execute(sql_cmd)
                    DI_total = DI_total + c.fetchone()[0]
                DI_total = DI_total/12
                sql_cmd = 'UPDATE ' + table_input + ' set EMA12 =' + str(DI_total) + ' where rowID =' + str(rowid[0])
                c.execute(sql_cmd)
                conn.commit()            
        Start_date_ptr = Start_date_ptr + delta_1day
    #EMA26 computation
    Start_date_ptr = Start_date
    while Start_date_ptr <= End_date:
        cur_date_str = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
        sql_cmd = 'select rowid from ' + table_input + ' where date_ID =\'' + cur_date_str + '\''
        c.execute(sql_cmd)
        rowid = c.fetchone()
        if rowid != None:
            sql_cmd = 'select EMA26 from ' + table_input + ' where rowid =' + str(rowid[0] - 1)
            c.execute(sql_cmd)
            EMA26_preday = c.fetchone()
            print(EMA26_preday)
            if (EMA26_preday != None) and (EMA26_preday[0] != None):
                sql_cmd = 'select DI from ' + table_input + ' where rowid =' + str(rowid[0])
                c.execute(sql_cmd)
                DI = c.fetchone()[0]
                EMA26 = (EMA26_preday[0]*25 + DI*2)/27
                sql_cmd = 'UPDATE ' + table_input + ' set EMA26 =' + str(EMA26) + ' where rowID =' + str(rowid[0])
                c.execute(sql_cmd)
                conn.commit() 
                print(EMA26)
            else:
                if rowid[0] < 26:
                    Start_date_ptr = Start_date_ptr + delta_1day
                    continue
                DI_total = 0.0
                for i in range(26):
                    sql_cmd = 'select DI from ' + table_input + ' where rowid =' + str(rowid[0] - i)
                    c.execute(sql_cmd)
                    DI_total = DI_total + c.fetchone()[0]
                DI_total = DI_total/26
                sql_cmd = 'UPDATE ' + table_input + ' set EMA26 =' + str(DI_total) + ' where rowID =' + str(rowid[0])
                c.execute(sql_cmd)
                conn.commit()            
        Start_date_ptr = Start_date_ptr + delta_1day
    #MACD_12_26 computation
    Start_date_ptr = Start_date
    while Start_date_ptr <= End_date:
        cur_date_str = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
        sql_cmd = 'select rowid from ' + table_input + ' where date_ID =\'' + cur_date_str + '\''
        c.execute(sql_cmd)
        rowid = c.fetchone()
        if rowid != None:
            sql_cmd = 'select EMA26 from ' + table_input + ' where rowid =' + str(rowid[0])
            c.execute(sql_cmd)
            EMA26 = c.fetchone()
            sql_cmd = 'select EMA12 from ' + table_input + ' where rowid =' + str(rowid[0])
            c.execute(sql_cmd)
            EMA12 = c.fetchone()
            if (EMA26 != None) and (EMA26[0] != None) and (EMA12 != None) and (EMA12[0] != None):
                MACD_12_26 = EMA12[0] - EMA26[0]
                sql_cmd = 'UPDATE ' + table_input + ' set MACD_12_26 =' + str(MACD_12_26) + ' where rowID =' + str(rowid[0])
                print(sql_cmd)
                c.execute(sql_cmd)
                conn.commit()
        Start_date_ptr = Start_date_ptr + delta_1day
    
    #MACD9 and MACD diff computation
    
    Start_date_ptr = Start_date
    while Start_date_ptr <= End_date:
        cur_date_str = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
        sql_cmd = 'select rowid from ' + table_input + ' where date_ID =\'' + cur_date_str + '\''
        c.execute(sql_cmd)
        rowid = c.fetchone()
        if rowid != None:
            sql_cmd = 'select MACD_9 from ' + table_input + ' where rowid =' + str(rowid[0] - 1)
            c.execute(sql_cmd)
            MACD_9_pre = c.fetchone()
            print(MACD_9_pre)
            if (MACD_9_pre != None) and (MACD_9_pre[0] != None):
                sql_cmd = 'select MACD_12_26 from ' + table_input + ' where rowid =' + str(rowid[0])
                c.execute(sql_cmd)
                MACD_12_26 = c.fetchone()[0]
                MACD_9 = (MACD_9_pre[0]*8 + MACD_12_26*2)/10
                sql_cmd = 'UPDATE ' + table_input + ' set MACD_9 =' + str(MACD_9) + ' where rowID =' + str(rowid[0])
                c.execute(sql_cmd)
                conn.commit()
                MACD_DIFF = MACD_12_26 - MACD_9
                sql_cmd = 'UPDATE ' + table_input + ' set MACD_DIFF =' + str(MACD_DIFF) + ' where rowID =' + str(rowid[0])
                c.execute(sql_cmd)
                conn.commit()
                print(sql_cmd)
            else:
                if rowid[0] < 34: #the first day we can have MACD9 value is the 34th day
                    Start_date_ptr = Start_date_ptr + delta_1day
                    continue
                MACD_12_26_total = 0.0
                for i in range(9):
                    sql_cmd = 'select MACD_12_26 from ' + table_input + ' where rowid =' + str(rowid[0] - i)
                    c.execute(sql_cmd)
                    MACD_12_26_total = MACD_12_26_total + c.fetchone()[0]
                MACD_12_26_total = MACD_12_26_total/9
                sql_cmd = 'UPDATE ' + table_input + ' set MACD_9 =' + str(MACD_12_26_total) + ' where rowID =' + str(rowid[0])
                c.execute(sql_cmd)
                conn.commit()
                sql_cmd = 'select MACD_12_26 from ' + table_input + ' where rowid =' + str(rowid[0])
                c.execute(sql_cmd)            
                MACD_DIFF = c.fetchone()[0] - MACD_12_26_total
                sql_cmd = 'UPDATE ' + table_input + ' set MACD_DIFF =' + str(MACD_DIFF) + ' where rowID =' + str(rowid[0])
                c.execute(sql_cmd)
                conn.commit()
        Start_date_ptr = Start_date_ptr + delta_1day
