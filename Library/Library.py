import pandas as pd
#from pandas.io.json.json import to_json
from Prices import Currency, CurrencyPair
from os.path import isfile
import datetime
import time

pathLibrary = "../Library/CsvLibrary/"



def GetFilePath(curPair : CurrencyPair, freq: int):
    name = curPair.RequestID
    res = pathLibrary + name + "_" + str(freq) + ".csv"
    return res

def GetFile(curPair: CurrencyPair, freq: int):
    res = GetFilePath(curPair, freq)
    if isfile(res):
        return res
    else:
        resInv = GetFilePath(curPair.GetInverse(), freq)
        if isfile(resInv):
            return resInv
        else:
            return None

def ReadFile(curPair: CurrencyPair, freq: int):
    filePath = GetFile(curPair, freq)
    if filePath != None:
        DF = pd.read_csv(filePath)
        #DF = DF.set_index("time") 
        columns = list(DF.columns)
        columns.remove("Unnamed: 0")
        DF = DF[columns]
        return DF
    else:
        return None

def CreateGrossFile(curPair: CurrencyPair, freq: int, DF: pd.DataFrame):
    path = GetFilePath(curPair, freq)
    DF.reset_index()
    DF.to_csv(path)


def CompleteHoles(DF : pd.DataFrame, freq: int):
    lastDate = 0
    for (index, row) in DF.iterrows():
        date = row["time"]
        if lastDate != 0:
            diff = (date - lastDate)
            diffSecs = diff.days * 24 * 60 * 60 + diff.seconds
            if diffSecs != freq * 60:
                if diffSecs == 0:
                    DF = DF.drop(index)
                else:
                    print(row["time"])
                    ListRows = []
                    n = int(diffSecs / float(freq * 60))
                    for i in range(n - 1):
                        newRow = row.copy()
                        lastDate = lastDate + datetime.timedelta(seconds = freq * 60)
                        newRow["time"] = lastDate 
                        ListRows += [newRow]
                    print(ListRows)
                    for row in ListRows:
                        DF = DF.append(row)
        lastDate = date
    DF = DF.sort_values("time")
    return DF


def LinearInterpolationFillMethod(DF: pd.DataFrame, start: datetime.datetime, end: datetime.datetime, freq: int):
    columns = ["open", "high", "low", "close", "vwap", "volume", "count"]
    DFstart = DF[DF["time"] < start]
    DFend = DF[DF["time"] > end]
    row0 = DFstart.tail(1)
    row1 = DFend.head(1)
    DFmid = DF[DF["time"] >= start]
    DFmid = DFmid[DFmid["time"] <= end]
    n = len(DFmid)
    i = 1
    res = {}
    for col in columns:
        res[col] = []
    for (index, row) in DFmid.iterrows():
        w = i/float(n)
        for col in columns:
            res[col] += [(1 - w) * float(row0[col]) + w * float(row1[col])]
        i += 1
    for col in columns:
        DF[col] = list(DFstart[col]) + res[col] + list(DFend[col])
    #print(DF)