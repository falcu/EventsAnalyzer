import datetime

def test():
    import pandas as pd
    df = pd.DataFrame([[1, 2], [3, 4], [5, 6], [7, 8]], columns=['A', 'B'])
    df.iloc[df.index[0:],df.columns.get_indexer(['A'])]

def test2():
    import providers
    stocksPath= r'D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\stocks.xlsx'
    marketPath= r'D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\s&p.xlsx'
    stocksPriceProvider = providers.ExcelDataProvider(stocksPath,'Precios')
    marketPriceProvider = providers.ExcelDataProvider(marketPath,'Precios')
    stocksReturnsProvider = providers.ReturnDataProvider(stocksPriceProvider)
    marketReturnProvider = providers.ReturnDataProvider(marketPriceProvider)

    return stocksReturnsProvider, marketReturnProvider

def test3():
    import providers
    import market_model
    import events_analyzer

    stocksPath= r'D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\stocks.xlsx'
    marketPath= r'D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\s&p.xlsx'
    stocksPriceProvider = providers.ExcelDataProvider(stocksPath,'Precios')
    stocksPriceProvider.file()
    marketPriceProvider = providers.ExcelDataProvider(marketPath,'Precios')
    marketPriceProvider.file()
    stocksReturnsProvider = providers.ReturnDataProvider(stocksPriceProvider)
    marketReturnProvider = providers.ReturnDataProvider(marketPriceProvider)

    mm = market_model.MarketModel(stocksReturnsProvider,marketReturnProvider)
    stocksWindows = events_analyzer.StocksWindows()
    stocksWindows.addStockWindow('XOM',1 , 251, 261 )
    stocksWindows.addStockWindow('ABV',250 , 500, 510 )
    abnormalReturnCalc = events_analyzer.AbnormalReturnCalculator( mm )
    cumCalc = events_analyzer.CumulativeCalculator()

    return cumCalc.cumulativeAR( abnormalReturnCalc, stocksWindows )

def testSampleGenerator():
    from events_analyzer import SampleGenerator
    generator = SampleGenerator(DummyStockProvider())
    return generator.generate(5, 10, 5)

class DummyStockProvider:
    def stocks(self):
        #First column ignore
        return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

    def priceDates(self):
        base = datetime.date(2016,5,10)
        return [base - datetime.timedelta(days=x) for x in range(0, 50)]