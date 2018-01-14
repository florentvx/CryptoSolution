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


#CompleteHoles(CurrencyPair(Currency("XBT"),Currency("EUR")), 240)