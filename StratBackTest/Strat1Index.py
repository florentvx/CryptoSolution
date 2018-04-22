from matplotlib import pyplot as plt
import pandas as pd
from numpy import int, str, float
from Prices import Currency
from Requests import OHLCLibrary
from scipy import stats
from math import sqrt
import numpy as np

class Strat1Index:
    def __init__(self, curID: str, currefID: str, fixing: str = "close", freq: int = 240):
        self.Cur = Currency(curID)
        self.CurRef = Currency(currefID)
        self.Fixing = fixing
        self.Freq = freq

    def Download(self):
        DF = pd.DataFrame()
        DF = OHLCLibrary(self.Cur, self.CurRef, freq = self.Freq)
        DF["Return"] = DF[self.Fixing]/DF[self.Fixing].shift(1) - 1
        self.DataFrame = DF

    def MovingAverage(self, freq: int):
        self.DataFrame["MA_" + str(freq)] = pd.rolling_mean(self.DataFrame[self.Fixing], freq)

    def VWMA(self, freq: int):
        VWMAcolumn = "VWMA_" + str(freq)
        self.DataFrame[VWMAcolumn] = self.DataFrame[self.Fixing] * self.DataFrame["volume"]
        self.DataFrame["temp"] = self.DataFrame["volume"].rolling(window = freq).sum()
        self.DataFrame[VWMAcolumn] = self.DataFrame[VWMAcolumn].rolling(window = freq).sum()
        self.DataFrame[VWMAcolumn] = self.DataFrame.apply(lambda row: row[VWMAcolumn] / row["temp"], axis = 1)

    def Results(self, col: str = "temp"):
        average = self.DataFrame[col].mean() * (240 * 6) /self.Freq * 30
        stddev = self.DataFrame[col].std() * sqrt((240 * 6) / self.Freq * 30)
        sharpe = average/stddev
        return [average, stddev,sharpe]

    def ResultString(self, col: str = "temp"):
        L = self.Results(col)
        res = "The average (monthy) return is: " + str(round(L[0] * 100, 4)) + "% \n"
        res += "The average (monthly) return is: " + str(round(L[1] * 100, 4)) + "% \n"
        res += "The Sharpe Ratio is: " + str(round(L[2], 4)) + " \n"
        return res
        
    def ApplyAllocation(self):
        self.DataFrame["temp"] = self.DataFrame.apply(lambda row: row["Return"] * row["Alloc"], axis = 1)
        Index = [1000]
        i=0
        for (index,row) in self.DataFrame[1:].iterrows():
            i+=1
            Index += [Index[-1] * (1 + row["temp"])]
        self.DataFrame["Index"] = Index
        

    def SimpleMAStrat(self, freq1 : int, freq2: int, factor : float = 1, longOnly: bool = False):
        self.VWMA(freq1)
        self.VWMA(freq2)
        n = max(freq1,freq2)
        alloc = [0 for i in range(n)]
        for (index,row) in self.DataFrame[n:].iterrows():
            ma1 = row["VWMA_" + str(freq1)]
            ma2 = row["VWMA_" + str(freq2)]
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


s1 = Strat1Index("XBT","EUR",freq = 60)
s1.Download()

freqMA = [5,10,15,20]
factors = [-1000,-100,-10,10,100,1000
           ]

param = [0,0,0]
sMax = 0
for i in range(1,len(freqMA)):
    print(i)
    for j in range(i):
        MA1 = freqMA[j]
        MA2 = freqMA[i]
        for factor in factors:
            s1.SimpleMAStrat(MA1,MA2,factor)
            s = s1.Results()[2]
            if s > sMax:
                param = [MA1,MA2,factor]
                sMax = s

print("MA1: " + str(param[0]) + "\n MA2: " + str(param[1]) + "\n Factor " + str(param[2]))
s1.SimpleMAStrat(param[0],param[1],param[2])
print(s1.ResultString())



plt.figure(1)
plt.subplot(311)
plt.plot(s1.DataFrame["time"], s1.DataFrame["close"])
plt.plot(s1.DataFrame["time"], s1.DataFrame["VWMA_" + str(param[0])])
plt.plot(s1.DataFrame["time"], s1.DataFrame["VWMA_" + str(param[1])])

plt.subplot(312)
plt.plot(s1.DataFrame["time"], s1.DataFrame["Index"])

plt.subplot(313)
plt.plot(s1.DataFrame["time"], s1.DataFrame["Alloc"])
plt.show()