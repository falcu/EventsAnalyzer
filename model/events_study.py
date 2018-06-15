from model.events_analyzer import StocksWindows
from random import shuffle, randint
from model.events_tests import TwoTailsZScore
from matplotlib import pyplot as plt
import numpy as np

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


class SimulatorLogger:
    def __init__(self):
        self._logData = {}
        self._testNames = set([])

    def initialize(self, testSet, tag='default'):
        for aTest in testSet.allTests():
            self._addTest(aTest,tag)

    def log(self, testSet, simulation, tag='default'):
        for aTest in testSet.allTests():
            self._addTest(aTest,tag=tag)
            self._addSimulationData(self._testData(aTest.testName(),tag), aTest, simulation)

    def _testData(self, testName, tag='default'):
        return self._logData[tag][testName]

    def _addTest(self, aTest, tag='default'):
        if tag not in self._logData:
            self._logData.update({tag: {}})
        if aTest.testName() not in self._logData[tag]:
            self._logData[tag].update({aTest.testName():{'simulation':{}}})
            self._testNames.add( aTest.testName() )

    def _addSimulationData(self, testData, aTest, simulation):
        testData.update({'n_events':aTest.nOfEvents()})
        testData['simulation'].update({simulation:{'z_value':aTest.testValue(), 'z_limit':aTest.zLimit()
                                     ,'is_significant':aTest.isSignificant()}})

    def _logTags(self):
        return self._logData.keys()

    def summary(self):
        for aTestName in self._testNames:
            self._summaryOfTest(aTestName)

    def plot(self):
        logTags = self._logTags()
        plot = plt.figure('Events Analyzer')
        thePlot = plot.add_subplot(111)
        thePlot.set_ylim(0, 1)
        plt.xlabel('n')
        plt.ylabel('Prob')
        maxN = 0
        for testName in self._testNames:
            n = [self._testData(testName, aTag)['n_events'] for aTag in logTags]
            maxN = max(n+[maxN])
            significants = [[result['is_significant'] for result in self._testData(testName, aTag)['simulation'].values()] for aTag in logTags]
            is_significant = np.array([s.count(True) for s in significants])
            total          = np.array([len(s) for s in significants])
            probabilities  = is_significant/total
            thePlot.scatter(n,probabilities,s=50, label=testName)
            #thePlot.ticklabel_format(useOffset=False)
        thePlot.legend(loc='upper left')
        #plt.xticks(range(0,int(maxN*1.1)))

        plt.show()

    def _summaryOfTest(self, testName):
        print("Summary of Test {}".format(testName))
        logTags = self._logTags()
        for aTag in logTags:
            testData = self._testData(testName, aTag)
            significantResults = [result['is_significant'] for result in testData['simulation'].values()]
            significant = significantResults.count(True)
            total       = len(significantResults)
            print('{}'.format(aTag))
            print("Significant results {} out of {} ({}%)".format(significant,total,(significant/total)*100.0))

class SampleData:
    def __init__(self, sampleOfStocks, stocksWindows):
        self.sampleOfStocks = sampleOfStocks
        self.stocksWindows = stocksWindows


class Simulator:
    def __init__(self, testSet, sampleGenerator, logger=None, tag='default',
                 nOfSamples=1000, nOfStocksInSample=100, estimationWindowSize=250, eventWindowSize=10, zScoreCalc=None):
        self.testSet                = testSet
        self.sampleGenerator        = sampleGenerator
        self.logger                 = logger or SimulatorLogger()
        self.tag                    = tag
        self.nOfSamples             = nOfSamples
        self.nOfStocksInSample      = nOfStocksInSample
        self.estimationWindowSize   = estimationWindowSize
        self.eventWindowSize        = eventWindowSize
        self.zScoreCalc             = zScoreCalc or TwoTailsZScore(0.05)

    def simulate(self):
        self.logger.initialize(self.testSet, tag=self.tag)
        for i in range(0,self.nOfSamples):
            self._doRun(i+1)

    def _doRun(self,sampleNumber):
        sampleData = self.sampleGenerator.generate(self.nOfStocksInSample, self.estimationWindowSize, self.eventWindowSize)
        self.testSet.workWith( sampleData.stocksWindows, zScore=self.zScoreCalc )
        self.logger.log( self.testSet, sampleNumber, tag=self.tag )