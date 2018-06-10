import datetime

import model.events_tests


def testParametricTest():
    from model import providers
    from model import market_model
    from model import events_analyzer

    stocksPath= r'D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\stocks4Test.xlsx'
    marketPath= r'D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\s&p.xlsx'
    stocksPriceProvider = providers.ExcelDataProvider(stocksPath, 'Precios')
    stocksPriceProvider.file()
    marketPriceProvider = providers.ExcelDataProvider(marketPath, 'Precios')
    marketPriceProvider.file()
    stocksReturnsProvider = providers.ReturnDataProvider(stocksPriceProvider)
    marketReturnProvider = providers.ReturnDataProvider(marketPriceProvider)

    mm = market_model.MarketModel(stocksReturnsProvider, marketReturnProvider)
    stocksWindows = events_analyzer.StocksWindows()

    stocksWindows.addStockWindow('AAME',1 , 251, 260 )
    stocksWindows.addStockWindow('AAON',250 , 500, 509 )
    stocksWindows.addStockWindow('AAP',500 , 750, 759 )
    abnormalReturnCalc = events_analyzer.AbnormalReturnCalculator(mm)
    parametricTest = model.events_tests.RankTest2(abnormalReturnCalc)
    parametricTest.workWith(stocksWindows)
    return parametricTest.testValue()

def testSampleGenerator():
    from model.events_study import SampleGenerator
    generator = SampleGenerator(DummyStockProvider())
    return generator.generate(5, 10, 5)

def doSimulation():
    from model import providers
    from model import market_model
    from model import events_analyzer
    from model import events_study
    from model.events_study import SampleGenerator

    stocksPath = r'D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\stocks.xlsx'
    #stocksPath = r'D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\stocks4Test.xlsx'
    marketPath = r'D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\s&p.xlsx'
    stocksPriceProvider = providers.ExcelDataProvider(stocksPath, 'Precios')
    marketPriceProvider = providers.ExcelDataProvider(marketPath, 'Precios')
    stocksReturnsProvider = providers.ReturnDataProvider(stocksPriceProvider)
    marketReturnProvider = providers.ReturnDataProvider(marketPriceProvider)

    mm = market_model.MarketModel(stocksReturnsProvider, marketReturnProvider)
    shock = events_analyzer.DecreasingShock(2,10)
    abnormalReturnCalc = events_analyzer.AbnormalReturnCalculator(mm, arShock=shock)
    eventTest = model.events_tests.ParametricTest1(abnormalReturnCalc)
    stockDataProvider = providers.StockDataProvider(stocksPriceProvider)
    generator = SampleGenerator(stockDataProvider)
    simulator = events_study.Simulator(sampleGenerator=generator, testToUse=eventTest, nOfSamples=100, nOfStocksInSample=50,
                                       estimationWindowSize=250, eventWindowSize=10)
    simulator.simulate()


class DummyStockProvider:
    def stocks(self):
        #First column ignore
        return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

    def priceDates(self):
        base = datetime.date(2016,5,10)
        return [base - datetime.timedelta(days=x) for x in range(0, 50)]