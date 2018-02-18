from enum import Enum, auto
import pandas as pd
import datetime

from Prices import *


def DictionaryToDataFrame(data: dict, columns: list, precision: int = 4):
    Index = []
    Values = {column:[] for column in columns}
    for key in data.keys():
        Index += [key]
        val = data[key]
        if type(val) == float:
            val = round(val,precision)
            Values[columns[0]] += [val]
        elif type(val) == list:
            for i in range(len(val)):
                Values[columns[i]] += [round(val[i],precision)]
        else:
            raise Exception("Type not taken into account")
    DF = pd.DataFrame(Index, columns = ["Currency"])
    for col in columns:
        DF[col] = Values[col]
    return DF

class TransactionType(Enum):
    NONE = auto()
    Deposit = auto()
    Trade = auto()

    @property
    def ToString(self):
        if self == TransactionType.NONE:
            return "None"
        elif self == TransactionType.Deposit:
            return "Deposit"
        elif self == TransactionType.Trade:
            return "Trade"
        else:
            raise Exception("Transaction Type Error")

class Transaction:

    def __init__(self, type: TransactionType, date: datetime, paid: Price, received: Price, fees: Price):
        self.Type = type
        self.Date = date
        self.Paid = paid
        self.Received = received
        self.Fees = fees
        if type != TransactionType.Deposit:
            ratio = int(paid.Amount / received.Amount * 10000)/10000.0
            self.XRate = XChangeRate(ratio, received.Currency,paid.Currency)
            #if ratio > 1:
            #    self.XRate = XChangeRate(ratio, received.Currency,paid.Currency)
            #else:
            #    self.XRate = XChangeRate(1/ratio, paid.Currency, received.Currency)
        else:
            self.XRate = XChangeRate(1,received.Currency, received.Currency)
        # the fees are here quoted as extra/ I pay paid.Amount + fees


    @property
    def ToString(self):
        return str(self.Date) + " " + self.Type.ToString + '\n' + \
               "Paid: " + self.Paid.ToString + '\n' + \
               "Received: " + self.Received.ToString + '\n' + \
               "Fees: " + self.Fees.ToString + '\n' + \
               "XChange Rate: " + self.XRate.ToString

class TransactionList:

    def __init__(self):
        self.List = []

    def SetList(self, list):
        self.List = list

    def Download(self, data : pd.DataFrame, curRef: Currency = Currency.EUR):
        paidPrice = Price(0,curRef)
        receivedPrice = Price(0,curRef)
        fees = Price(0,curRef)
        self.CcyRef = curRef
        self.List = []
        for (index, row) in data.iterrows():
            if row["type"] == "deposit":
                self.List += [Transaction(
                    TransactionType.Deposit,
                    row["time"],
                    Price(0, curRef),
                    Price(row["amount"],row["asset"][1:]),
                    Price(0, curRef))]
            elif row["type"] == "trade":
                asset = row["asset"]
                asset = asset[(len(asset) - 3):]
                if row["amount"] > 0:
                    receivedPrice = Price(row["amount"],asset)
                elif row["amount"] < 0:
                    paidPrice = Price(-row["amount"],asset)
                else:
                    raise Exception("Amount free Price")
                if row["fee"] > 0:
                    if fees.Amount == 0:
                        fees = Price(row["fee"],row["asset"][1:])
                    else:
                        raise Exception("Double fees Problem")
                if paidPrice.Amount > 0 and receivedPrice.Amount > 0:
                    self.List += [Transaction(
                        TransactionType.Trade,
                        row["time"],
                        paidPrice,
                        receivedPrice,
                        fees)]
                    paidPrice = Price(0,curRef)
                    receivedPrice = Price(0,curRef)
                    fees = Price(0,curRef)
            else:
                raise Exception("Trade type Unknown")
    
    #TODO: What if BTC are exchanged for ETH???
    def GetAverageCosts(self):
        res = {}
        for transaction in self.List:
            Rec = transaction.Received
            Paid = transaction.Paid
            if Rec.Currency != self.CcyRef and Paid.Currency == self.CcyRef:
                if not Rec.Currency.ToString in res.keys():
                    res[Rec.Currency.ToString] = [Paid.Amount / Rec.Amount, Rec.Amount]
                else:
                    old = res[Rec.Currency.ToString]
                    newN = old[1] + Rec.Amount
                    newCost = (old[0] * old[1] + Paid.Amount)/newN
                    res[Rec.Currency.ToString] = [newCost,newN]
            elif Rec.Currency == self.CcyRef and Paid.Currency != self.CcyRef:
                if not Paid.Currency in res.keys():
                    raise BaseException("Problem: Paid with a currency unpresent in the portfolio")
                else:
                    old = res[Paid.Currency.ToString]
                    res[Paid.Currency.ToString] = [old[0], old[1] - Paid.Amount]
        return DictionaryToDataFrame(res, ["Cost","Amount"])

    @property
    def IsSorted(self):
        res = True
        if len(self.List) == 0:
            return None
        else:
            date = self.List[0]
            for tr in self.List[1:]:
                if tr.Date > date:
                    date = tr.Date
                else:
                    res = False
                    break
            return res


    @property
    def ToString(self):
        res = '\n' + "Transactions List: " + '\n'
        i = 0
        for tr in self.List:
            res += str(i) + ":" + '\n' + tr.ToString + '\n' + '\n'
            i += 1
        return res