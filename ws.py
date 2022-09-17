import requests
from bs4 import BeautifulSoup as bs
from email.mime.text import MIMEText
import smtplib
import time
from datetime import datetime
import config


def read_count():
    f = open("count.txt", "r")
    count = f.read(1)
    if count == '': count = 0   
    f.close()
    return int(count)


def sum_count(value):
    f = open("count.txt", "w")
    f.write(str(value))
    f.close()


def get_content(url, num_tracking):
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
        response = requests.get(url + num_tracking, timeout=5, headers=headers)        
        if response.status_code != 200:
            print("error in get source data")
    except requests.exceptions.ReadTimeout: 
        pass

    html = response.content
    content = bs(html, 'html.parser')
    return content  


def send_email(messages):
    email_message = MIMEText(messages)
    email_message['Subject'] = "Rastreio do tracking " + config.num_tracking + " atualizado"
    email_message['From'] = config.email_sender
    email_message['To'] = config.email_receivers

    email_user = config.email_smtp_user
    email_app_password = config.email_smtp_password
    sent_from = config.email_sender
    sent_to = config.email_receivers
    email_message = email_message.as_string()

    try:
        server = smtplib.SMTP_SSL(config.email_smtp_host, config.email_smtp_port)
        server.ehlo()
        server.login(email_user, email_app_password)
        server.sendmail(sent_from, sent_to, email_message)
        server.close()

        print('E-mail enviado!|', datetime.now().strftime('%d/%m/%Y %H:%M'))
    except Exception as exception:
        print("Error: %s!\n\n" % exception) 


def get_messages(content):
    messages = ''
    c = 0
    count_events = read_count()
    rows = content.select('tr[style="font-family:Verdana,Arial; font-size:10px; text-decoration:none; color:black;"]')    

    for r in rows:
        row = str(r.findAll("td")) 

        message = row.replace('<td align="left" valign="top">', "") \
            .replace('<b>', "") \
            .replace("</b>", "") \
            .replace("</td>", "") \
            .replace("<br/>", "") \
            .replace("\n", "") \
            .strip()            
        
        c = c + 1

        messages = messages + message + "\n"
    
    if (c > count_events):
        send_email(messages)
        sum_count(c)
    else:
        print('Sem atualização |', datetime.now().strftime('%d/%m/%Y %H:%M'))


while True:
    content = get_content(config.url, config.num_tracking)
    get_messages(content)

    time.sleep(config.interval)         
