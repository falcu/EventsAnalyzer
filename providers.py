import pandas as pd
from decorators import computeBefore

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
        return self._file.columns

class ReturnDataProvider:
    def __init__(self, pricesProvider):
        self.pricesProvider = pricesProvider

    def computeReturns(self):
        prices = self.pricesProvider.file()
        #Assume first column has dates
        zeroToTMinus1Prices = prices.loc[prices.index[0:-1], prices.columns[1:]]
        oneToTPrices        = prices.loc[prices.index[1:], prices.columns[1:]].set_index(zeroToTMinus1Prices.index)
        stockReturns        = oneToTPrices.sub(zeroToTMinus1Prices).divide(zeroToTMinus1Prices )

        return stockReturns

