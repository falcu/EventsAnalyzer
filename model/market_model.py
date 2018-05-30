import statsmodels.formula.api as sm
import pandas as pd

class MarketModelData:
    def __init__(self, estimatedParameters, allReturnsMatrix, marketName, marketMean, marketVariance):
        self.estimatedParameters    = estimatedParameters
        self.allReturnsMatrix       = allReturnsMatrix
        self.marketName             = marketName
        self.marketMean             = marketMean
        self.marketVariance         = marketVariance

class MarketModel:
    def __init__(self, stockReturnsProvider, marketReturnProvider):
        self.stockReturnsProvider = stockReturnsProvider
        self.marketReturnProvider = marketReturnProvider

    def compute(self, stocksWindows):
        stocksReturnsMatrix     = self.stockReturnsProvider.computeReturns()
        marketReturnsMatrix     = self.marketReturnProvider.computeReturns()
        allReturnsMatrix        = pd.concat([marketReturnsMatrix,stocksReturnsMatrix], axis=1)
        parameters              = []
        marketName              = allReturnsMatrix.columns[0]
        stockNames              = stocksWindows.stocks()
        def formulaFunc(stockName) : return '{} ~ {}'.format(stockName, marketName)
        for stockName in stockNames:
            estimationWindow    = stocksWindows.getStockWindow(stockName).estimationWindow()
            computeReturns      = allReturnsMatrix.loc[allReturnsMatrix.index[estimationWindow.toIndex()],[marketName,stockName]]\
                                                .set_index(allReturnsMatrix.index[estimationWindow.toIndexStandarized()])
            stockModel = sm.ols(formula=formulaFunc(stockName), data=computeReturns).fit()
            currentParams = stockModel.params.rename_axis({'Intercept':'intercept', marketName:'beta'})
            marketVariance = self.marketReturnProvider.computeVariance(index=estimationWindow.toIndex()).values[0]
            marketMean = self.marketReturnProvider.computeMean(index=estimationWindow.toIndex()).values[0]
            currentParams = currentParams.append( pd.Series({'resid_variance':stockModel.mse_resid,
                                                 'market_mean':marketMean, 'market_variance':marketVariance}))

            parameters.append(currentParams.to_frame(stockName))
            #mse_resid  is the variance of residuals
        estimatedParameters = pd.concat(parameters, axis=1)

        return MarketModelData( estimatedParameters, allReturnsMatrix, marketName, marketMean, marketVariance)


