import pandas as pd

class AbnormalReturnCalculator:
    def __init__(self, marketModel):
        self.marketModel = marketModel

    def computeAR(self, estimationWindow, eventWindow):
        marketModelResult                       = self.marketModel.compute(estimationWindow)
        eventWindowReturns                      = marketModelResult.data
        eventWindowReturns                      = eventWindowReturns.loc[eventWindowReturns.index[eventWindow.toIndex()]]
        stocksEventWindowReturns                = eventWindowReturns.loc[eventWindowReturns.index,eventWindowReturns.columns[1:]]
        marketEventWindowReturns                = eventWindowReturns.loc[eventWindowReturns.index,eventWindowReturns.columns[0:1]]
        marketEventWindowReturnsMatrix          = pd.concat([marketEventWindowReturns]*stocksEventWindowReturns.shape[1], axis=1)
        marketEventWindowReturnsMatrix.columns  = stocksEventWindowReturns.columns
        betas                                   = marketModelResult.parameters[1:2]
        alphas                                  = marketModelResult.parameters[0:1]
        betaMatrix                              = pd.concat([betas]*eventWindowReturns.shape[0], axis=0).set_index(eventWindowReturns.index)
        alphaMatrix                             = pd.concat([alphas]*eventWindowReturns.shape[0], axis=0).set_index(eventWindowReturns.index)
        eventWindowMarketModelReturn            = marketEventWindowReturnsMatrix.multiply(betaMatrix).add(alphaMatrix)
        abnormalReturns                         = stocksEventWindowReturns.sub(eventWindowMarketModelReturn)

        return abnormalReturns

class Window:
    def __init__(self, stock, t1, t2, t3, windowBuilder=None):
        self.stock = stock
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.windowBuilder = windowBuilder or IntegerWindowBuilder

    def estimationWindow(self):
        return self.windowBuilder.buildEstimationWindow(self)

    def eventWindow(self):
        return self.windowBuilder.buildEventWindow(self)

class IntegerWindowBuilder:
     @classmethod
     def buildEstimationWindow(cls, window):
         return IntegerIndexWindow(window.t1, window.t2)

     @classmethod
     def buildEventWindow(cls, window):
         return IntegerIndexWindow(window.t2, window.t3)


class IntegerIndexWindow:
    def __init__(self, start, end):
        self.start = start
        self.end   = end

    def toIndex(self):
        return [i for i in range(self.start,self.end)]

