import numpy as np
import pandas as pd


class AbnormalReturnResult:
    def __init__(self, arEventWindow, arEstimationWindow, arVariance, nOfStocks ):
        self.arEventWindow = arEventWindow
        self.arEstimationWindow = arEstimationWindow
        self.arVariance = arVariance
        self.nOfStocks = nOfStocks

class NullAbnormalReturnShock:
    def doShock(self, stockReturnsEventWindow):
        return stockReturnsEventWindow

class DecreasingShock:
    def __init__(self, volatilityFactor, theLambda ):
        self.volatilityFactor = volatilityFactor
        self.theLambda          = theLambda

    def doShock(self, stockReturnsEventWindow):
        increasingIntegerMatrix = pd.DataFrame([ [i]*stockReturnsEventWindow.shape[1] for i in range(stockReturnsEventWindow.shape[0])])
        n0 = self._n0(stockReturnsEventWindow)
        shockValueFunc = lambda value : n0 * np.exp(-value/self.theLambda)
        shockMatrix = increasingIntegerMatrix.apply(shockValueFunc).set_index(stockReturnsEventWindow.index)
        shockMatrix.columns = stockReturnsEventWindow.columns

        return shockMatrix

    def _n0(self, stockReturnsEventWindow):
        stockVolat = np.sqrt( stockReturnsEventWindow.var()[0] )
        return self.volatilityFactor*stockVolat



class AbnormalReturnCalculator:
    def __init__(self, marketModel, arShock=None):
        self.marketModel = marketModel
        self.arShock = arShock or NullAbnormalReturnShock()

    def computeAR(self, stocksWindows):
        marketModelResult                       = self.marketModel.compute(stocksWindows)
        allReturnsMatrix                        = marketModelResult.allReturnsMatrix
        estimatedParams                         = marketModelResult.estimatedParameters
        stocksReturns                           = allReturnsMatrix.loc[allReturnsMatrix.index,allReturnsMatrix.columns[1:]]
        marketReturns                           = allReturnsMatrix.loc[allReturnsMatrix.index,allReturnsMatrix.columns[0:1]]
        abnormalReturnsEventWindow              = []
        abnormalReturnsEstimationWindow         = []
        abnormalReturnsVariance                 = []
        for aStock in stocksWindows.stocks():
            window                                  = stocksWindows.getStockWindow(aStock)
            eventWindow                             = window.eventWindow()
            estimationWindow                        = window.estimationWindow()
            standarizedIndexEventWindow             = eventWindow.toIndexStandarized()
            standarizedIndexEstimationWindow        = estimationWindow.toIndexStandarized()
            # Compute AR
            stockReturnsEventWindow                 = stocksReturns.loc[stocksReturns.index[eventWindow.toIndex()], [aStock] ]\
                                                        .set_index(stocksReturns.index[standarizedIndexEventWindow])
            stockReturnsEstimationWindow            = stocksReturns.loc[stocksReturns.index[estimationWindow.toIndex()], [aStock] ]\
                                                        .set_index(stocksReturns.index[standarizedIndexEstimationWindow])
            marketReturnsEventWindow                = marketReturns.loc[marketReturns.index[eventWindow.toIndex()] ]\
                                                        .set_index(marketReturns.index[standarizedIndexEventWindow] )
            marketReturnsEstimationWindow           = marketReturns.loc[marketReturns.index[estimationWindow.toIndex()]] \
                                                        .set_index(marketReturns.index[standarizedIndexEstimationWindow])

            stockReturnsEventWindow                 = self.arShock.doShock( stockReturnsEventWindow )
            marketReturnsEventWindow.columns        = [aStock]
            marketReturnsEstimationWindow.columns   = [aStock]
            alpha                                   = estimatedParams.loc['intercept', aStock]
            beta                                    = estimatedParams.loc['beta', aStock]
            marketModelReturnsEventWindow           = marketReturnsEventWindow.multiply(beta).add(alpha)
            marketModelReturnsEstimationWindow      = marketReturnsEstimationWindow.multiply(beta).add(alpha)
            stockAREventWindow                      = stockReturnsEventWindow.sub(marketModelReturnsEventWindow)
            stockAREstimationWindow                 = stockReturnsEstimationWindow.sub(marketModelReturnsEstimationWindow)
            abnormalReturnsEventWindow.append( stockAREventWindow )
            abnormalReturnsEstimationWindow.append( stockAREstimationWindow )
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

        arEventWindow = pd.concat(abnormalReturnsEventWindow, axis=1)
        arEstimationWindow = pd.concat(abnormalReturnsEstimationWindow, axis=1)
        arVariance = pd.concat(abnormalReturnsVariance, axis=1)

        return AbnormalReturnResult( arEventWindow, arEstimationWindow, arVariance, len(stocksWindows.stocks()) )


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
         return IntegerIndexWindow(window.t1, window.t2)

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


