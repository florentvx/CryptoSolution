from Framework.Prices import Currency
from Risk.Density import Density
from numpy import matrix, zeros, diag, sqrt, random
from pandas import DataFrame
from scipy import linalg
from typing import List

class Copula:
    def __init__(self, listCur: List[Currency], size: int, curRef: Currency = Currency.EUR):
        listCur.remove(curRef)
        self.CurrencyList = listCur
        self.N = len(self.CurrencyList)
        self.CurRef = curRef
        self.Densities = {}
        for cur in self.CurrencyList:
            d = Density(size,cur)
            d.TotalTransform()
            self.Densities[cur] = d
        self.T = len((self.Densities[self.CurrencyList[0]]).StdReturns)

    def ComputeCorrelation(self):
        A = zeros(shape = (self.N, self.T))
        for i in range(self.N):
            A[i] = self.Densities[self.CurrencyList[i]].StdReturns
        temp = DataFrame(A)
        Sigma = A.dot(matrix.transpose(A))
        Sigma /= float(self.T)
        std = []
        for i in range(self.N):
            std += [sqrt(Sigma[i,i])]
        for i in range(self.N):
            for j in range(self.N):
                Sigma[i,j] /= std[i] * std[j]
        self.Sigma = Sigma

    def PrintCorrelation(self):
        res = ""
        for i in range(10):
            res += " "
        for cur in self.CurrencyList:
            res += cur.ToString + " "
        res += "\n"
        n = len(self.CurrencyList)
        for i in range(n):
            curString = self.CurrencyList[i].ToString
            res += curString
            for k in range(10 - len(curString)):
                res += " "
            for j in range(n):
                res += " " + str(round(self.Sigma[i][j]*100,2)) + "% "
            res += "\n"
        print(res)


    def SqrtCorrel(self):
        (w,v) = linalg.eig(self.Sigma)
        wreal = []
        for i in range(self.N):
            wreal += [sqrt(w[i].real)]
        wdiag = diag(wreal)
        self.Sqrt = wdiag.dot(matrix.transpose(v))

    def Simulate(self, n: int = 10000):
        return random.multivariate_normal([0 for i in range(self.N)],self.Sigma, n)


def Example():
    C = Copula([Currency.XBT,Currency.ETH, Currency.BCH, Currency.LTC, Currency.XRP])
    #C = Copula([Currency.BCH])
    C.ComputeCorrelation()
    print(C.Sigma)
    tab = C.Simulate(10000)
    cov = matrix.transpose(tab).dot(tab)/10000

    print(cov)



