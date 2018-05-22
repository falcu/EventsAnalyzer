import statsmodels.formula.api as sm
import pandas as pd

class MarketModelData:
    def __init__(self):
        self.parameters  = None
        self.data        = None
        self.market_name = None
        self.stock_names = None

class ComputeWindowData:
    def __init__(self, stocks, stocksWindowData, window):
        self.stocks             = stocks
        self.stocksWindowData   = stocksWindowData
        self.window             = window

class MarketModel:
    def __init__(self, stockReturnsProvider, marketReturnProvider):
        self.stockReturnsProvider = stockReturnsProvider
        self.marketReturnProvider = marketReturnProvider

    def compute(self, computeWindowData):
        stockReturns    = self.stockReturnsProvider.computeReturns()
        marketReturns   = self.marketReturnProvider.computeReturns()
        allReturns      = pd.concat([marketReturns,stockReturns], axis=1)
        parameters = []
        marketName     = allReturns.columns[0]
        stockNames = computeWindowData.stocks
        formulaFunc = lambda stockName : '{} ~ {}'.format(stockName, marketName)
        for stockName in stockNames:
            index = computeWindowData.stocksWindowData[stockName].toIndex()
            computeReturns = allReturns.loc[allReturns.index[index],[marketName,stockName]].set_index(allReturns.index[computeWindowData.window.toIndex()])
            stockModel = sm.ols(formula=formulaFunc(stockName), data=computeReturns).fit()
            parameters.append(stockModel.params.rename_axis({'Intercept':'intercept', marketName:'beta'}).to_frame(stockName))

        result = MarketModelData()
        result.parameters = pd.concat(parameters, axis=1)
        result.data       = allReturns
        result.market_name=marketName
        result.stock_names=stockNames

        return result


