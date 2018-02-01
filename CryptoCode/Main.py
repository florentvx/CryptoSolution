
import matplotlib.pyplot as plt
from Requests import *


from Transaction import *
from IndexCalculations import *

print("CryptoCode.py")
time.sleep(1)

Df = KrakenLedgerRequest()

TL = TransactionList()
TL.Download(Df)


FXEURMH = FXMarketHistory()
FXEURMH.DownloadList([Currency.XBT,Currency.ETH,Currency.BCH,Currency.XRP,Currency.LTC], 240, live = True)
#FXEURMH = FXMarketHistory(["XBT","ETH","BCH","XRP","LTC"],240)

AH = AllocationHistory(TL,FXEURMH)
lastAlloc = AH.GetLastAllocation()
print(lastAlloc.ToString)
print(lastAlloc.VaR(0.05).ToString)



I = Index(AH, FXEURMH)
I.CalculateAllIndices()
I.CalculateStrategyIndex()

plt.figure()
plt.subplot(211)
plt.plot(I.DataFrame["time"], I.DataFrame["Index_Strat"])
plt.plot(I.DataFrame["time"], I.DataFrame["Index_XBT"], 'g-')
plt.legend(["Strat","XBT"])

plt.subplot(212)
plt.plot(I.DataFrame["time"], I.DataFrame["Total"], 'r-')
plt.legend(["Amount"])
plt.show()

fig = plt.figure()
plt.subplot(211)
plt.plot(I.DataFrame["time"], I.DataFrame["Alloc_XBT"],'-')
plt.plot(I.DataFrame["time"], I.DataFrame["Alloc_ETH"],'-')
plt.legend(["XBT","ETH"])
plt.subplot(212)
plt.plot(I.DataFrame["time"], I.DataFrame["Alloc_BCH"],'-')
plt.plot(I.DataFrame["time"], I.DataFrame["Alloc_LTC"],'-')
plt.plot(I.DataFrame["time"], I.DataFrame["Alloc_XRP"],'-')
plt.legend(["BCH", "LTC", "XRP"])
plt.show()


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

