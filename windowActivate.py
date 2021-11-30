# coding=utf-8
# @Author : 松柏长青
# @email : qiubaishen@qq.com。
# @about : window激活工具目前只支持windows10。
import hashlib
import json
import os
import smtplib
import sqlite3
import sys
import threading
import time
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from tkinter.messagebox import *
from urllib.request import *


def ui(sofware_version):
    """ui界面。"""
    os.system(f'title window10激活工具绿色版{sofware_version}')
    print(""" 
              ,.—-.               .—-, 
             /::.  /'\\            '//'\  .:'\ 
            '|::.  |\\ \\.-—---.// //|   .:| 
            '|::.  |/,.—-,   ,.—-,!|   .:| 
             `·--·´;      '; ;       ';`·--·´ 
                  ';       ; ;       '; 
                   `.  @'; ;@  .´ 
                 .·´¯¯¯(`¯´)¯¯¯`·. 
                '; ·.·    ¯Y¯   ·.· '; 
                 `·.____/'\___¸.·´ 
                       # \_____/      
                          ')=(            ,._,._,._,.__,._,. 
                    . · ´      ` · .     (  by qiubaishen  ) 
                  ,'  '; .·´¨¨`·.  ;  ',    `'`¯`'`¯`'`¯`'` 
                  `· .; ;       ; ;. ·´ 
                    (¯¯`.__¸.´¯¯) 
         /¯'/¯/¯¯¯`'   \¸__/     '´¯¯'\¯\¯\ 
         \_\_\_______) (_______/_/_/ 
 ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯˜¤¹""")
    print('window10 激活工具'.center(50, '='))


def update_program(url):
    try:
        os.mkdir(os.getcwd() + '\\temp')
        urlretrieve(url=url, filename=fr'{os.getcwd()}\temp\windowActivate.exe')
        global update_flag, program_flag
        update_flag = True
        program_flag = True
    except:
        global fail_update
        fail_update = True


def send_fali_email(sender, receiver, error_keys, password):
    """发送失败信息。"""
    message = MIMEMultipart()
    message['From'] = '<%s>' % sender
    message['To'] = '<%s>' % receiver
    subject = 'windows 密钥激活失败！'
    message['Subject'] = Header(subject, 'utf-8')
    with open('error.txt', 'w') as f:
        json.dump(obj=error_keys, fp=f)
    with open('error.txt', 'rb') as f:
        alt = MIMEApplication(f.read())
        alt.add_header('Content-Disposition', 'attachment', filename='失效密钥.txt')
    message.attach(alt)
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.qq.com', 25)
        smtpObj.login(user=sender, password=password)
        smtpObj.sendmail(sender, receiver, message.as_string())
    except Exception:
        showerror(title='发送失败', message='发送失败，请检查网络连接！')
    finally:
        os.remove(os.getcwd() + '\\error.txt')


update_flag = False
program_flag = False
fail_update = False

if not os.path.exists(os.getcwd() + '\\data'):
    showwarning(title='错误', message='无法启动程序,缺少data文件！')
    exit(0)
os.rename(os.getcwd() + '\\data', os.getcwd() + '\\data.sqlite3')

conn = sqlite3.connect(database='./data.sqlite3', )
cur = conn.cursor()
try:
    cur.execute('create table if not exists keys(key Text,flag INTEGER default 1)')
    cur.execute('create table if not exists serverconfig(email Text,serverip Text,id INTEGER default 1)')
    conn.commit()
    cur.execute('select key from keys where flag=1')
    keys = cur.fetchall()
    keys = [key[0] for key in keys]
    cur.execute('select * from serverconfig')
    serverconfig = cur.fetchone()
    email, password, serverip, version = serverconfig
    program_update_url = serverip + '/update?token=' + hashlib.md5(
        password.encode()).hexdigest() + f'&version={version}'
    db_update_url = serverip + '/getkeys?token=' + hashlib.md5(password.encode()).hexdigest()
    get_version_url = serverip + '/getversion?token=' + hashlib.md5(password.encode()).hexdigest()
    insert_sql = 'insert into keys (key,flag) values'
    ui(version)
    # 检查程序更新。

    try:
        res = urlopen(url=get_version_url, timeout=15)
        server_version = json.loads(res.read().decode('utf-8'))
        if server_version[-1] != version:
            cur.execute(f"update serverconfig set id='{server_version[-1]}'")
            conn.commit()
            update_thread = threading.Thread(target=update_program, args=(program_update_url,), name='应用更新线程')
            update_thread.daemon = False
            update_thread.start()
            sys.stdout.writelines('正在更新程序。。。\n')
            strarrs = ['/', '|', '\\']
            for i in range(0, 100, 10):
                sys.stdout.write(strarrs[i % 3] + '{}/100:'.format(i + 1) + '#' * i + '\r')
                sys.stdout.flush()
                time.sleep(3)
                while not update_flag and i == 80:
                    if fail_update:
                        break
            os.system('cls')
            ui(version)
            if fail_update:
                print('更新失败，请检查网络连接！')
            else:
                print('更新完成!')
                showinfo(title='提示', message='更新完成，将重新启动程序！')


    except Exception:
        pass

    if program_flag:
        with open('move.bat', 'w') as f:
            text = [f'@move /y {os.getcwd()}\\temp\\windowActivate.exe {os.getcwd()}\\windowActivate.exe\n',
                    f'@rmdir /s/q {os.getcwd()}\\temp\n', f'@start {os.getcwd()}\\windowActivate.exe\n', '@exit\n']
            f.writelines(text)
        os.system('@start move.bat')
        sys.exit(0)

    # 更新密钥数据库。
    try:
        res = urlopen(url=db_update_url, timeout=15)
        new_keys = json.loads(res.read().decode('utf-8'))
        cur.execute('select key from keys')
        com_keys = cur.fetchall()
        com_keys = [key[0] for key in com_keys]
        new_keys = list(set(new_keys) - set(com_keys))
        if len(new_keys) > 0:
            for k in new_keys:
                insert_sql += "('%s',1)," % k
            keys.extend(new_keys)
            insert_sql = insert_sql[:-1]
            cur.execute(insert_sql)
            conn.commit()
            strarrs = ['/', '|', '\\']
            sys.stdout.writelines('正在更新资源。。。\n')
            for i in range(0, 100, 20):
                sys.stdout.write(strarrs[i % 3] + '{}/100:'.format(i + 1) + '#' * i + '\r')
                sys.stdout.flush()
                time.sleep(1)
            os.system('cls')
            ui(version)
    except Exception as e:
        pass

    update_sqls = []
    i = 0
    if len(keys) == 0:
        showinfo(title='提示', message='由于作者长时间没维护接口，系统接口已经失效！系统将发送信息告知作者进行修复，请耐心等待！')
        cur.execute('select key from keys where flag=0')
        error_keys = cur.fetchall()
        error_keys = [key[0] for key in error_keys]
        send_fali_email(email, email, error_keys, password)
        sys.exit(0)
    isactivate = askyesno(title='提示', message='是否需要激活windows?')
    if not isactivate:
        sys.exit(0)
    for key in keys:
        print('第%d次激活尝试。。。' % (i + 1))
        os.system('slmgr.vbs /upk')
        os.system('slmgr /ipk %s' % key)
        os.system('lmgr /skms zh.us.to')
        os.system('slmgr /ato')
        isactivate = askyesno(title='继续激活', message='是否已经成功激活?')
        if isactivate:
            os.system('cls')
            ui(version)
            print('windows已成功激活!')
            break
        else:
            update_sqls.append("update keys set flag=0 where key='%s'" % key)
        os.system('cls')
        ui(version)
        i += 1
    if i == (len(keys)):
        os.system('cls')
        ui(version)
        print('windows激活失败!')
        sendflag = askyesno(title='帮助与改进', message='是否发送失败信息给作者?')
        if sendflag:
            send_fali_email(email, email, keys, password)

    if len(update_sqls) > 0:
        for update_sql in update_sqls:
            cur.execute(update_sql)
        conn.commit()
        pass

except Exception as e:
    pass
finally:
    cur.close()
    conn.close()
    os.rename(os.getcwd() + '\\data.sqlite3', os.getcwd() + '\\data')
