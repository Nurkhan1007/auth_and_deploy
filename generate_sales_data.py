from datetime import datetime, timedelta
import pandas as pd
from random import randint
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

companies = eval(config['Companies']['companies'])

today = datetime.today()

today_weekday = datetime.today().weekday()

yesterday = today - timedelta(days=1)

if 1<=today_weekday<=5:
    d = {
        'dt': [yesterday.strftime('%d-%m-%Y')] * len(companies) * 2,
        'company': companies * 2, 
        'transaction_type': ['buy'] * len(companies) + ['sell'] * len(companies),
        'amount': [randint(0, 1000) for _ in range(len(companies)*2)]
    }
    df = pd.DataFrame(d)
    df.to_csv('sales-data.csv', index=False)
    print('Файл сохранен')