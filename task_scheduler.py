import os, time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from datetime import datetime
from datetime import timedelta
import sqlite3

delta_2min = timedelta(minutes = 2)

def html_daily():
    os.system("python html-daily.py")

def new_stock_update():
    os.system("python sub_task_new_stock/new_stock_update.py")

def new_move_update():
    os.system("python sub_task_new_movie/new_movie_update.py")

def stock_revenue_high():
    os.system("python DB_management/sub_task_stock_revenue/sub_task_stock_revenue.py")

def stock_volume_update():
    os.system("python DB_management/sub_task_stock_volume/sub_task_stock_daily_volume.py")

def stock_eps_high_update():
    os.system("python DB_management/sub_task_stock_eps/sub_task_stock_eps.py")

def stock_buy_sell_1day():
    os.system("python DB_management/sub_task_stock_buy_sell/sub_task_stock_buy_sell_1day.py")

def stock_gross_margin_high():
    os.system("python DB_management/sub_task_stock_gross_margin/sub_task_stock_gross_margin.py")

def stock_holder_update():
    os.system("python DB_management/sub_task_stock_holder/sub_task_stock_holder.py")

def stock_observation_list_print():
    os.system("python DB_management/sub_task_observe_list/observe_list_operation.py print")


def stock_volume_realtime_update():
    os.system("python DB_management/sub_realtime_volume_update/sub_realtime_volume_update.py")


def index_update():
    os.system("python DB_management/index_update_into_database.py")

def stock_update():
    os.system("python DB_management/stock_data_daily_update.py")

def stock_revenue_update():
    os.system("python DB_management/stock_monthly_revenue_update.py")

def stock_eps_update():
    os.system("python DB_management/stock_data_eps.py")

def stock_gross_margin_update():
    os.system("python DB_management/stock_gross_margin.py")

def stock_capital_amount_update():
    os.system("python DB_management/stock_capital_amount.py")

def stock_buy_sell_update():
    os.system("python DB_management/stock_buy_sell.py")

def stock_holder_update():
    os.system("python DB_management/stock_holder.py")

def stock_data_MA_MACD_computation():
    os.system("python DB_management/stock_data_MA_MACD_computation.py")

sched = BackgroundScheduler()
sched.add_job(html_daily, 'interval', minutes = 28, id = '001', next_run_time = datetime.now() + delta_2min, max_instances = 1)
sched.add_job(new_stock_update, 'cron', day_of_week='mon-sun', hour='0,12', id = '002', max_instances = 1)
sched.add_job(new_move_update, 'cron', day_of_week='mon-sun', hour='8', id = '003', max_instances = 1)
sched.add_job(stock_revenue_high, 'cron', day='1-13', hour='9,12,15,18,21', minute = '30', id = '004', max_instances = 1)
sched.add_job(stock_volume_update, 'cron', day_of_week='mon-fri', hour='6,15,16,17,20', minute = '15', id = '005', max_instances = 1)
sched.add_job(stock_eps_high_update, 'cron', hour='22,8', minute = '15', id = '006', max_instances = 1)
sched.add_job(stock_buy_sell_1day, 'cron', day_of_week='mon-fri', hour='6,15,16,17,20', minute = '40', id = '007', max_instances = 1)
sched.add_job(stock_gross_margin_high, 'cron', hour='22,8', minute = '15', id = '008', max_instances = 1)
sched.add_job(stock_holder_update, 'cron', day_of_week='mon', hour='4,5', minute = '15', id = '009', max_instances = 1)
sched.add_job(stock_observation_list_print, 'cron', day_of_week='mon-sun', hour='17,18,22,05', id = '010', max_instances = 1)

sched.add_job(stock_volume_realtime_update, 'cron', day_of_week='mon-fri', hour='9-14', minute = '0,10,20,30,40,50', id = 'realtime-01', max_instances = 1)

sched.add_job(index_update, 'cron', day_of_week='mon-fri', hour='6,15,16,18,21', id = 'DB_001', max_instances = 1)
sched.add_job(stock_update, 'cron', day_of_week='mon-fri', hour='6,15,16,17,20', id = 'DB_002', max_instances = 1)
sched.add_job(stock_revenue_update, 'cron', day='1-13', hour='9,12,15,18,21', id = 'DB_003', max_instances = 1)
sched.add_job(stock_eps_update, 'cron', hour='22,8', id = 'DB_004', max_instances = 1)
sched.add_job(stock_gross_margin_update, 'cron', hour='22,8', minute = '15', id = 'DB_005', max_instances = 1)
#sched.add_job(stock_capital_amount_update, 'cron', day_of_week='sat', hour='10', id = 'DB_006', max_instances = 1)
sched.add_job(stock_buy_sell_update, 'cron', day_of_week='mon-fri', hour='6,15,16,17,20', minute = '30', next_run_time = datetime.now(), id = 'DB_007', max_instances = 1)
sched.add_job(stock_holder_update, 'cron', day_of_week='sat-sun', hour='3,4,5', minute = '0,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57', id = 'DB_008', max_instances = 1)
sched.add_job(stock_data_MA_MACD_computation, 'cron', day_of_week='mon-fri', hour='6,15,16,17,20', minute = '20', id = 'DB_009', max_instances = 1)
sched.start()

while 1:
    print(sched.get_job('001'))
    print(sched.get_job('002'))
    print(sched.get_job('003'))
    print(sched.get_job('004'))
    print(sched.get_job('005'))
    print(sched.get_job('006'))
    print(sched.get_job('007'))
    print(sched.get_job('008'))
    print(sched.get_job('009'))
    print(sched.get_job('010'))
    print(sched.get_job('realtime-01'))
    print(sched.get_job('DB_001'))
    print(sched.get_job('DB_002'))
    print(sched.get_job('DB_003'))
    print(sched.get_job('DB_004'))
    print(sched.get_job('DB_005'))
    print(sched.get_job('DB_006'))
    print(sched.get_job('DB_007'))
    print(sched.get_job('DB_008'))
    print(sched.get_job('DB_008'))
    time.sleep(100)