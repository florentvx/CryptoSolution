from Framework.Prices import Currency,Price,XChangeRate
from CryptoCode.FXMarket import FXMarketHistory
from CryptoCode.Transaction import TransactionType, Transaction, TransactionList
from datetime import datetime
from CryptoCode.AllocationHistory import AllocationHistory
from CryptoCode.IndexCalculations import Index

XCRateBTC0 = XChangeRate(1000, Currency("XBT"),Currency("EUR"))
XCRateETH0 = XChangeRate(100, Currency("ETH"),Currency("EUR"))
XCRateBTC1 = XChangeRate(1100, Currency("XBT"),Currency("EUR"))
XCRateETH1 = XChangeRate(90, Currency("ETH"),Currency("EUR"))
XCRateBTC2 = XChangeRate(1200, Currency("XBT"),Currency("EUR"))
XCRateETH2 = XChangeRate(100, Currency("ETH"),Currency("EUR"))


FXMH = FXMarketHistory()
FXMH.AddXChangeRate(datetime(2017,1,1), XCRateBTC0)
FXMH.AddXChangeRate(datetime(2017,1,1), XCRateETH0)
FXMH.AddXChangeRate(datetime(2017,3,1), XCRateBTC1)
FXMH.AddXChangeRate(datetime(2017,3,1), XCRateETH1)
FXMH.AddXChangeRate(datetime(2017,5,1), XCRateBTC2)
FXMH.AddXChangeRate(datetime(2017,5,1), XCRateETH2)


print(FXMH.ToString)

t1 = Transaction(TransactionType.Deposit,datetime(2017,2,1),Price(0,Currency.NONE),Price(1000,Currency.EUR),Price(0,Currency.NONE))
t2 = Transaction(TransactionType.Trade,datetime(2017,2,15),Price(500,Currency.EUR),Price(0.5,Currency.XBT),Price(0,Currency.EUR))
t3 = Transaction(TransactionType.Trade,datetime(2017,4,1),Price(0.25,Currency.XBT),Price(3.4375,Currency.ETH),Price(0,Currency.EUR))


TL = TransactionList()
TL.SetList([t1,t2,t3])

AH = AllocationHistory(TL,FXMH)

print(AH.ToString)

print(TL.GetAverageCosts(FXMH))

I = Index(AH,FXMH)
print(I.DataFrame)

#TODO: Implement a sorted Dictionary - in order to store Allocation and FXMarket
#TODO: Be able to create manually everything (FXMarket History, Allocation History)
#TODO: Separate with a Download Function the request from kraken and the init (FXMarketHistory)
#TODO: PDLs
