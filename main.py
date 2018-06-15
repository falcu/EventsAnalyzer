from model import providers
from model import market_model
from model import events_analyzer
from model import events_study
from model.events_study import SampleGenerator, SimulatorLogger
from model import events_tests
from argparse import ArgumentParser

def main(**kwargs):
    parser = ArgumentParser(description='Event Analyzer')
    parser.add_argument('-sf', '--stock_file', help='Stock file path', required=True, type=str)
    parser.add_argument('-mf', '--market_file', help='Market file path', required=True, type=str)
    parser.add_argument('-nsa', '--n_samples', help='Number of samples', required=False, type=int, default=10)
    parser.add_argument('-nst', '--n_stocks', help='Number of stocks', required=False, type=int, default=10)
    parser.add_argument('-esw', '--estimation_size', help='Estimation window size', required=False, type=int, default=250)
    parser.add_argument('-evw', '--event_size', help='Event window size', required=False, type=int, default=10)
    parser.add_argument('-sh', '--shock', help='Has shock?', required=False, type=bool, default=False)
    parser.add_argument('-slam', '--shock_lambda', help='Lambda of the shock', required=False, type=int, default=1)
    parser.add_argument('-ssig', '--factor_sigma_shock', help='Sigma factor of shock', required=False, type=int, default=2)
    args = vars(parser.parse_args())
    stocksPath              = args['stock_file']
    marketPath              = args['market_file']
    nOfSamples              = args['n_samples']
    nOfStocks               = args['n_stocks']
    estimationWindowSize    = args['estimation_size']
    eventWindowSize         = args['event_size']
    shock                   = args['shock']
    lambdaShock             = args['shock_lambda']
    sigmaShockFactor        = args['factor_sigma_shock']
    #PARAMETERS
    #stocksPath = r"D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\stocks.xlsx"
    #marketPath = r"D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\s&p.xlsx"
    #nOfSamples = 1
    #nOfStocks = 100
    #estimationWindowSize = 250
    #eventWindowSize = 10
    #SHOCK PARAMETERS
    #shock = False
    #lambdaShock = 1
    #sigmaShockFactor = 2

    #SETUP
    stocksPriceProvider = providers.ExcelDataProvider(stocksPath, 'Precios')
    marketPriceProvider = providers.ExcelDataProvider(marketPath, 'Precios')
    stocksReturnsProvider = providers.ReturnDataProvider(stocksPriceProvider)
    marketReturnProvider = providers.ReturnDataProvider(marketPriceProvider)
    mm = market_model.MarketModel(stocksReturnsProvider, marketReturnProvider)
    shock = events_analyzer.DecreasingShock(sigmaShockFactor,lambdaShock) if shock else None
    tag = 'WithEvent' if shock else 'NoEvent'
    abnormalReturnCalc = events_analyzer.AbnormalReturnCalculator(mm, arShock=shock)
    eventTestSet = events_tests.EventTestSet( events_tests.EventTest.makeTest(abnormalReturnCalc, testName='all') )
    stockDataProvider = providers.StockDataProvider(stocksPriceProvider)
    generator = SampleGenerator(stockDataProvider)
    simulator = events_study.Simulator(eventTestSet, generator, tag=tag, nOfSamples=nOfSamples, nOfStocksInSample=nOfStocks,
                                       estimationWindowSize=estimationWindowSize, eventWindowSize=eventWindowSize)

    #RUN SIMULATION
    simulator.simulate()
    simulator.logger.summary()
    simulator.logger.plot()



def ej1():
    #PARAMETERS
    stocksPath = r"D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\stocks.xlsx"
    marketPath = r"D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\s&p.xlsx"
    nOfStocks = [50, 100, 150, 200]
    nOfSamples = 1000
    estimationWindowSize = 250
    eventWindowSize = 10
    #SHOCK PARAMETERS
    shock = False
    lambdaShock = 1
    sigmaShockFactor = 2

    tag = 'WithEvent' if shock else 'NoEvent'
    tags = ['{}_n_{}'.format(tag,n) for n in nOfStocks]

    # SETUP
    stocksPriceProvider = providers.ExcelDataProvider(stocksPath, 'Precios')
    marketPriceProvider = providers.ExcelDataProvider(marketPath, 'Precios')
    stocksReturnsProvider = providers.ReturnDataProvider(stocksPriceProvider)
    marketReturnProvider = providers.ReturnDataProvider(marketPriceProvider)
    mm = market_model.MarketModel(stocksReturnsProvider, marketReturnProvider)
    shock = events_analyzer.DecreasingShock(sigmaShockFactor, lambdaShock) if shock else None
    abnormalReturnCalc = events_analyzer.AbnormalReturnCalculator(mm, arShock=shock)
    eventTestSet = events_tests.EventTestSet(events_tests.EventTest.makeTest(abnormalReturnCalc, testName='all'))
    stockDataProvider = providers.StockDataProvider(stocksPriceProvider)
    generator = SampleGenerator(stockDataProvider)
    logger = SimulatorLogger()

    def _makeSimulator(tag,n):
        return events_study.Simulator(eventTestSet, generator, tag=tag, nOfSamples=nOfSamples,
                                       nOfStocksInSample=n,
                                       estimationWindowSize=estimationWindowSize, eventWindowSize=eventWindowSize, logger=logger)

    simulators = []
    for i in range(0,len(nOfStocks)):
        aTag = tags[i]
        n    = nOfStocks[i]
        aSimulator = _makeSimulator(aTag,n)
        simulators.append(aSimulator)

    # RUN SIMULATIONS
    for aSimulator in simulators:
        aSimulator.simulate()

    logger.summary()
    logger.plot()

def ej2():
    #PARAMETERS
    stocksPath = r"D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\stocks.xlsx"
    marketPath = r"D:\Guido\Master Finanzas\2018\Primer Trimestre\Metodos No Param\s&p.xlsx"
    nOfStocks = 100
    nOfSamples = 1000
    estimationWindowSize = 250
    eventWindowSize = 10
    #SHOCK PARAMETERS
    shock = True
    lambdasShock = [0.1, 1, 10]
    sigmasShockFactor = [0.5, 1, 2]

    tagPrefix = 'WithEvent' if shock else 'NoEvent'

    # SETUP
    stocksPriceProvider = providers.ExcelDataProvider(stocksPath, 'Precios')
    marketPriceProvider = providers.ExcelDataProvider(marketPath, 'Precios')
    stocksReturnsProvider = providers.ReturnDataProvider(stocksPriceProvider)
    marketReturnProvider = providers.ReturnDataProvider(marketPriceProvider)
    mm = market_model.MarketModel(stocksReturnsProvider, marketReturnProvider)
    logger = SimulatorLogger()
    def _makeSimulator(eventTestSet, generator, tag):
        return events_study.Simulator(eventTestSet, generator, tag=tag, nOfSamples=nOfSamples,
                                       nOfStocksInSample=nOfStocks,
                                       estimationWindowSize=estimationWindowSize, eventWindowSize=eventWindowSize, logger=logger)

    simulators = []
    for lambdaShock in lambdasShock:
        for sigmaShock in sigmasShockFactor:
            tag = '{}_{}_{}_{}'.format(tagPrefix,nOfStocks,lambdaShock,sigmaShock)
            shock = events_analyzer.DecreasingShock(sigmaShock, lambdaShock) if shock else None
            abnormalReturnCalc = events_analyzer.AbnormalReturnCalculator(mm, arShock=shock)
            eventTestSet = events_tests.EventTestSet(events_tests.EventTest.makeTest(abnormalReturnCalc, testName='all'))
            stockDataProvider = providers.StockDataProvider(stocksPriceProvider)
            generator = SampleGenerator(stockDataProvider)
            aSimulator = _makeSimulator(eventTestSet, generator, tag, )
            simulators.append(aSimulator)

    # RUN SIMULATIONS
    for aSimulator in simulators:
        aSimulator.simulate()

    logger.summary()
    logger.plot()


if __name__ == '__main__':
    main()