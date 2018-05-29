import pandas as pd
from model.decorators import computeBefore


class ExcelDataProvider:
    def __init__(self, fileName, sheetName):
        self.fileName    = fileName
        self.sheetName   = sheetName
        self._file        = None
        self._loaded     = False

    def preCompute(self):
        if not self._loaded:
            self._loaded = True
            self._file = pd.read_excel( self.fileName, self.sheetName)

    @computeBefore
    def file(self):
        return self._file

    @computeBefore
    def headers(self):
        return self._file.columns.values

class ReturnDataProvider:
    def __init__(self, pricesProvider):
        self.pricesProvider = pricesProvider

    def computeReturns(self):
        prices = self._pricesMatrix()
        zeroToTMinus1Prices = prices.loc[prices.index[0:-1]]
        oneToTPrices        = prices.loc[prices.index[1:]].set_index(zeroToTMinus1Prices.index)
        stockReturns        = oneToTPrices.sub(zeroToTMinus1Prices).divide(zeroToTMinus1Prices )

        return stockReturns

    def computeMean(self):
        return self._pricesMatrix().mean(axis=0)

    def computeVariance(self):
        return self._pricesMatrix().var(axis=0)

    def _pricesMatrix(self):
        # Assume first column has dates
        prices = self.pricesProvider.file()
        return prices.loc[prices.index, prices.columns[1:]]

class StockDataProvider:
    def __init__(self, stockProvider):
        self._stockProvider = stockProvider

    def stocks(self):
        #First column ignore
        return self._stockProvider.headers()[1:]

    def priceDates(self):
        data = self._stockProvider.file()
        return data.loc[data.index[0]].values()

