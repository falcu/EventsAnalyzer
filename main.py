from model import providers
from model import market_model
from model import events_analyzer
from model import events_study
from model.events_study import SampleGenerator
from model import events_tests

def main(stocksPath=r'D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\stocks.xlsx',
         marketPath=r'D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\s&p.xlsx',
         shock=False, lambdaShock=1, sigmaShockFactor=2, testName='ParametricTest1',
         nOfSamples=1000, nOfStocks=100, estimationWindowSize=250, eventWindowSize=10):

    print('Using {} '.format(testName))

    stocksPriceProvider = providers.ExcelDataProvider(stocksPath, 'Precios')
    marketPriceProvider = providers.ExcelDataProvider(marketPath, 'Precios')
    stocksReturnsProvider = providers.ReturnDataProvider(stocksPriceProvider)
    marketReturnProvider = providers.ReturnDataProvider(marketPriceProvider)

    mm = market_model.MarketModel(stocksReturnsProvider, marketReturnProvider)
    shock = events_analyzer.DecreasingShock(sigmaShockFactor,lambdaShock) if shock else None
    abnormalReturnCalc = events_analyzer.AbnormalReturnCalculator(mm, arShock=shock)
    eventTest = events_tests.EventTest.makeTest(testName, abnormalReturnCalc)
    stockDataProvider = providers.StockDataProvider(stocksPriceProvider)
    generator = SampleGenerator(stockDataProvider)
    simulator = events_study.Simulator(sampleGenerator=generator, testToUse=eventTest, nOfSamples=nOfSamples, nOfStocksInSample=nOfStocks,
                                       estimationWindowSize=estimationWindowSize, eventWindowSize=eventWindowSize)

    simulator.simulate()

if __name__ == '__main__':
    main()