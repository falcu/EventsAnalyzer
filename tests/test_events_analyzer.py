from unittest import TestCase
import tests.test_base as test_base
from model import providers
from model import market_model
from model import events_analyzer

class ParametricTestByCumulativeARTest( TestCase ):

    def test_cumulativeAR_fromTestData_computesCorrectValue(self):
        parametricTest = self._makeParametricTestByCumulativeAR()

        result = parametricTest.cumulativeAR()

        self.assertAlmostEqual(-0.047443369, result, 7 )

    def test_testValue_fromTestData_computesCorrectValue(self):
        parametricTest = self._makeParametricTestByCumulativeAR()

        result = parametricTest.testValue()

        self.assertAlmostEqual(-0.0031613674, result, 7 )

    def _makeParametricTestByCumulativeAR(self):
        stocksPriceProvider = providers.ExcelDataProvider(test_base.getTestStocksFile(), 'Precios')
        marketPriceProvider = providers.ExcelDataProvider(test_base.getTestSandPFile(), 'Precios')
        stocksReturnsProvider = providers.ReturnDataProvider(stocksPriceProvider)
        marketReturnProvider = providers.ReturnDataProvider(marketPriceProvider)
        marketModel = market_model.MarketModel(stocksReturnsProvider, marketReturnProvider)
        stocksWindows = events_analyzer.StocksWindows()
        stocksWindows.addStockWindow('AAME', 1, 251, 261)
        stocksWindows.addStockWindow('AAON', 250, 500, 510)
        stocksWindows.addStockWindow('AAP', 500, 750, 760)
        abnormalReturnCalc = events_analyzer.AbnormalReturnCalculator(marketModel)
        parametricTest = events_analyzer.ParametricTestByCumulativeAR(abnormalReturnCalc)
        parametricTest.workWith(stocksWindows)

        return parametricTest