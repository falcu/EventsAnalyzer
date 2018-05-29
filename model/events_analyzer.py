from random import shuffle, randint
import pandas as pd
import numpy as np
from model.decorators import computeBefore

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
            # Compute AR
            eventWindow                         = window.eventWindow()
            standarizedIndexEventWindow         = eventWindow.toIndexStandarized()
            stockReturnsEventWindow             = stocksReturns.loc[stocksReturns.index[eventWindow.toIndex()], [aStock] ]\
                                                        .set_index(stocksReturns.index[standarizedIndexEventWindow])
            marketReturnsEventWindow            = marketReturns.loc[marketReturns.index[eventWindow.toIndex()] ]\
                                                        .set_index(marketReturns.index[standarizedIndexEventWindow] )
            marketReturnsEventWindow.columns    = [aStock]
            alpha                               = estimatedParams.loc[estimatedParams.index[0:1], [aStock]]
            beta                                = estimatedParams.loc[estimatedParams.index[1:2], [aStock]]
            betaRow                             = pd.concat([beta]*marketReturnsEventWindow.shape[0], axis=0)
            betaRow                             = betaRow.set_index(marketReturnsEventWindow.index[standarizedIndexEventWindow])
            betaRow.columns                     = [aStock]
            alphaRow                            = pd.concat([alpha]*marketReturnsEventWindow.shape[0], axis=0)
            alphaRow                            = alphaRow.set_index(marketReturnsEventWindow.index[standarizedIndexEventWindow])
            alphaRow.columns                    = [aStock]
            marketModelReturnsEventWindow       = marketReturnsEventWindow.multiply(betaRow).add(alphaRow)
            abnormalReturns.append( stockReturnsEventWindow.sub(marketModelReturnsEventWindow) )
            #Compute AR Variance
            estimationWindow                     = window.estimationWindow()
            standarizedIndexEstimationWindow     = estimationWindow.toIndexStandarized()
            marketReturnsEstimationWindow        = marketReturns.loc[marketReturns.index[estimationWindow.toIndex()]] \
                .set_index(marketReturns.index[standarizedIndexEstimationWindow])
            commonIndex                          = marketReturnsEstimationWindow.index[standarizedIndexEstimationWindow]
            columnLength                         = marketReturnsEstimationWindow.shape[0]
            residVariance                        = estimatedParams.loc[estimatedParams.index[2:3], [aStock]]
            residVarianceColumnVector            = self._makeColumnVectorFromValue(residVariance.values[0][0],columnLength,marketModelResult.marketName,
                                                                                   commonIndex)
            L1Minus1ColumnVector                 = self._makeColumnVectorFromValue(1.0/window.L1(),columnLength,marketModelResult.marketName,
                                                                                   commonIndex)
            marketMeanColumnVector               = self._makeColumnVectorFromValue(marketModelResult.marketMean,columnLength,marketModelResult.marketName,
                                                                                   commonIndex)
            marketVarianceColumnVector           = self._makeColumnVectorFromValue(marketModelResult.marketVariance,columnLength,marketModelResult.marketName,
                                                                                   commonIndex)
            onesColumnVector                     = self._makeColumnVectorFromValue(1,columnLength,marketModelResult.marketName,
                                                                                   commonIndex)

            additionalVariance                   = marketReturnsEstimationWindow.sub(marketMeanColumnVector).apply(lambda v : np.power(v,2))\
                                                        .divide(marketVarianceColumnVector).add(onesColumnVector).multiply(L1Minus1ColumnVector)
            finalVariance                         = residVarianceColumnVector.add(additionalVariance)
            finalVariance.columns                 = [aStock]
            abnormalReturnsVariance.append(finalVariance)

        ar = pd.concat(abnormalReturns, axis=1)
        arVariance = pd.concat(abnormalReturnsVariance, axis=1)

        return AbnormalReturnResult( ar, arVariance, ar.shape[1] )

    def _makeColumnVectorFromValue(self, value, length, columnName, index=None):
        valueAsDF = pd.DataFrame( [value], columns=[columnName] )
        valueColumnVector = pd.concat([valueAsDF] * length, axis=0)
        valueColumnVector.columns = [columnName]
        if not index is None:
            valueColumnVector=valueColumnVector.set_index(index)
        return valueColumnVector

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
        varianceOfARAcrossSecurity = self.arResult.arVariance.sum( axis = 1 ).multiply(1/np.power(self.arResult.nOfStocks,2))
        cumulativeARVariance       = varianceOfARAcrossSecurity.sum( axis =0 )
        return cumulativeARVariance

    def testValue(self):
        return self.cumulativeAR() / self.cumulativeARVariance()


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

class SampleGenerator:
    def __init__(self, stockDataProvider):
        self._stockDataProvider = stockDataProvider

    def generate(self, numberOfStocks, estimationWindowLength, eventsWindowLength, windowBuilder=None):
        stocksSample = self._stocksSample(numberOfStocks)
        stocksWindows = StocksWindows(windowBuilder=windowBuilder)
        for aStock in stocksSample:
            t1, t2, t3 = self._buildWindowSample(estimationWindowLength, eventsWindowLength)
            stocksWindows.addStockWindow(aStock, t1, t2, t3)

        return SampleData(stocksSample, stocksWindows)

    def _stocksSample(self, numberOfStocks):
        allStocks = self._stockDataProvider.stocks()
        shuffle(allStocks)
        return allStocks[0:numberOfStocks]

    def _buildWindowSample(self, estimationWindowLength, eventsWindowLength):
        numberOfDates = len(self._stockDataProvider.priceDates())
        t2 = randint(estimationWindowLength, numberOfDates - eventsWindowLength)  #Day of event
        t1 = t2 - estimationWindowLength
        t3 = t2 + eventsWindowLength

        return t1, t2, t3


class SampleData:
    def __init__(self, sampleOfStocks, stocksWindows):
        self.sampleOfStocks = sampleOfStocks
        self.stocksWindows = stocksWindows


