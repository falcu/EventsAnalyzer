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
    marketPriceProvider = providers.ExcelDataProvider(marketPath,'Precios')
    stocksReturnsProvider = providers.ReturnDataProvider(stocksPriceProvider)
    marketReturnProvider = providers.ReturnDataProvider(marketPriceProvider)

    mm = market_model.MarketModel(stocksReturnsProvider,marketReturnProvider)
    windowXOM = events_analyzer.IntegerIndexWindow(1,251)
    windowABV = events_analyzer.IntegerIndexWindow(250,500)
    window    = events_analyzer.IntegerIndexWindow(0,250)
    windowsData = market_model.ComputeWindowData(['XOM','ABV'], {'XOM':windowXOM, 'ABV':windowABV}, window)
    return mm.compute(windowsData)