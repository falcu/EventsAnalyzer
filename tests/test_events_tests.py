from unittest import TestCase

import model.events_tests
import tests.test_base as test_base
from model import providers
from model import market_model
from model import events_analyzer
from abc import ABC, abstractmethod

class BaseEventTest( TestCase ):

    @abstractmethod
    def _eventTestClass(self):
        pass

    def _makeEventTest(self, stocksFile=''):
        stocksFile = stocksFile or test_base.getTestStocksFile()
        stocksPriceProvider = providers.ExcelDataProvider(stocksFile, 'Precios')
        marketPriceProvider = providers.ExcelDataProvider(test_base.getTestSandPFile(), 'Precios')
        stocksReturnsProvider = providers.ReturnDataProvider(stocksPriceProvider)
        marketReturnProvider = providers.ReturnDataProvider(marketPriceProvider)
        marketModel = market_model.MarketModel(stocksReturnsProvider, marketReturnProvider)
        stocksWindows = events_analyzer.StocksWindows()
        stocksWindows.addStockWindow('AAME', 0, 249, 258)
        stocksWindows.addStockWindow('AAON', 250, 499, 508)
        stocksWindows.addStockWindow('AAP', 250, 499, 508)
        abnormalReturnCalc = events_analyzer.AbnormalReturnCalculator(marketModel)
        parametricTest = self._eventTestClass()(abnormalReturnCalc)
        parametricTest.workWith(stocksWindows)

        return parametricTest


class ParametricTest1( BaseEventTest ):

    def _eventTestClass(self):
        return model.events_tests.ParametricTest1

    def test_testValue_fromTestDataWithNoEvents_computesCorrectValue(self):
        eventTest = self._makeEventTest()

        result = eventTest.testValue()

        self.assertAlmostEqual(-0.453,result, 3 )

    def test_isSignificant_fromTestDataWithNoEvents_shouldNotBe(self):
        eventTest = self._makeEventTest()

        self.assertFalse( eventTest.isSignificant() )

    def test_testValue_fromTestDataWithEvents_computesCorrectValue(self):
        eventTest = self._makeEventTest(test_base.getTestStocksWithEventsFile())

        result = eventTest.testValue()

        self.assertAlmostEqual(36.008,result, 3 )

    def test_isSignificant_fromTestDataWithEvents_shouldBe(self):
        eventTest = self._makeEventTest(test_base.getTestStocksWithEventsFile())

        self.assertTrue( eventTest.isSignificant() )

class ParametricTest2( BaseEventTest ):

    def _eventTestClass(self):
        return model.events_tests.ParametricTest2

    def test_testValue_fromTestDataWithNoEvents_computesCorrectValue(self):
        eventTest = self._makeEventTest()

        result = eventTest.testValue()

        self.assertAlmostEqual(-0.449 ,result, 2 )

    def test_isSignificant_fromTestDataWithNoEvents_shouldNotBe(self):
        eventTest = self._makeEventTest()

        self.assertFalse( eventTest.isSignificant() )

    def test_testValue_fromTestDataWithEvents_computesCorrectValue(self):
        eventTest = self._makeEventTest(test_base.getTestStocksWithEventsFile())

        result = eventTest.testValue()

        self.assertAlmostEqual(42.728,result, 3 )

    def test_isSignificant_fromTestDataWithEvents_shouldBe(self):
        eventTest = self._makeEventTest(test_base.getTestStocksWithEventsFile())

        self.assertTrue( eventTest.isSignificant() )

class SignTestTest( BaseEventTest ):

    def _eventTestClass(self):
        return model.events_tests.SignTest

    def test_isSignificant_fromTestData_shouldNotBe(self):
        eventTest = self._makeEventTest()

        self.assertFalse( eventTest.isSignificant() )

    def test_testValue_fromTestDataWithNoEvents_computesCorrectValue(self):
        eventTest = self._makeEventTest()

        result = eventTest.testValue()

        self.assertAlmostEqual(-0.962,result, 3 )

    def test_testValue_fromTestDataWithEvents_computesCorrectValue(self):
        eventTest = self._makeEventTest(test_base.getTestStocksWithEventsFile())

        result = eventTest.testValue()

        self.assertAlmostEqual(-2.502,result, 3 )

    def test_isSignificant_fromTestDataWithEvents_shouldBe(self):
        eventTest = self._makeEventTest(test_base.getTestStocksWithEventsFile())

        self.assertTrue( eventTest.isSignificant() )

class RankTestTest( BaseEventTest ):

    def _eventTestClass(self):
        return model.events_tests.RankTest

    def test_isSignificant_fromTestData_shouldNotBe(self):
        eventTest = self._makeEventTest()

        self.assertFalse( eventTest.isSignificant() )

    def test_testValue_fromTestDataWithNoEvents_computesCorrectValue(self):
        eventTest = self._makeEventTest()

        result = eventTest.testValue()

        self.assertAlmostEqual(-1.062,result, 3 )

    def test_isSignificant_fromTestDataWithEvents_shouldBe(self):
        eventTest = self._makeEventTest(test_base.getTestStocksWithEventsFile())

        self.assertTrue( eventTest.isSignificant() )

    def test_testValue_fromTestDataWithEvents_computesCorrectValue(self):
        eventTest = self._makeEventTest(test_base.getTestStocksWithEventsFile())

        result = eventTest.testValue()

        self.assertAlmostEqual(2.870,result, 3 )