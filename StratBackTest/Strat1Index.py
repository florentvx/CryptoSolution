from matplotlib import pyplot as plt
from dask.dataframe.rolling import rolling_mean
from pandas import DataFrame
from numpy import int, str, float
from Prices import Currency
from Requests import OHLCLibrary
from scipy import stats
import numpy as np


class Strat1Index:
    def __init__(self, curID: str, currefID: str, fixing: str = "close", freq: int = 240):
        self.Cur = Currency(curID)
        self.CurRef = Currency(currefID)
        self.Fixing = fixing
        self.Freq = freq

    def Download(self):
        DF = DataFrame()
        DF = OHLCLibrary(self.Cur, self.CurRef, freq = self.Freq)
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


    def SimpleMAStrat(self, freq1 : int, freq2: int, factor : float = 1, longOnly: bool = True):
        self.MovingAverage(freq1)
        self.MovingAverage(freq2)
        n = max(freq1,freq2)
        alloc = [0 for i in range(n)]
        for (index,row) in self.DataFrame[n:].iterrows():
            ma1 = row["MA_" + str(freq1)]
            ma2 = row["MA_" + str(freq2)]
            pos = 1 - factor * abs((ma1 - ma2)/ma2)
            if longOnly:
                if ma1 > ma2:
                    alloc += [max(0,pos)]
                else:
                    alloc += [max(0,-pos)]
            else:
                if ma1 > ma2:
                    alloc += [pos]
                else:
                    alloc += [-pos]
        self.DataFrame["Alloc"] = alloc
        self.ApplyAllocation()


s1 = Strat1Index("XBT","EUR",freq = 1)
s1.Download()

s1.SimpleMAStrat(5,10,50)
#s1.DataFrame.to_clipboard()
I1 = list(s1.DataFrame["Index"])
A1 = list(s1.DataFrame["Alloc"])
s1.SimpleMAStrat(5,10,100)
I2 = list(s1.DataFrame["Index"])
A2 = list(s1.DataFrame["Alloc"])
s1.SimpleMAStrat(5,10)


plt.figure(1)
plt.subplot(311)
plt.plot(s1.DataFrame["time"], s1.DataFrame["close"])
plt.plot(s1.DataFrame["time"], s1.DataFrame["MA_" + str(5)])
plt.plot(s1.DataFrame["time"], s1.DataFrame["MA_" + str(10)])

plt.subplot(312)
plt.plot(s1.DataFrame["time"], I1)
plt.plot(s1.DataFrame["time"], I2)
plt.plot(s1.DataFrame["time"], s1.DataFrame["Index"])
plt.legend([str(50),str(100),str(1)])

plt.subplot(313)
plt.plot(s1.DataFrame["time"], A1)
plt.plot(s1.DataFrame["time"], A2)
plt.plot(s1.DataFrame["time"], s1.DataFrame["Alloc"])
plt.legend([str(50),str(100),str(1)])
plt.show()