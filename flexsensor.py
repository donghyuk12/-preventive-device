import gspread
import time
import datetime
import spidev
import paho.mqtt.client as mqtt
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import math
from twilio.rest import Client

account_sid = 'AC2eb1b1137ab55e6d13d969e988a02e7f'
auth_token = 'dd9c6ccef49406c2d1119cc3ae0de07c'
client = Client(account_sid, auth_token)

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
]
json_file_name = 'flexsensor-ec0c2fedab42.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1GfW_IFz1P8sm8E2Fx0sWSAdf558tbPLfrRqGYu2ukl4/edit?usp=sharing'
doc = gc.open_by_url(spreadsheet_url)
worksheet = doc.worksheet('flexsensor')
spi=spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz=1350000
count = 0
timecount=0
def adc(channel):
    buff=spi.xfer2([1,(8+channel)<<4,0])
    adcvalue=((buff[1]&3)<<8)+buff[2]
    return adcvalue
mcp3008=0
adcchannel = 0
while True :
    t = time.localtime()
    a_1 = adc(mcp3008)
    print("sensor1 : %d" %(a_1))
    time.sleep(0.5)
    a_2 = adc(adcchannel)
    a_3 = a_1 - a_2
    print(a_3)
    if a_1>50:
        timecount +=1
    if a_3 >50:
        t1 = datetime.now()
        t1ymd = t1.strftime('%Y-%m-%d')
        t1hms = t1.strftime('%H:%M:%S')
        if a_2 < 10 :
            t2 = datetime.now()
            t2ymd = t1.strftime('%Y-%m-%d')
            t2hms = t1.strftime('%H:%M:%S')
            worksheet.append_row([t2ymd, t2hms, "사용"])
    if timecount>20:
        print("위험")
        message = client.messages.create(
            to="+821041293832", 
            from_="+17163207584",
            body="냉장고 문이 안닫혔습니다.")
        worksheet.append_row([t2ymd, t2hms, "위험"])
        timecount=0
        break