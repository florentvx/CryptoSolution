from enum import Enum, auto



class Currency(Enum):
    NONE = "NONE"
    EUR = "EUR"
    USD = "USD"
    XBT = "XBT"
    ETH = "ETH"
    BCH = "BCH"
    XRP = "XRP"
    LTC = "LTC"

    @property
    def ToID(self):
        return str(self._name_)

    @property
    def ToString(self):
        if self == Currency.NONE:
            return "None"
        elif self == Currency.EUR:
            return "Euro"
        elif self == Currency.XBT:
            return "BitCoin"
        elif self == Currency.ETH:
            return "Ether"
        elif self == Currency.BCH:
            return "BitCoinCash"
        elif self == Currency.LTC:
            return "LiteCoin"
        elif self == Currency.XRP:
            return "Ripple"
        else:
            Exception("Currency Error")

    @property
    def Prefix(self):
        if self == Currency.EUR or self == Currency.USD:
            return "Z"
        else:
            return "X"

class Price:

    def __init__(self, amount: float, currency):

        self.Amount = amount

        if(type(currency) == Currency):
            self.Currency = currency
        elif(type(currency) == str):
            try:
                self.Currency = Currency[currency]
            except:
                self.Currency = Currency.NONE
        else:
            self.Currency = Currency.NONE

    @property
    def Copy(self):
        return Price(self.Amount, self.Currency)

    @property
    def ToString(self):
        return str(round(self.Amount,6)) + " " + self.Currency.ToString


class CurrencyPair:

    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    @property
    def ToString(self):
        return self.X.ToString + " / " + self.Y.ToString

    @property
    def RequestID(self):
        if self.X != Currency.BCH and self.X != Currency.LTC:
            return self.X.Prefix + self.X.ToID + self.Y.Prefix + self.Y.ToID
        else:
            return self.X.ToID + self.Y.ToID

    def GetInverse(self):
        return CurrencyPair(self.Y, self.X)

class XChangeRate:

    def __init__(self, rate: float, X, Y):

        self.Rate = rate
        self.CurPair = CurrencyPair(X,Y)

    @property
    def GetInverse(self):
        return XChangeRate(1/self.Rate, self.CurPair.Y, self.CurPair.X)

    @property
    def ToString(self):
        return str(self.Rate) + " " + self.CurPair.ToString