import urllib
import json
import urllib.request
import time
import datetime
import pandas as pd
from Prices import Currency, CurrencyPair



def ToDate(sec):
    textDate = str(time.strftime("%d/%m/%y %H:%M:%S",time.gmtime(sec)))
    date = datetime.datetime.strptime(textDate,"%d/%m/%y %H:%M:%S")
    return date


def JsonToDataFrame(Json, Numbers, type = "ledger"):
    try:
        data = json.loads(Json.read().decode('utf8'))["result"][type]
    except:
        data = Json["result"][type]
    firstKey = list(data.keys())[0]
    Headers = ["id"]
    for key in data[firstKey].keys():
        Headers += [key]
    nColumns = len(Headers)
    arrays = [[] for i in range(nColumns)]
    for key in data.keys():
        arrays[0] += [key]
        item = data[key]
        for i in range(1,nColumns):
            title = Headers[i]
            value = item[title]
            if title in Numbers:
                value = float(value)
                if title == "time":
                    value = datetime.datetime.fromtimestamp(value)
            arrays[i] += [value]
    DF = pd.DataFrame()
    for i in range(nColumns):
        DF[Headers[i]] = arrays[i]
    return DF




#<pair_name> = pair name
#    array of array entries(<time>, <open>, <high>, <low>, <close>, <vwap>, <volume>, <count>)
#last = id to be used as since when polling for new, committed OHLC data
#interval = time frame interval in minutes (optional):
#	1 (default), 5, 15, 30, 60, 240, 1440, 10080, 21600

def OHLC(X = Currency.XBT, Z = Currency.EUR, startDate = datetime.datetime(2000,1,1), freq = 1140):
    DF = pd.DataFrame()
    urlStart = "https://api.kraken.com/0/public/OHLC?"
    pairID = CurrencyPair(X,Z).RequestID
    print(pairID)
    print(urlStart + "pair=" + pairID+ "&interval=" + str(freq))
    print("")
    text = urllib.request.urlopen(urlStart + "pair=" + pairID+ "&interval=" + str(freq))
    data = json.loads(text.read().decode('utf8'))["result"]
    keys = list(data.keys())
    data = data[keys[0]]
    time = []
    open = []
    high = []
    low = []
    close = []
    vwap = []
    volume = []
    count = []
    for info in data:
        date = ToDate(int(info[0]))
        if date > startDate:
            time += [date]
            open += [float(info[1])]
            high += [float(info[2])]
            low += [float(info[3])]
            close += [float(info[4])]
            vwap += [float(info[5])]
            volume += [float(info[6])]
            count += [float(info[7])]
    DF["time"] = time
    DF["open"] = open
    DF["high"] = high
    DF["low"] = low
    DF["close"] = close
    DF["vwap"] = vwap
    DF["volume"] = volume
    DF["count"] = count
    return DF

def ComputeReturns(data, col = "close", title = "return"):
    returns = [0.]
    previous = 0.
    for (index, row) in data.iterrows():
        if index != 0:
            returns += [row[col]/previous - 1]
        previous = row[col]
    data[title] = returns

def ComputePricesPerDay(DF):
    Res = {}
    for (index,row) in DF.iterrows():
        hour = row["time"].hour
        if hour == 0:
            Res[str(row["time"].date())] = {0 : row["open"], -1: row["close"]}
        else:
            try:
                dicoDay = Res[str(row["time"].date())]
                dicoDay[hour] = row["open"]
                dicoDay[-1] = row["close"]
            except:
                print("err")
    DF = pd.DataFrame()
    List_keys = []
    time = []
    data = {}
    data_len = 10000000
    for date in Res.keys():
        time += [date]
        ResDate = Res[date]
        if len(List_keys) == 0:
            for k in ResDate.keys():
                if k != 0:
                    List_keys += [k]
                    data[k] = []
        for key in List_keys:
            try:
                data[key] += [ResDate[key]/ResDate[0] - 1]
            except:
                for key2 in data.keys():
                    data_len = min(data_len, len(data[key2]))
    DF["time"] = time[:data_len]
    for key in List_keys:
        DF[str(key)] = data[key][:data_len]
    return DF

