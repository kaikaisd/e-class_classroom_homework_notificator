import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sqlite3
from sqlite3 import Error
import platform
import pathlib
import os

# OS PATH FEGURATION
if platform.system() == "Windows":
    path = pathlib.Path().absolute()
else:
    path = None
file = str(path)+r"\data.db"
# ---- EOF OS PATH FEGURATION ----

#Funcion

def first_time_run():
    sql_table = """ CREATE TABLE record (
        id integer PRIMARY KEY AUTOINCREMENT,
        work text NOT NULL,
        link text NOT NULL UNIQUE,
        type text NOT NULL,
        start_date text NOT NULL,
        deadline text NOT NULL,
        status text NOT NULL
    ); """
    conn = None
    try:
        conn = sqlite3.connect(file)
        c = conn.cursor()
        c.execute(sql_table)
    except Error as e:
        print(e)
        print("\n發生錯誤")
        exit()
    finally:
        conn.commit()
        if conn:
            conn.close()

def select(argument = "*"):
    return "SELECT "+str(argument)+" FROM record"

def insert(arg_1, arg_2):
    return "INSERT INTO record ("+str(arg_1)+") VALUES ("+str(arg_2)+")"

def delete(argument):
    return "DELETE FROM record SET"+str(argument)

def update(argument,condi):
    return "UPDATE record SET "+str(argument)+" WHERE "+str(condi)
    
def sql_func(action, cont_1, cont_2):
    switch = {
        "select": select(cont_1),
        "insert": insert(cont_1,cont_2),
        "update": update(cont_1,cont_2),
        "delete": delete(cont_1)
    }
    sql = switch.get(action, "ERROR")
    conn = None
    if sql == "ERROR":
        print("程式錯誤,請聯繫程式員修復")
        exit()
    else:
        conn = sqlite3.connect(file)
        c = conn.cursor()
        try:
            c.execute(sql)
        except Error as e:
            e
        finally:
            conn.commit()
    conn.close()

def telegram_notification(msg):
    patt = """
    你好,本週有的功課為 : 
    
    """
    server = smtplib.SMTP('MAIL_SERVER', 587)
    server.starttls()
    server.login("SENDER_MAIL", "PASSWORD")
    server.sendmail("SENDER_MAIL", "RECIEVER_MAIL", patt)
    server.quit()

# ---- EOF function ----

#Run
print("""
=================================================
|                                               |
|          eclass Homework Noticificator        |
|                  Version: 0.1                 |
|               Coded by kaikaisd               |
|                                               |
|          此程式並不能免去你再次登入的歩驟        |
|             請配合使用瀏覽器外掛腳本            |
=================================================

外掛腳本 : https://gist.github.com/kaikaisd/1853f5c826993966051627174beb8874
"""+"\n")

#inputs
print('請輸入你登入後的SESSION字串\n')
session= input('PHPSESSID=')
while len(session) != 26 or type(session) != str:
    print("你輸入的session有誤,請重新輸入")
    time.sleep(3)
    session= str(input('PHPSESSID='))
str(session)

print('\n請輸入你想讀取的eclass教室號碼,例: 20111\n')
classroom= input('javascript:fe_eclass('XXXXX')=')
while len(classroom) != 5 or type(classroom) != str:
    print("你輸入的eclass教室號碼無效,請重新輸入")
    time.sleep(3)
    session= input('eclassXX=')
str(classroom)

if "data.db" not in os.listdir():
    first_time_run()

#General Setting
req_time=0 
cookies = {}
table_data = []
headers = {
    'Cache-Control': 'no-cache',    
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}
cookies['PHPSESSID']=str(session)


#runtime
while True:
    #try session is good to go
    test_req_home = requests.get('https://eclass.choinong.edu.mo/home/index.php',headers=headers,cookies=cookies)
    test_req_room = requests.get('https://eclass.choinong.edu.mo/home/eLearning/login.php?uc_id='+str(classroom),headers=headers,cookies=cookies)
    if test_req_home.ok and test_req_room.ok:
        #go through
        while True:
            call = requests.get('https://eclass.choinong.edu.mo/eclass40/src/assessment/assessment.php',headers=headers,cookies=cookies)
            req_time+=1
            call.encoding = call.apparent_encoding
            soup = BeautifulSoup(call.text, "html5lib")
            for idx,tr in enumerate(soup.find_all('tr', {'class':'normal record_level_top'})):
                tds = tr.find_all('td')
                a_tag = tr.find('a',href = True).get('href')
                sql_func("insert","work,link,type,start_date,deadline,status","'"+str(tds[1].find('a').contents[0])+"','"+str('https://eclass.choinong.edu.mo'+str(a_tag))+"','"+str(tds[2].contents[0])+"','"+str(tds[4].contents[0])+"','"+str(tds[5].find('span').contents[0])+"','"+str(1 if tds[6].contents[0] == '進行中' else (-1 if tds[6].contents[0] == '已逾期' else 0))+"'")
            print("已向伺服器請求了 "+str(req_time)+" 次  時間: "+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            time.sleep(5)
    else:
        print("此SESSION已經失效或eclass房間有誤,請重啟此程序並再次登入eclass獲取新的session並再執行本程序")
        break
