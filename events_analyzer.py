import pandas as pd
from decorators import computeBefore

class AbnormalReturnResult:
    def __init__(self, ar, nOfStocks, l2 ):
        self.ar = ar
        self.nOfStocks = nOfStocks
        self.l2 = l2

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
        for aStock in stocksWindows.stocks():
            eventWindow                         = stocksWindows.getStockWindow(aStock).eventWindow()
            standarizedIndex                    = eventWindow.toIndexStandarized()
            stockReturnsEventWindow             = stocksReturns.loc[stocksReturns.index[eventWindow.toIndex()], [aStock] ]\
                                                        .set_index(stocksReturns.index[standarizedIndex])
            marketReturnsEventWindow            = marketReturns.loc[marketReturns.index[eventWindow.toIndex()] ]\
                                                        .set_index(marketReturns.index[standarizedIndex] )
            marketReturnsEventWindow.columns    = [aStock]
            beta                                = estimatedParams.loc[estimatedParams.index[1:2], [aStock]]
            alpha                               = estimatedParams.loc[estimatedParams.index[0:1], [aStock]]
            betaRow                             = pd.concat([beta]*marketReturnsEventWindow.shape[0], axis=0)
            betaRow                             = betaRow.set_index(marketReturnsEventWindow.index[standarizedIndex])
            betaRow.columns                     = [aStock]
            alphaRow                            = pd.concat([alpha]*marketReturnsEventWindow.shape[0], axis=0)
            alphaRow                            = alphaRow.set_index(marketReturnsEventWindow.index[standarizedIndex])
            alphaRow.columns                    = [aStock]
            marketModelReturnsEventWindow       = marketReturnsEventWindow.multiply(betaRow).add(alphaRow)
            abnormalReturns.append( stockReturnsEventWindow.sub(marketModelReturnsEventWindow) )
        ar = pd.concat(abnormalReturns, axis=1)
        return AbnormalReturnResult( ar, ar.shape[1], ar.shape[0] )

class CumulativeCalculator:

    def cumulativeAR(self, arCalculator, stocksWindows):
        arResult = arCalculator.computeAR( stocksWindows )
        cumAccrossSecurity = arResult.ar.sum( axis = 1 )
        cumAccrossSecurityAvg = cumAccrossSecurity.divide( arResult.nOfStocks )
        cumAR = cumAccrossSecurityAvg.sum( axis = 0 )
        return cumAR

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

    def estimationWindow(self):
        return self.windowBuilder.buildEstimationWindow(self)

    def eventWindow(self):
        return self.windowBuilder.buildEventWindow(self)

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

