from Framework.Prices import Currency, Price
from Framework.SortedDictionary import SortedDictionary
from CryptoCode.FXMarket import FXMarket, FXMarketHistory
from CryptoCode.Transaction import TransactionType, Transaction, TransactionList
from copy import deepcopy
from datetime import datetime
from Risk.Copula import Copula

class AllocationElement:

    def __init__(self, percentage: float, amount: float, currency: Currency):
        if percentage <= 1.0:
            self.Percentage = percentage
        else:
            Exception("Allocation Element > 100%")
        self.Price = Price(amount, currency)

    @property
    def Amount(self):
        return self.Price.Amount

    def SetAmount(self, value):
        self.Price.Amount = value

    @property
    def Currency(self):
        return self.Price.Currency

    @property
    def ToString(self):
        return "( " + str(int(self.Percentage * 10000.0) / 100.0) + \
               " %, " + self.Price.ToString + ")"


class Allocation:

    def __init__(self, dictionary: dict, fee = AllocationElement(0., 0., Currency.NONE)):
        #self.Date = date
        self.Dictionary = dictionary
        self.Fee = fee
        self.Total = Price(0,Currency.NONE)

    def CalculateTotal(self, FX: FXMarket, curRef: Currency = Currency.EUR):
        total = Price(0,curRef)
        for cur in self.Dictionary.keys():
            total = FX.Sum(total, self.Dictionary[cur])
        total = FX.Sum(total, self.Fee.Price)
        self.Total = total
        return total

    def Copy(self):
        dico = deepcopy(self.Dictionary)
        fee = AllocationElement(self.Fee.Percentage, self.Fee.Amount, self.Fee.Currency)
        return Allocation(dico, fee)

    def CancelFee(self):
        self.Fee = AllocationElement(0,0,Currency.NONE)

    def UpdatePercentages(self,FX: FXMarket, curRef: Currency = Currency.EUR):
        total = self.CalculateTotal(FX)
        for cur in self.Dictionary.keys():
            self.Dictionary[cur].Percentage = self.Dictionary[cur].Amount / FX.ConvertPrice(total, cur).Amount
        if self.Fee.Currency != Currency.NONE:
            self.Fee.Percentage = self.Fee.Amount / FX.ConvertPrice(total, self.Fee.Currency).Amount

    def Move(self, FX: FXMarket, curRef : Currency = Currency.EUR):
        newAlloc = self.Copy()
        newAlloc.CancelFee()
        newAlloc.UpdatePercentages(FX, curRef)
        return newAlloc

    def AddTransaction(self, transaction: Transaction, FX: FXMarket):
        res = deepcopy(self.Dictionary)
        fees = AllocationElement(0.,0,Currency.NONE)
        try:
            allocIn = res[transaction.Received.Currency]
            allocIn.SetAmount(allocIn.Amount + transaction.Received.Amount)
        except:
            res[transaction.Received.Currency] = \
                AllocationElement(0.,transaction.Received.Amount, transaction.Received.Currency)

        # Changing the Amounts
        
        # Paid
        if transaction.Type != TransactionType.Withdrawals or transaction.Paid.Currency.IsFiat:
            try:
                alloc = res[transaction.Paid.Currency]
                alloc.SetAmount(alloc.Amount - transaction.Paid.Amount)
                if alloc.Amount < 0:
                    raise Exception("Paid more than available")
            except:
                raise Exception("Paid in unavailable currency")

        # Fees
        try:
            fAlloc = res[transaction.Fees.Currency]
            fAlloc.SetAmount(fAlloc.Amount - transaction.Fees.Amount)
            if fAlloc.Amount < 0:
                raise Exception("Paid more than available (fees)")
            fees = AllocationElement(0., transaction.Fees.Amount, transaction.Fees.Currency)
        except:
            raise Exception("Paid in unavailable currency (fees)")

        newAlloc = Allocation(res, fees)
        newAlloc.UpdatePercentages(FX)
        return newAlloc

    def Total(self, cur: Currency = Currency.EUR):
        usedCur = self.Dictionary.keys.First()
        if cur in self.Dictionary.keys():
            usedCur = cur
        allocCur = self.Dictionary[cur]
        return Price(round(allocCur.Amount / allocCur.Percentage,2), usedCur)

    def VaR(self, q: float = 0.05,  returnSize: int = 400, n: int = 1000, scale: float = 4, printCorrelation: bool = True):
        C = Copula(list(self.Dictionary.keys()),returnSize)
        C.ComputeCorrelation()
        if (printCorrelation):
            print("Correlation Matrix (" + str(returnSize) + " returns):")
            C.PrintCorrelation()
        sim = C.Simulate(n)
        PnL = []
        for i in range(n):
            reti = sim[i]
            PnLi = 0
            j = 0
            for cur in C.CurrencyList:
                PnLi += self.Dictionary[cur].Percentage * C.Densities[cur].TransformFromStdNorm(reti[j])
                j += 1
            PnL += [PnLi]
        PnL.sort()
        return Price(round(PnL[int(n*q)] * self.Total.Amount * scale,2), self.Total.Currency)


    @property
    def ToString(self):
        res =  "Allocation: " + '\n'
        for cur in self.Dictionary.keys():
            res += cur.ToString + ": " + self.Dictionary[cur].ToString + '\n'
        res += "Fees: " + self.Fee.ToString + "\n"
        res += "Total : " + self.Total.ToString
        res += '\n'
        return res


class AllocationHistory:

    def __init__(self, TL: TransactionList, FXMH: FXMarketHistory):
        self.Currencies = FXMH.Currencies
        alloc = Allocation({})

        # Transaction List needs to be sorted before!!!!!!!!!!!!!!!!!!!!

        self.History = SortedDictionary()
        for transaction in TL.List:
            FX = FXMH.GetFXMarket(transaction.Date)
            alloc = alloc.AddTransaction(transaction,FX)
            #print(alloc.Dictionary[Currency.EUR].ToString)
            alloc.CalculateTotal(FX)
            self.History.Add(transaction.Date, alloc)
        for date in FXMH.FXMarkets.Keys:
            (alloc,test) = self.History.Get(date)
            if alloc != None and test == False:
                alloc = alloc.Move(FXMH.FXMarkets.HardGet(date))
                self.History.Add(date, alloc)


    def GetAllocation(self, date):
        return self.History.Get(date)

    def GetLastAllocation(self):
        return self.History.GetMax()

    @property
    def ToString(self):
        res = "Allocation History" + '\n'
        for date  in self.History.Keys:
            res += "Date: " + str(date) + "\n"
            res += self.History.HardGet(date).ToString + '\n'
        return res