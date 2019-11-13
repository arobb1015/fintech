from __future__ import print_function
from os.path import join, dirname, abspath
from functools import reduce
from matplotlib import rc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import time
import datetime
import random
import xlrd #Excel import module

def buildArrayFrom(inputtedExcelFile, inputtedWorksheetName, inputtedStartCol, inputtedStartRow, inputtedEndCol, inputtedEndRow):
    '''This opens the Excel workbook (assuming that it's located in the same directory as this Python file'''
    pathToExcelFile = join(dirname(dirname(abspath(__file__))), 'Workspace', str(inputtedExcelFile))
    activeWorkbook = xlrd.open_workbook(pathToExcelFile)
    # sheetNamesOfWorkbook = activeWorkbook.sheet_names() #this copies all of the sheetnames of the workbook into an array
    # print('(All Sheets):', sheetNamesOfWorkbook) #prints the sheetname of EVERY TAB in the workbook
    # print('Sheet Name:', sheetNamesOfWorkbook[0]) #prints the sheetname of ONLY THE 1st TAB in the workbook
    # activeSheet = activeWorkbook.sheet_by_name(sheetNamesOfWorkbook[0]) #gets NAME OF THE TAB based on its position
    activeSheet = activeWorkbook.sheet_by_name(str(inputtedWorksheetName))
    tableInQuestion = defineTableInQuestion(str(inputtedStartCol), str(inputtedStartRow), str(inputtedEndCol), str(inputtedEndRow), activeSheet)
    return tableInQuestion

def workWithWorksheet(inputtedExcelFile, inputtedWorksheetName):
    '''This opens the Excel workbook (assuming that it's located in the same directory as this Python file'''
    pathToExcelFile = join(dirname(dirname(abspath(__file__))), 'Workspace', str(inputtedExcelFile))
    activeWorkbook = xlrd.open_workbook(pathToExcelFile)
    activeSheet = activeWorkbook.sheet_by_name(str(inputtedWorksheetName))
    return activeSheet

def defineTableInQuestion(startCol, startRow, endCol, endRow, worksheet):
    print("START FROM COLUMN(",startCol,") IN EXCEL; START FROM ROW(",startRow,") IN EXCEL")
    print("END AT COLUMN(",endCol,") IN EXCEL; END AT ROW(",endRow,") IN EXCEL")
    ordinalStartCol = getOrdinalCoordinateForColumn(str(startCol))+1
    startRow = int(startRow)

    accountedRowShift = startRow

    ordinalEndCol = getOrdinalCoordinateForColumn(str(endCol))+1
    endRow = int(endRow)
    print("EXCEL_ROW_START(",startRow,"); EXCEL_COL_START(",ordinalStartCol,")")
    print("EXCEL_ROW_END(",endRow,"); EXCEL_COL_END(",ordinalEndCol,")")
    specifiedTable = np.empty([(endRow-startRow+1), (ordinalEndCol-ordinalStartCol+1)], dtype = object)
    #print("The dimensions of this array are as follows: (rows,cols) =>", specifiedTable.shape)

    for i in range(startRow, len(specifiedTable)+accountedRowShift):
        for j in range(ordinalStartCol, ordinalEndCol+1):
            #print(str(worksheet.cell_value(i, j)))
            #print("(i,j) => ","(",i,",",j,") stores (",worksheet.cell_value(i-1, j-1),") from the worksheet in ArrayColIndex",(j - ordinalStartCol))
            specifiedTable[(i-accountedRowShift),(j - ordinalStartCol)] = str(worksheet.cell_value(i-1, j-1))
            #print(specifiedTable[i,j])
    return specifiedTable

def getOrdinalCoordinateForColumn(x):
    return reduce(lambda s,a:s*26+ord(a)-ord('A')+1, x, 0)-1

def getAlphaNumericCoordinatesFor(rowx, colx):
    """ (5, 7) => 'H6' """
    return "%s%d" % (getAlphaNumericCoordinateForColumn(colx), rowx+1)

def getAlphaNumericCoordinateForColumn(colx):
    """Inputting index 7 yields 'H', Inputting index 27 yields 'AB'
       Note:  Within MS-Excel, the column count starts at 1 but Python starts the count at 0.
              So if you typed '=COLUMN()' in the 'BV' column while in Excel, it'd return 74,
              but to access that column's data within Python you'd actually point to index 73
    """
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if colx <= 25:
        return alphabet[colx]
    else:
        xdiv26, xmod26 = divmod(colx, 26)
        return alphabet[xdiv26 - 1] + alphabet[xmod26]

def printTableDefinedFromExcel(table):
    print("\nThe dimensions of this table are as follows: (rows,cols) =>", table.shape,"\n")
    for i in range(0, len(table)):
        for j in range(0, len(table[0,])):
            print(table[i, j], end="  ")
        print("\n")

def convertToDataFrame(arrayBuiltFromExcel, categoryInfo, headerInfo):
    columnThatContainsCategories = categoryInfo[0]
    startingRowForColumnOfCategories = categoryInfo[1][0]
    endingRowForColumnOfCategories = categoryInfo[1][1]

    listOfCategories = []
    indexForMeaningfulRows = []
    for i in range(startingRowForColumnOfCategories, endingRowForColumnOfCategories):
        category = arrayBuiltFromExcel[i, columnThatContainsCategories]
        if (category.isspace() is True or category.strip() == ''):
            continue  # Ignores the entry that only contains whitespace or is empty and skips ahead to the next entry
        else:
            listOfCategories.append(category)
            indexForMeaningfulRows.append(i)

    print(listOfCategories)

    rowThatContainsHeaders = headerInfo[0]
    startingColumnForHeaders = headerInfo[1][0]
    endingColumnForHeaders = headerInfo[1][1]
    numberOfHeaders = endingColumnForHeaders - startingColumnForHeaders

    listOfHeaders = []
    for i in range(startingColumnForHeaders, endingColumnForHeaders):
        headerTitle = arrayBuiltFromExcel[rowThatContainsHeaders, i]
        listOfHeaders.append(headerTitle)
    print(listOfHeaders)

    dataFrame = pd.DataFrame(index=listOfHeaders, columns=listOfCategories)

    headerCounter = 0
    for i in range(startingColumnForHeaders, endingColumnForHeaders):
        categoryCounter = 0
        for j in indexForMeaningfulRows:
            category = listOfCategories[categoryCounter]
            cell = arrayBuiltFromExcel[j, i]
            dataFrame.iloc[headerCounter].loc[category] = cell
            categoryCounter += 1
        headerCounter += 1
    return dataFrame

def measureSeries(series, choice):
    measurement = 0
    if(choice[0] is 'Average'):
        if(choice[1] is 'Geometrically'):
            average = math.exp(sum(map(math.log, series)))**(1/len(series))
            measurement = average
        elif(choice[1] is 'Arithmetically'):
            average = sum(series)/len(series)
            measurement = average
    elif(choice[0] is 'Median'):
        median = np.median(series)
        measurement = median
    elif(choice[0] is 'CAGR'):
        print("The",len(series),"period annual growth rate was ___")
    elif(choice[0] is 'YoY Change'):
        listOfGrowthRates = []
        listOfGrowthRates.append(0)
        for i in range(1,len(series)):
            previous = series[i-1]
            mostRecent = series[i]
            percentChange = round(100*((mostRecent - previous) / previous),3)
            listOfGrowthRates.append(percentChange)
        measurement = listOfGrowthRates
    return measurement


# arrayStructure = buildArrayFrom('SBUX.xlsx', 'Balance Sheets', 'A', '1', 'F', '38')
# balanceSheetDF = convertToDataFrame(arrayStructure, (0,[1,31]), (0,[1,6]))
#
# cash_AND_equivalents = [float(x) for x in balanceSheetDF['Cash & Cash Equivalents'].tolist()]
# shortTermInvestments = [float(x) for x in balanceSheetDF['Short-term Investments'].tolist()]
# accountsReceivable = [float(x) for x in balanceSheetDF['Accounts Receivable, Net'].tolist()]
# inventories = [float(x) for x in balanceSheetDF['Inventories'].tolist()]
# prepaidsOTHER_CA = [float(x) for x in balanceSheetDF['Prepaid Expense & Other Assets, Current'].tolist()]
# longtermInvestments = [float(x) for x in balanceSheetDF['Long-Term Investments'].tolist()]
# equityCostInvestments = [float(x) for x in balanceSheetDF['Equity & Cost Investments'].tolist()]


arrayStructure2 = buildArrayFrom('SBUX.xlsx', 'Income Statement', 'A', '3', 'F', '27')
incomeStatementDF = convertToDataFrame(arrayStructure2, (0,[1,25]), (0,[1,6]))

print(incomeStatementDF['Store Operating Expenses'])
#revenues = [float(x) for x in incomeStatementDF['Revenues'].tolist()]



#measureSeries(incomeStatementDF['Net Income'], ('Average', 'Geometrically'))

#printTableDefinedFromExcel(arrayStructure)