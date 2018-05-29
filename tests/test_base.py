_TEST_FILES_FOLDER       = r'test_files'
_TEST_SANDP_FILE_NAME    = r'test_s&p.xlsx'
_TEST_STOCKS_FILE_NAME   = r'test_stocks.xlsx'

import os
def getTestFilesPath():
    baseDir=os.path.dirname(os.path.realpath(__file__))
    return os.path.join(baseDir,_TEST_FILES_FOLDER)

def getTestSandPFile():
    return os.path.join(getTestFilesPath(), _TEST_SANDP_FILE_NAME)

def getTestStocksFile():
    return os.path.join(getTestFilesPath(), _TEST_STOCKS_FILE_NAME)