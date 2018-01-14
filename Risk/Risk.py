from Prices import Currency
from Requests import OHLCLibrary
from scipy import stats
from pandas import DataFrame

class Density:

    def __init__(self, cur: Currency, curRef: Currency = Currency.EUR, fixing: str = "close", freq: int = 240):
        self.Currency = cur
        self.CurrencyRef = curRef
        self.Fixing = fixing
        self.Freq = freq

    def DownloadReturns(self):
        DF = DataFrame()
        DF = OHLCLibrary(self.Currency, self.CurrencyRef, freq = self.Freq, isUpdating = False)
        DF["Return"] = DF[self.Fixing]/DF[self.Fixing].shift(1) - 1
        self.DataFrame = DF

    def GetPDF(self, max: float = 0.25, n: int = 100):
        self.Points = [-max + 2 * max * i / float(n) for i in range(n + 1)]
        self.PDF = stats.gaussian_kde(self.DataFrame["Return"][1:]).evaluate(self.Points)

    def GetCDF(self, precision : int = 100):
        CDF = []
        dx = 1 / float(precision)
        x = dx
        i = 0
        for i_percentile in range(precision - 1):
            tot = 0
            i = 0
            dtot = 0
            while tot + dtot < x:
                tot += dtot
                dtot = (self.Points[i+1] - self.Points[i]) * self.PDF[i]
                i += 1
            w = (x - tot) / dtot
            CDF += [(1 - w) * self.Points[i] + w * (self.Points[i + 1])]
        self.CDF = CDF

d = Density(Currency.XBT)
d.DownloadReturns()
d.GetPDF()
d.GetCDF(2)









