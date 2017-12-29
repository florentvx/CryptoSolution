
from Requests import *
from Prices import *
from SortedDictionary import *



class FXMarket:

    def __init__(self, XChangeRates: list):
        self.FX = []
        for xRate in XChangeRates:
            if type(xRate) == XChangeRate:
                self.FX += [xRate]
            else:
                raise Exception("Wrong Input")

    def IsFXRate(self,X: Currency, Y: Currency):
        if X==Y:
            return 0
        else:
            for xRate in self.FX:
                if xRate.CurPair.X == X:
                    if xRate.CurPair.Y == Y:
                        return 1
                if xRate.CurPair.Y == X:
                    if xRate.CurPair.X == Y:
                        return -1
            return 0

    def GetFXRate(self, X: Currency, Y: Currency):
        if X == Y:
            return 1.0
        for i in range(len(self.FX)):
            xRate = self.FX[i]
            if xRate.CurPair.X == X:
                if xRate.CurPair.Y == Y:
                    return xRate.Rate
            if xRate.CurPair.Y == X:
                if xRate.CurPair.X == Y:
                    return 1 / xRate.Rate
        raise Exception("Undefined XChangeRate: " + X.ToString + " " + Y.ToString)

    def AddQuote(self, XCRate: XChangeRate):
        X = XCRate.CurPair.X
        Y = XCRate.CurPair.Y
        test = self.IsFXRate(X,Y)
        if test > 0:
            self.FX[test] = XCRate
        elif test < 0:
            self.FX[-test] = XChangeRate(XCRate.Rate,Y,X)
        else:
            self.FX += [XCRate]


    def ConvertPrice(self, input: Price, output: Currency):
        rate = self.GetFXRate(input.Currency, output)
        return Price(input.Amount * rate, output)

    def Sum(self, price : Price, Delta : Price):
        if price.Currency == Currency.NONE and price.Currency.Amount == 0:
            return Delta
        else:
            if Delta.Currency == Currency.NONE and Delta.Amount ==0:
                return price
            else:
                return Price(price.Amount + self.ConvertPrice(Delta, price.Currency).Amount, price.Currency)

    @property
    def ToString(self):
        res = "FX Market" + '\n'
        for xRate in self.FX:
            res += xRate.ToString + '\n'
        return res


#1 (default), 5, 15, 30, 60, 240, 1440, 10080, 21600

class FXMarketHistory:

    def __init__(self, ref: Currency = Currency.EUR):
        self.CurrencyRef = ref
        self.FXMarkets = SortedDictionary()
        self.Currencies = []

    def AddQuote(self, date, cur, quote):
        if cur not in self.Currencies:
            self.Currencies += [cur]
        (FX,test) = self.FXMarkets.Get(date)
        if test == 1:
            FX.AddQuote(XChangeRate(quote,cur,self.CurrencyRef))
        else:
            newFX = FXMarket([XChangeRate(quote, cur, self.CurrencyRef)])
            self.FXMarkets.Add(date,newFX)

    def AddXChangeRate(self, date, XRate: XChangeRate):
        if XRate.CurPair.Y == self.CurrencyRef:
            self.AddQuote(date,XRate.CurPair.X,XRate.Rate)
        elif XRate.CurPair.X == self.CurrencyRef:
            self.AddQuote(date,XRate.CurPair.X,XRate.Rate)
        else:
            raise Exception(XRate.ToString + " : Invalid quote (ref: " + self.CurrencyRef.ToString +")")

    def Download(self, cur: Currency, freq: int, fixing: str = "close", startDate: datetime = datetime.datetime(2017,1,1)):
        DF = OHLC(X = cur, Z = self.CurrencyRef, startDate = startDate, freq = freq)
        #print(DF)
        for (index, row) in DF.iterrows():
            self.AddQuote(row["time"], cur, row[fixing])

    def DownloadList(self,curList: list, freq: int, fixing: str = "close", startDate: datetime = datetime.datetime(2017,1,1)):
        for cur in curList:
            self.Download(cur, freq, fixing, startDate)

    #def DownloadList(self, CurrencyList: list, freq: int):
    #    self.DataFrames = {}
    #    for cur in CurrencyList:
    #        DF = OHLC(X = cur, Z = self.CurrencyRef.name, startDate = datetime.datetime(2017,1,1), freq = freq)
    #        DF["return"] = DF["close"]/DF["close"].shift(1) - 1
    #        Index = [1000]
    #        for (index,row) in DF[1:].iterrows():
    #            Index += [Index[-1] * (1 + row["return"])]
    #        DF["Index"] = Index
    #        self.DataFrames[Currency(cur)] = DF


    #def RefactorReturns(self, factor: float, X: Currency):
    #    DF = self.DataFrames[X]
    #    DF["return"] = (DF["close"]/DF["close"].shift(1) - 1) * factor
    #    Index = [1000]
    #    for (index,row) in DF[1:].iterrows():
    #        Index += [Index[-1] * (1 + row["return"])]
    #    DF["Index"] = Index
    #    self.DataFrames[Currency(X)] = DF


    def GetFXMarket(self, date: datetime):
        return self.FXMarkets.Get(date)[0]

    @property
    def ToString(self):
        res = "FXMarketHIstory: Currency Ref : " + self.CurrencyRef.ToString + "\n"
        for i in range(self.FXMarkets.Keys.N):
            key = self.FXMarkets.Keys.HardGet(i)
            res += str(key) + "\n"
            res += self.GetFXMarket(key).ToString + "\n"
        return res