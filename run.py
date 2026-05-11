import os
import pandas as pd
import configparser
from datetime import datetime, timedelta
import time
import yfinance as yf
from pgdb import PGDatabase

dirname = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read(os.path.join(dirname, 'config.ini'))
#print(config['Files']['sales_path'])

companies = eval(config['Companies']['companies'])
database_creds = config['Database']

sales_path = config['Files']['sales_path']

sales_df = pd.DataFrame()
if os.path.exists(sales_path):
    sales_df = pd.read_csv(sales_path)
    #print(sales_df)
    os.remove(sales_path)


historical_list = []

start_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')

for company in companies:
    try:
        df = yf.download(
            company,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=False
        ).reset_index()

        if df.empty:
            #print(f"{company}: данных нет")
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.rename(columns={
            "Date": "index",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adjclose",
            "Volume": "volume"
        })

        df["ticker"] = company

        df = df[["index", "open", "high", "low", "close", "adjclose", "volume", "ticker"]]

        historical_list.append(df)

        #print(f"{company}: OK")

    except Exception as e:
        print(f"{company} ERROR: {e}")


historical_df = pd.concat(historical_list, ignore_index=True)

database = PGDatabase(
    host = database_creds['HOST'],
    port = database_creds['PORT'],
    database=database_creds['DATABASE'],
    user = database_creds['USER'],
    password=database_creds['PASSWORD']
)

for i , row in sales_df.iterrows():
    query = f"insert into sales values ('{row['dt']}', '{row['company']}', '{row['transaction_type']}', {row['amount']})"
    print(query)
    database.post(query)

for i, row in historical_df.iterrows():
    query = f"insert into stock values ('{row['index']}', '{row['ticker']}', {row['open']}, {row['close']})"
    database.post(query)
