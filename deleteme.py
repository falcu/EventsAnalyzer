import datetime

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

    stocksWindows.addStockWindow('AAME',1 , 251, 261 )
    stocksWindows.addStockWindow('AAON',250 , 500, 510 )
    stocksWindows.addStockWindow('AAP',500 , 750, 760 )
    abnormalReturnCalc = events_analyzer.AbnormalReturnCalculator(mm)
    cumCalc = events_analyzer.ParametricTestByCumulativeAR(abnormalReturnCalc)
    cumCalc.workWith(stocksWindows)
    return cumCalc.testValue()

def testSampleGenerator():
    from model.events_analyzer import SampleGenerator
    generator = SampleGenerator(DummyStockProvider())
    return generator.generate(5, 10, 5)

class DummyStockProvider:
    def stocks(self):
        #First column ignore
        return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

    def priceDates(self):
        base = datetime.date(2016,5,10)
        return [base - datetime.timedelta(days=x) for x in range(0, 50)]