
import matplotlib.pyplot as plt
from Requests import *
import krakenex

from Transaction import *
from IndexCalculations import *

print("CryptoCode.py")
time.sleep(1)
k = krakenex.API()
#ret = k.query_public("OHLC", req = {'pair': "XETHZUSD", 'since': str(1499000000)})

k.load_key("keys.txt")

#print(k.query_private('Balance'))
#print(k.query_private('TradesHistory'))
ledger = k.query_private('Ledgers')
Df = JsonToDataFrame(ledger,["time","amount","fee","balance"])

Df = Df.sort_values("time",0,True)

TL = TransactionList()
TL.Download(Df)

print(TL.ToString)



FXEURMH = FXMarketHistory()
FXEURMH.DownloadList([Currency.XBT,Currency.ETH,Currency.BCH,Currency.XRP,Currency.LTC],240)
#FXEURMH = FXMarketHistory(["XBT","ETH","BCH","XRP","LTC"],240)

AH = AllocationHistory(TL,FXEURMH)

print(AH.GetLastAllocation().ToString)




I = Index(AH, FXEURMH)
I.CalculateAllIndices()
#print(I.DataFrame)
I.CalculateStrategyIndex()
#I.RefactorIndex("BCH",0.25)
#I.RefactorIndex("LTC",0.25)
#I.RefactorIndex("XRP", 0.25)

fig1 = plt.figure()
plt.plot(I.DataFrame["time"], I.DataFrame["Total"])
plt.show()

fig2 = plt.figure()
plt.plot(I.DataFrame["time"], I.DataFrame["Index_XBT"],'-')
plt.plot(I.DataFrame["time"], I.DataFrame["Index_ETH"],'-')
plt.plot(I.DataFrame["time"], I.DataFrame["Index_Strat"],'-')
plt.plot(I.DataFrame["time"], I.DataFrame["Index_BCH"],'-')
plt.plot(I.DataFrame["time"], I.DataFrame["Index_LTC"],'-')
plt.plot(I.DataFrame["time"], I.DataFrame["Index_XRP"],'-')
plt.legend(["BTC", "ETH", "Strat", "BCH","LTC","XRP"])
plt.show()


#fig = plt.figure()
#plt.plot(DF_BTC["time"], DF_BTC["Index"],'-')
#plt.plot(DF_ETH["time"], DF_ETH["Index"],'-')
#plt.plot(DF_BCH["time"], DF_BCH["Index"],'-')
#plt.plot(DF_LTC["time"], DF_LTC["Index"],'-')
#plt.plot(DF_XRP["time"], DF_XRP["Index"],'-')

#plt.legend(["BTC", "ETH", "BCH", "LTC", "XRP"])
#plt.show()


def PrintExample():

    DF_BTC = OHLC(startDate = datetime(2017,1,1),freq = 240)
    DF_ETH = OHLC(X = "ETH", startDate = datetime(2017,1,1), freq = 240)

    DayPrices = ComputePricesPerDay(DF_BTC)

    print(len(DayPrices))

    plt.scatter(DayPrices["12"],DayPrices["-1"])
    plt.plot(DayPrices["12"],DayPrices["12"],'-')
    plt.show()

    start_BTC = DF_BTC["close"][0]
    start_ETH = DF_ETH["close"][0]


    fig = plt.figure()
    plt.plot(DF_BTC["time"], DF_BTC["close"] / start_BTC * 1000,'-')
    plt.plot(DF_ETH["time"], DF_ETH["close"] / start_ETH * 1000,'-')
    plt.legend(["BTC", "ETH"])
    plt.show()

    ComputeReturns(DF_BTC)
    ComputeReturns(DF_ETH)

    DF_BTC["mean_return"] = pd.rolling_mean(DF_BTC["return"], 10)
    DF_ETH["mean_return"] = pd.rolling_mean(DF_ETH["return"], 10)

    plt.plot(DF_BTC["time"], DF_BTC["mean_return"],'-')
    plt.plot(DF_ETH["time"], DF_ETH["mean_return"],'-')

    DF_BTC["std_return"] = pd.rolling_std(DF_BTC["return"], 10)
    DF_ETH["std_return"] = pd.rolling_std(DF_ETH["return"], 10)

    plt.plot(DF_BTC["time"], DF_BTC["std_return"],'-')
    plt.plot(DF_ETH["time"], DF_ETH["std_return"],'-')

    plt.legend(["BTC mean", "ETH mean", "BTC std", "ETH std"])
    plt.show()

