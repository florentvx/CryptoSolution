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


    def SimpleMAStrat(self, freq1 : int, freq2: int, factor : float = 1):
        self.MovingAverage(freq1)
        self.MovingAverage(freq2)
        n = max(freq1,freq2)
        alloc = [0 for i in range(n)]
        for (index,row) in self.DataFrame[n:].iterrows():
            ma1 = row["MA_" + str(freq1)]
            ma2 = row["MA_" + str(freq2)]
            pos = 1 - factor * abs((ma1 - ma2)/ma2)
            if ma1 > ma2:
                alloc += [pos]
            else:
                alloc += [-pos]
        self.DataFrame["Alloc"] = alloc
        self.ApplyAllocation()


s1 = Strat1Index("XBT","EUR",freq = 15)
s1.Download()

points = [-10./100. + 0.1/100.*i for i in range(2*100)]

pdf = stats.gaussian_kde(s1.DataFrame["Return"][1:])
df = pdf.evaluate(points)
print(pdf.factor)

pdf1 = stats.gaussian_kde(s1.DataFrame["Return"][1:],0.1)
df1 = pdf1.evaluate(points)

pdf2 = stats.gaussian_kde(s1.DataFrame["Return"][1:],0.5)
df2 = pdf2.evaluate(points)

mean = np.average(s1.DataFrame["Return"][1:])
std = np.std(s1.DataFrame["Return"][1:])

pdfgauss = [stats.norm.pdf(x,loc = mean, scale = std) for x in points]

print("mean : " + str(mean * 24 * 60 / s1.Freq))
print("std : " + str(std * 24 * 60 / s1.Freq))

print(np.sum(df)*0.1/100.)
print(np.sum(pdfgauss)*0.1/100.)

plt.figure()
plt.plot(points,df)
plt.plot(points,df1)
plt.plot(points,df2)
plt.legend([pdf.factor,pdf1.factor,pdf2.factor])
plt.show()

plt.figure()
plt.plot(points,df)
plt.plot(points,pdfgauss)
plt.legend(["return","gauss"])
plt.show()






s1.SimpleMAStrat(20,50,10)
#s1.DataFrame.to_clipboard()
I1 = list(s1.DataFrame["Index"])
s1.SimpleMAStrat(20,50,20)
I2 = list(s1.DataFrame["Index"])
s1.SimpleMAStrat(20,50)


plt.figure(1)
plt.subplot(211)
plt.plot(s1.DataFrame["time"], s1.DataFrame["close"])
plt.plot(s1.DataFrame["time"], s1.DataFrame["MA_" + str(20)])
plt.plot(s1.DataFrame["time"], s1.DataFrame["MA_" + str(50)])

plt.subplot(212)
plt.plot(s1.DataFrame["time"], I1)
plt.plot(s1.DataFrame["time"], I2)
plt.plot(s1.DataFrame["time"], s1.DataFrame["Index"])
plt.legend([str(10),str(20),str(1)])
plt.show()