from scipy import stats as st
from model.decorators import computeBefore
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd

class ZScore(ABC):
    def __init__(self, alpha = 0.05):
        self.alpha = alpha

    @abstractmethod
    def isSignificant(self):
        pass

    @abstractmethod
    def zLimit(self):
        pass

class OneTailZScore(ZScore):
    def __init__(self, alpha = 0.05, side='right'):
        super().__init__(alpha)
        if side not in ['right','left']:
            raise Exception('Not supported side')
        self.side = side

    def isSignificant(self, zScore):
        zLimit = self.zLimit()
        if self.side == 'right':
            return zScore > zLimit
        else:
            return zScore < np.negative(zLimit)

    def zLimit(self):
        return st.norm.ppf(1 - self.alpha)

class TwoTailsZScore(ZScore):
    def __init__(self, alpha = 0.05 ):
        super().__init__(alpha)

    def isSignificant(self, zScore):
        zLimit = self.zLimit()
        return np.abs(zScore) > zLimit

    def zLimit(self):
        return st.norm.ppf(1 - (self.alpha/2.0))


class EventTest:
    def __init__(self, arCalculator, zScore=None):
        self.arCalculator           = arCalculator
        self.stocksWindow           = None
        self.arComputed             = False
        self.arResult               = None
        self.zScoreCalc             = self.getZScoreCalculator(zScore)
        self._wasTestValueComputed = False

    def getZScoreCalculator(self, zScore):
        return zScore or TwoTailsZScore(0.05)

    def workWith(self, stocksWindow, zScore=None):
        self.stocksWindow           = stocksWindow
        self.arComputed             = False
        self.zScoreCalc             = self.getZScoreCalculator(zScore)
        self._wasTestValueComputed  = False

    def preCompute(self):
        if not self.arComputed and self.stocksWindow:
            self.arResult = self.arCalculator.computeAR( self.stocksWindow )
            self.arComputed = True

    @computeBefore
    def testValue(self):
        if not self._wasTestValueComputed:
            self._wasTestValueComputed = True
        return self._testValueCompute()

    @abstractmethod
    def _testValueCompute(self):
        pass

    def isSignificant(self ):
        testValue = self.testValue()
        return self.zScoreCalc.isSignificant(testValue)

    def zLimit(self):
        return self.zScoreCalc.zLimit()

    @computeBefore
    def nOfEvents(self):
        return self.arResult.nOfStocks

    @abstractmethod
    def testName(self):
        pass

    @classmethod
    def makeTest(cls, arCalculator, zScoreCalc=None, testName='all'):
        testsCandidatesClass =  cls.__subclasses__()
        try:
            allTests = [testClass(arCalculator, zScoreCalc) for testClass in testsCandidatesClass]
            if testName == 'all':
                return allTests
            else:
                return next(aTest for aTest in allTests if aTest.testName()==testName)
        except:
            raise Exception('Test {} does not exist'.format(testName))

    @classmethod
    def subs(cls):
        return cls.__subclasses__()


class ParametricTest1( EventTest ):

    def __init__(self, arCalculator, zScoreCalc=None):
        super().__init__( arCalculator, zScoreCalc )

    def _testValueCompute(self):
        arEventW = self.arResult.arEventWindow
        arEstimationW = self.arResult.arEstimationWindow
        cumAccrossSecEstimationW= arEstimationW.sum(axis=1).divide( self.arResult.nOfStocks )
        oneOverT = 1.0/cumAccrossSecEstimationW.shape[0]
        standardDeviation = np.sqrt( oneOverT*cumAccrossSecEstimationW.apply(lambda value : value**2).sum(axis=0) )
        cumAccrossSecurityAvgTime0 = (arEventW.loc[arEventW.index[0],arEventW.columns].sum())\
                                            /self.arResult.nOfStocks
        return cumAccrossSecurityAvgTime0 / standardDeviation

    def testName(self):
        return 'ParametricTest1'

class ParametricTest2( EventTest ):

    def __init__(self, arCalculator, zScoreCalc=None):
        super().__init__( arCalculator, zScoreCalc )

    def _testValueCompute(self):
        arEventW = self.arResult.arEventWindow
        arEstimationW = self.arResult.arEstimationWindow
        t = arEstimationW.shape[0]
        n = self.arResult.nOfStocks
        standardDeviationAsset = arEstimationW.apply(lambda value : value**2)\
                                    .sum(axis=0).multiply(1/t).apply( lambda value : np.sqrt(value))
        standarizedAR = arEventW.divide(standardDeviationAsset)

        return standarizedAR.sum(axis=1).loc[standarizedAR.index[0]]*(1.0/np.sqrt(n))

    def testName(self):
        return 'ParametricTest2'

class RankTest(EventTest):

    def __init__(self, arCalculator, zScoreCalc=None):
        super().__init__( arCalculator, zScoreCalc )

    def _testValueCompute(self):
        arEventW = self.arResult.arEventWindow
        arEstimationW = self.arResult.arEstimationWindow
        ar = pd.concat( [arEstimationW,arEventW] ).reset_index(drop=True)
        rankMatrix = ar.rank()
        n = self.arResult.nOfStocks
        rankMean = rankMatrix.loc[rankMatrix.index,rankMatrix.columns[0]].values.mean()
        eventIndex = arEstimationW.shape[0]
        rankMatrixOfEventMinusMean = rankMatrix.loc[rankMatrix.index[eventIndex],rankMatrix.columns].sub(rankMean)

        return (rankMatrixOfEventMinusMean.sum()/n)/self._computeStandardDeviation(rankMatrix,rankMean)

    def _computeStandardDeviation(self, rankMatrix, rankMean):
        rankMatrixMinusMean = rankMatrix.sub(rankMean)
        n = self.arResult.nOfStocks
        t = rankMatrix.shape[0]
        sumAccrossSecurities = rankMatrixMinusMean.sum( axis=1 )
        sumAccrossSecurities=sumAccrossSecurities.div(n).apply( lambda value: value**2)
        sumAccrossTime = sumAccrossSecurities.sum( axis=0 )

        return np.sqrt(sumAccrossTime/t)

    def testName(self):
        return 'RankTest'

class SignTest(EventTest):

    def __init__(self, arCalculator, zScoreCalc=None):
        super().__init__( arCalculator, zScoreCalc )

    def _testValueCompute(self):
        allCount, positiveCount = self._count()
        return ((positiveCount/allCount) - 0.5)*np.sqrt(allCount)/0.5

    def _count(self):
        oneDimensionValues = np.concatenate(self.arResult.arEventWindow.values)
        return len(oneDimensionValues), sum(n>0 for n in oneDimensionValues)

    def testName(self):
        return 'SignTest'

class EventTestSet:
    def __init__(self, tests=None):
        self._tests = tests or []

    def addTest(self, aTest):
        self._tests.append( aTest )

    def workWith(self, stocksWindow, zScore=None):
        for aTest in self._tests:
            aTest.workWith( stocksWindow, zScore)

    def allTests(self):
        return self._tests

    def allTestNames(self):
        return [t.testName() for t in self.allTests()]

#Additional:
# class ParametricTestByCumulativeAR(EventTest):
#
#     def __init__(self, arCalculator):
#         super().__init__( arCalculator )
#
#     @computeBefore
#     def cumulativeAR(self):
#         cumAccrossSecurity = self.arResult.arEventWindow.sum( axis = 1 )
#         cumAccrossSecurityAvg = cumAccrossSecurity.divide( self.arResult.nOfStocks )
#         cumAR = cumAccrossSecurityAvg.sum( axis = 0 )
#         return cumAR
#
#     @computeBefore
#     def cumulativeARVariance(self):
#         varianceOfARAcrossSecurity = self.arResult.arVariance.sum( axis = 1 ).multiply(1.0/np.power(self.arResult.nOfStocks,2.0))
#         cumulativeARVariance       = varianceOfARAcrossSecurity.sum( axis =0 )
#         return cumulativeARVariance
#
#     @computeBefore
#     def testValue(self):
#         return self.cumulativeAR() / np.sqrt( self.cumulativeARVariance() )