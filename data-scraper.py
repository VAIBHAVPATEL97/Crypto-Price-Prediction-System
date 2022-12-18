from countdown import countdown
import pandas as pd
import datetime
import os, requests
import uuid
import dateutil.parser, dateutil.tz as tz

def get_ohlc (pair, interval=1, since='last'):
    endpoint = 'https://api.kraken.com/0/public/OHLC'
    payLoad = {
        'pair':     pair,
        'interval': interval,
        'since' :   since
    }
    response = requests.get(endpoint, payLoad)
    data = response.json()
    OHLC = data['result'][pair]
    data = pd.DataFrame.from_records(OHLC, columns=['Time', 'Open', 'High', 'Low', 'Close', 'vwap', 'volume', 'count'])
    data['Time'] = pd.to_datetime(data['Time'], unit='s')
    data.set_index('Time',inplace=True)
    data = data.drop(['vwap', 'volume', 'count'], axis=1)
    data['Open']  = data.Open.astype(float)
    data['High']  = data.High.astype(float)
    data['Low']   = data.Low.astype(float)
    data['Close'] = data.Close.astype(float)
    return data

def load_data(pair, path):
    data = pd.read_json(path + pair + '.json' , orient='split')
    tmp = data.tail(1).index                    
    tmp = tmp.strftime('%Y-%m-%d %H:%M:%S')     
    dt = str_to_datetime(tmp[0])                
    ts = dt.timestamp()                         
    return data, ts

def str_to_datetime(datestr):
    Y = int(datestr[0:4])
    M = int(datestr[5:7])
    D = int(datestr[8:10])
    H = int(datestr[11:13])
    m = int(datestr[14:16])

    return datetime.datetime(Y, M, D, H, m, 0, tzinfo=tz.gettz("Etc/GMT"))

path = "./data/"
pair = '1INCHEUR'

if os.path.exists(path + pair + '.json') == False:
    data = get_ohlc(pair, 1)                            # 1 minute timeframe
    # data.to_csv(r'C:\Users\User\Desktop\MLops project\Experiments\historical_data\data.csv')
    data.to_json(path + pair + '.json', orient='split')
else:
    data1, ts = load_data(pair, path)
    data2 = get_ohlc(pair, 1, ts)
    data3 = pd.concat([data1, data2])
    data3.drop(data3.tail(1).index,inplace=True) # delete last record because it's not ended
    data3.to_json(path + pair + '.json', orient='split')
