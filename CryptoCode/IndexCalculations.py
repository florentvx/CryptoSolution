from AllocationHistory import *


def DateCut(date: datetime):
    print(date)
    return datetime(date.year, date.month, date.day, date.hour, date.minute)

def RenameColumn(x: str, cur: Currency):
    if x=="time":
        return x
    else:
        return x + "_" + cur.name

def RenameColumns(DF: pd.DataFrame, columns: list, cur: Currency):
    cols = list(DF.columns)
    for i in range(len(cols)):
        str = cols[i]
        if str in columns:
            cols[i] = RenameColumn(str, cur)
    DF.columns = cols



class Index:

    def __init__(self, AH : AllocationHistory, FXMH: FXMarketHistory):
        self.Currencies = AH.Currencies
        self.CurrencyRef = FXMH.CurrencyRef

        Spots = {}
        Allocs = {}
        Total = []
        Dates = []
        for cur in self.Currencies + [self.CurrencyRef]:
            Spots[cur] = []
            Allocs[cur] = []
        for date in AH.History.Keys:
            Dates += [date]
            alloc = AH.GetAllocation(date)[0]
            Total += [alloc.Total.Amount]
            FX = FXMH.GetFXMarket(date)
            for cur in self.Currencies:
                Spots[cur] += [FX.GetFXRate(cur, self.CurrencyRef)]
                try:
                    Allocs[cur] += [alloc.Dictionary[cur].Percentage]
                except:
                    Allocs[cur] += [0]
            Allocs[self.CurrencyRef] += [alloc.Dictionary[self.CurrencyRef].Percentage]

        DF = pd.DataFrame()
        DF["time"] = Dates

        DF["Total"] = Total
        for cur in self.Currencies + [self.CurrencyRef]:

            if cur != self.CurrencyRef:
                DF["Spot_" + cur.ToID] = Spots[cur]
            DF["Alloc_" + cur.ToID] = Allocs[cur]
        self.DataFrame = DF

    def CalculateIndex(self, ID: str):
        self.DataFrame["Return_" + ID] = self.DataFrame["Spot_" + ID]/self.DataFrame["Spot_" + ID].shift(1) - 1
        IndexList = [1000]
        for (index, row) in self.DataFrame[1:].iterrows():
            IndexList += [IndexList[-1] * (1 + row["Return_" + ID])]
        self.DataFrame["Index_" + ID] = IndexList

    def CalculateAllIndices(self):
        for cur in self.Currencies:
            id = cur.ToID
            self.CalculateIndex(id)

    def RefactorIndex(self, ID: str, factor: float):
        self.DataFrame["Return_" + ID] = self.DataFrame["Spot_" + ID]/self.DataFrame["Spot_" + ID].shift(1) - 1
        Index = [1000]
        for (index, row) in self.DataFrame[1:].iterrows():
            Index += [Index[-1] * (1 + factor * row["Return_" + ID])]
        self.DataFrame["Index_" + ID] = Index

    def CalculateStrategyIndex(self):
        res = [1000]
        for (index,row) in self.DataFrame[1:].iterrows():
            ret = 0
            for cur in self.Currencies:
                ret += row["Alloc_" + cur.ToID] * row["Return_" + cur.ToID]
            res += [res[-1] * (1 + ret)]
        self.DataFrame["Index_Strat"] = res