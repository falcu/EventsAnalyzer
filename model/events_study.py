from model.events_analyzer import StocksWindows
from random import shuffle, randint
from model.events_tests import TwoTailsZScore

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
        numberOfDates = len(self._stockDataProvider.returnDates())
        t2 = randint(estimationWindowLength, numberOfDates - 1 - eventsWindowLength)  #Day of event
        t1 = t2 - estimationWindowLength
        t3 = t2 + eventsWindowLength

        return t1, t2, t3


class SampleData:
    def __init__(self, sampleOfStocks, stocksWindows):
        self.sampleOfStocks = sampleOfStocks
        self.stocksWindows = stocksWindows


class Simulator:
    def __init__(self, nOfSamples=1000, nOfStocksInSample=100, estimationWindowSize=250, eventWindowSize=10,
                 sampleGenerator=None, testToUse=None, zScoreCalc=None):
        self.nOfSamples             = nOfSamples
        self.nOfStocksInSample      = nOfStocksInSample
        self.estimationWindowSize   = estimationWindowSize
        self.eventWindowSize        = eventWindowSize
        self.sampleGenerator        = sampleGenerator
        self.testToUse              = testToUse
        self.significantQuant       = 0
        self.zScoreCalc             = zScoreCalc or TwoTailsZScore(0.05)

    def simulate(self):
        for i in range(0,self.nOfSamples):
            self._doRun(i+1)
            print('Significant {} out of {} ({}%)'.format(self.significantQuant, i+1,
                                                          (self.significantQuant / (i+1)) * 100.0))

        print('------------------------------')
        print('Significant {} out of {} ({}%)'.format(self.significantQuant,self.nOfSamples,self.significantQuant/self.nOfSamples*100.0))

    def _doRun(self,sampleNumber):
        print('Sample {}'.format(sampleNumber))
        sampleData = self.sampleGenerator.generate(self.nOfStocksInSample, self.estimationWindowSize, self.eventWindowSize)
        self.testToUse.workWith( sampleData.stocksWindows, zScore=self.zScoreCalc )
        if self.testToUse.isSignificant():
            self.significantQuant+=1
            print("Is Significant")
        else:
            print("Not Significant")