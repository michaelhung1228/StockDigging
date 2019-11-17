import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3
from yattag import Doc
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

time_open = datetime.strptime("09:00", "%H:%M")
time_now = datetime.now()
time_open = time_open.replace(year = time_now.year, month = time_now.month, day = time_now.day)
time_delta = time_now - time_open
print(time_open)
print(time_now)
print(time_delta.total_seconds()/60)