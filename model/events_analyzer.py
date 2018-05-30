import pandas as pd
import numpy as np
from model.decorators import computeBefore
import scipy.stats as st

class AbnormalReturnResult:
    def __init__(self, ar, arVariance, nOfStocks ):
        self.ar = ar
        self.arVariance = arVariance
        self.nOfStocks = nOfStocks

class AbnormalReturnCalculator:
    def __init__(self, marketModel):
        self.marketModel = marketModel

    def computeAR(self, stocksWindows):
        marketModelResult                       = self.marketModel.compute(stocksWindows)
        allReturnsMatrix                        = marketModelResult.allReturnsMatrix
        estimatedParams                         = marketModelResult.estimatedParameters
        stocksReturns                           = allReturnsMatrix.loc[allReturnsMatrix.index,allReturnsMatrix.columns[1:]]
        marketReturns                           = allReturnsMatrix.loc[allReturnsMatrix.index,allReturnsMatrix.columns[0:1]]
        abnormalReturns                         = []
        abnormalReturnsVariance                 = []
        for aStock in stocksWindows.stocks():
            window                              =stocksWindows.getStockWindow(aStock)
            eventWindow                         = window.eventWindow()
            standarizedIndexEventWindow         = eventWindow.toIndexStandarized()
            # Compute AR
            stockReturnsEventWindow             = stocksReturns.loc[stocksReturns.index[eventWindow.toIndex()], [aStock] ]\
                                                        .set_index(stocksReturns.index[standarizedIndexEventWindow])
            marketReturnsEventWindow            = marketReturns.loc[marketReturns.index[eventWindow.toIndex()] ]\
                                                        .set_index(marketReturns.index[standarizedIndexEventWindow] )
            marketReturnsEventWindow.columns    = [aStock]
            alpha                               = estimatedParams.loc['intercept', aStock]
            beta                                = estimatedParams.loc['beta', aStock]
            marketModelReturnsEventWindow       = marketReturnsEventWindow.multiply(beta).add(alpha)
            abnormalReturns.append( stockReturnsEventWindow.sub(marketModelReturnsEventWindow) )
            #Compute AR Variance
            residVariance                        = estimatedParams.loc['resid_variance', aStock]
            oneOverL1                            = 1.0/window.L1()
            marketMean                           = estimatedParams.loc['market_mean', aStock]
            marketVariance                       = estimatedParams.loc['market_variance', aStock]

            additionalVariance                   = marketReturnsEventWindow.sub(marketMean).apply(lambda v : np.power(v,2))\
                                                        .divide(marketVariance).add(1.0).multiply(oneOverL1)
            finalVariance                         = additionalVariance.add(residVariance)
            finalVariance.columns                 = [aStock]
            abnormalReturnsVariance.append(finalVariance)

        ar = pd.concat(abnormalReturns, axis=1)
        arVariance = pd.concat(abnormalReturnsVariance, axis=1)

        return AbnormalReturnResult( ar, arVariance, ar.shape[1] )

class ParametricTestByCumulativeAR:

    def __init__(self, arCalculator):
        self.arCalculator = arCalculator
        self.stocksWindow = None
        self.arComputed   = False
        self.arResult     = None

    def workWith(self, stocksWindow):
        self.stocksWindow = stocksWindow
        self.arComputed = False

    def preCompute(self):
        if not self.arComputed and self.stocksWindow:
            self.arResult = self.arCalculator.computeAR( self.stocksWindow )
            self.arComputed = True

    @computeBefore
    def cumulativeAR(self):
        cumAccrossSecurity = self.arResult.ar.sum( axis = 1 )
        cumAccrossSecurityAvg = cumAccrossSecurity.divide( self.arResult.nOfStocks )
        cumAR = cumAccrossSecurityAvg.sum( axis = 0 )
        return cumAR

    @computeBefore
    def cumulativeARVariance(self):
        varianceOfARAcrossSecurity = self.arResult.arVariance.sum( axis = 1 ).multiply(1.0/np.power(self.arResult.nOfStocks,2.0))
        cumulativeARVariance       = varianceOfARAcrossSecurity.sum( axis =0 )
        return cumulativeARVariance

    def testValue(self):
        return self.cumulativeAR() / np.sqrt( self.cumulativeARVariance() )

    def isSignificant(self, alpha=0.05, twoTails=True ):
        significance = alpha/2.0 if twoTails else alpha
        zScore = st.norm.ppf(1-significance)
        testValue = self.testValue()
        print("Test value: {}, zScore: {}".format(testValue, zScore))
        return np.abs(testValue)>=zScore


class StocksWindows:
    def __init__(self,windowBuilder=None):
        self._stocksWindows = {}
        self._windowBuilder = windowBuilder or IntegerWindowBuilder

    def addStockWindow(self, stock, t1,t2, t3 ):
        self._stocksWindows.update( {stock: Window(  t1, t2, t3) } )

    def stocks(self):
        return list( self._stocksWindows.keys() )

    def getStockWindow(self, aStock):
        if aStock not in self._stocksWindows:
            raise Exception('{} not present'.format( aStock ))
        return self._stocksWindows[aStock]


class Window:
    def __init__(self, t1, t2, t3, windowBuilder=None):
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.windowBuilder = windowBuilder or IntegerWindowBuilder
        self._estimationWindow = self.windowBuilder.buildEstimationWindow(self)
        self._eventWindow      = self.windowBuilder.buildEventWindow(self)

    def estimationWindow(self):
        return self._estimationWindow

    def eventWindow(self):
        return self._eventWindow

    def L1(self):
        return self._estimationWindow.elapsed()

    def L2(self):
        return self._eventWindow.elapsed()

class IntegerWindowBuilder:
     @classmethod
     def buildEstimationWindow(cls, window):
         return IntegerIndexWindow(window.t1, window.t2-1)

     @classmethod
     def buildEventWindow(cls, window):
         return IntegerIndexWindow(window.t2, window.t3)


class IntegerIndexWindow:
    def __init__(self, start, end):
        self.start = start
        self.end   = end

    def toIndex(self):
        return [i for i in range(self.start,self.end)]

    def toIndexStandarized(self):
        return [i for i in range(0, self.end - self.start)]

    def elapsed(self):
        return self.end - self.start


