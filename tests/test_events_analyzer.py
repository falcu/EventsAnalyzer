from unittest import TestCase
import tests.test_base as test_base
from model import providers
from model import market_model
from model import events_analyzer

class ParametricTestByCumulativeARTest( TestCase ):

    def test_cumulativeAR_fromTestData_computesCorrectValue(self):
        parametricTest = self._makeParametricTestByCumulativeAR()

        result = parametricTest.cumulativeAR()

        self.assertAlmostEqual(-0.0385857442, result, 7 )

    def test_testValue_fromTestData_computesCorrectValue(self):
        parametricTest = self._makeParametricTestByCumulativeAR()

        result = parametricTest.testValue()

        self.assertAlmostEqual(-0.19196367,result, 7 )

    def test_isSignificant_fromTestData_shouldNotBe(self):
        parametricTest = self._makeParametricTestByCumulativeAR()

        self.assertFalse( parametricTest.isSignificant() )

    def test_isSignificant_fromTestDataWithEvents_shouldBe(self):
        parametricTest = self._makeParametricTestByCumulativeAR(test_base.getTestStocksWithEventsFile())

        self.assertTrue( parametricTest.isSignificant() )

    def _makeParametricTestByCumulativeAR(self, stocksFile=''):
        stocksFile = stocksFile or test_base.getTestStocksFile()
        stocksPriceProvider = providers.ExcelDataProvider(stocksFile, 'Precios')
        marketPriceProvider = providers.ExcelDataProvider(test_base.getTestSandPFile(), 'Precios')
        stocksReturnsProvider = providers.ReturnDataProvider(stocksPriceProvider)
        marketReturnProvider = providers.ReturnDataProvider(marketPriceProvider)
        marketModel = market_model.MarketModel(stocksReturnsProvider, marketReturnProvider)
        stocksWindows = events_analyzer.StocksWindows()
        stocksWindows.addStockWindow('AAME', 0, 249, 258)
        stocksWindows.addStockWindow('AAON', 249, 499, 508)
        stocksWindows.addStockWindow('AAP', 250, 499, 508)
        abnormalReturnCalc = events_analyzer.AbnormalReturnCalculator(marketModel)
        parametricTest = events_analyzer.ParametricTestByCumulativeAR(abnormalReturnCalc)
        parametricTest.workWith(stocksWindows)

        return parametricTest