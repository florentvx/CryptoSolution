from IndexCalculations import *

XCRate0 = XChangeRate(100, Currency("XBT"),Currency("EUR"))
XCRate1 = XChangeRate(110, Currency("XBT"),Currency("EUR"))
XCRate2 = XChangeRate(150, Currency("XBT"),Currency("EUR"))


FXMH = FXMarketHistory()
FXMH.AddXChangeRate(datetime(2017,1,1), XCRate0)

print(FXMH.ToString)


FXMH.AddXChangeRate(datetime(2017,3,1), XCRate1)
FXMH.AddXChangeRate(datetime(2017,5,1), XCRate2)

print(FXMH.ToString)

t1 = Transaction(TransactionType.Deposit,datetime(2017,2,1),Price(0,Currency.NONE),Price(100,Currency.EUR),Price(0,Currency.NONE))
t2 = Transaction(TransactionType.Trade,datetime(2017,2,15),Price(50,Currency.EUR),Price(0.5,Currency.XBT),Price(1,Currency.EUR))
t3 = Transaction(TransactionType.Trade,datetime(2017,4,1),Price(11,Currency.EUR),Price(0.1,Currency.XBT),Price(1,Currency.EUR))


TL = TransactionList()
TL.SetList([t1,t2,t3])

AH = AllocationHistory(TL,FXMH)

print(AH.ToString)

I = Index(AH,FXMH)
print(I.DataFrame)

#TODO: Implement a sorted Dictionary - in order to store Allocation and FXMarket
#TODO: Be able to create manually everything (FXMarket History, Allocation History)
#TODO: Separate with a Download Function the request from kraken and the init (FXMarketHistory)
#TODO: PDLs
