from Prices import Currency
from Requests import OHLCLibrary
from scipy import stats
import pandas as pd
import math as mth
import matplotlib.pyplot as plt

class Density:

    def __init__(self, cur: Currency, curRef: Currency = Currency.EUR, fixing: str = "close", freq: int = 240):
        self.Currency = cur
        self.CurrencyRef = curRef
        self.Fixing = fixing
        self.Freq = freq
        self.Points = []

    def DownloadReturns(self):
        DF = pd.DataFrame()
        DF = OHLCLibrary(self.Currency, self.CurrencyRef, freq = self.Freq, live = False)
        DF["Return"] = DF[self.Fixing]/DF[self.Fixing].shift(1) - 1
        self.Returns = list(DF["Return"][1:])

    def GetPDF(self, max: float = 0.5, n: int = 1000):
        self.dx = 2 * max / float(n)
        self.Max = max
        self.Points = [-max + self.dx * i  for i in range(n + 1)]
        self.PDF = stats.gaussian_kde(self.Returns).evaluate(self.Points)

    def ToDataFrame(self):
        DF = pd.DataFrame()
        try:
            DF["Points"] = self.Points
            DF["PDF"] = self.PDF
            return DF
        except:
            return pd.DataFrame()


    def GetCDF(self, precision : int = 1000):
        CDF = []
        dx = 1 / float(precision)
        x = dx
        i = 0
        imax = len(self.PDF)
        for i_percentile in range(precision - 1):
            tot = 0
            i = 0
            dtot = 0
            while tot + dtot < x and i< imax:
                tot += dtot
                dtot = self.dx * self.PDF[i]
                i += 1
            w = (x - tot) / dtot
            CDF += [self.Points[i - 2] - w * self.dx]
            x += dx
        self.CDF = CDF

    def GetPDFMeasure(self, n: int):
        res = 0
        for i in range(len(self.Points)):
            res += self.PDF[i] * (self.Points[i]) ** n
        return res * self.dx

    def NormParam(self):
        mu = self.GetPDFMeasure(1)
        return (mu, (self.GetPDFMeasure(2) - mu ** 2) ** 0.5)
    
    def GetHistoricalQuantiles(self):
        Quantiles = []
        n = float(len(self.CDF))
        for ret in self.Returns:
            i = 0
            while i < int(n) and self.CDF[i] < ret:
                i += 1
            if i == 0:
                w = (ret + self.Max) / (self.CDF[i] + self.Max)
                Quantiles += [w / n]
            elif i == n:
                w = (ret - self.Max) / (self.CDF[i-1] - self.Max)
                Quantiles += [1 - w / n]
            else:
                w = (ret - self.CDF[i]) / (self.CDF[i-1] - self.CDF[i])
                Quantiles += [(i + 1 - w) / n]
            if Quantiles[-1] < 0 or Quantiles[-1] > 1:
                print("error")
        self.Quantiles = Quantiles

    def TransformToStdNorm(self):
        StdReturns = []
        for q in self.Quantiles:
            StdReturns += [stats.norm.ppf(q)]
        self.StdReturns = StdReturns

    def TransformFromStdNorm(self, ret):
        q = stats.norm.cdf(ret)
        n = len(self.CDF)
        i = int((n + 1) * q)
        w = n * q - i
        if i >= n - 1:
            return self.CDF[n - 1]
        else:
            return (1 - w) * self.CDF[i] + w * self.CDF[i+1]

    def TotalTransform(self):
        self.DownloadReturns()
        print("Loaded " + str(len(self.Returns)) + " Returns for the Currency: " + self.Currency.ToString)
        self.GetPDF()
        self.GetCDF()
        self.GetHistoricalQuantiles()
        self.TransformToStdNorm()

def Example():
    d = Density(Currency.BCH)
    d.TotalTransform()

    plt.figure()
    plt.subplot(211)
    plt.hist(d.Returns, bins = 50)
    plt.subplot(212)
    plt.hist(d.StdReturns, bins = 50)
    plt.show()







