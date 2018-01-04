from Prices import *
from matplotlib import pyplot as plt
from dask.dataframe.rolling import rolling_mean
from pandas import DataFrame
from numpy import int, str
from Requests import OHLC


class Strat1Index:
    def __init__(self, curID: str, currefID: str, fixing: str = "close", freq: int = 240):
        self.Cur = Currency(curID)
        self.CurRef = Currency(currefID)
        self.Fixing = fixing
        self.Freq = freq

    def Download(self):
        DF = DataFrame()
        DF = OHLC(self.Cur, self.CurRef, freq = self.Freq)
        DF["Return"] = DF[self.Fixing]/DF[self.Fixing].shift(1) - 1
        self.DataFrame = DF

    def MovingAverage(self, freq: int):
        self.DataFrame["MA_" + str(freq)] = rolling_mean(self.DataFrame[self.Fixing], freq)

    def ApplyAllocation(self):
        self.DataFrame["temp"] = self.DataFrame.apply(lambda row: row["Return"] * row["Alloc"], axis = 1)
        Index = [1000]
        i=0
        print(self.DataFrame)
        for (index,row) in self.DataFrame[1:].iterrows():
            i+=1
            Index += [Index[-1] * (1 + row["temp"])]
        self.DataFrame["Index"] = Index


    def SimpleMAStrat(self, freq1 : int, freq2: int):
        self.MovingAverage(freq1)
        self.MovingAverage(freq2)
        alloc = []
        for (index,row) in self.DataFrame.iterrows():
            if row["MA_" + str(freq1)] > row["MA_" + str(freq2)]:
                alloc += [1]
            else:
                alloc += [-1]
        self.DataFrame["Alloc"] = alloc
        self.ApplyAllocation()


s1 = Strat1Index("XBT","EUR",freq = 30)
s1.Download()
s1.SimpleMAStrat(20,50)
s1.DataFrame.to_clipboard()
I1 = s1.DataFrame["Index"]
s1.SimpleMAStrat(20,50)
print(s1.DataFrame)


plt.figure(1)
plt.subplot(211)
plt.plot(s1.DataFrame["time"], s1.DataFrame["close"])
plt.plot(s1.DataFrame["time"], s1.DataFrame["MA_" + str(20)])
plt.plot(s1.DataFrame["time"], s1.DataFrame["MA_" + str(50)])

plt.subplot(212)
plt.plot(s1.DataFrame["time"], I1)
plt.plot(s1.DataFrame["time"], s1.DataFrame["Index"])
plt.show()