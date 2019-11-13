import pandas as pd
import numpy as np
import datetime as dt
from math import *

# Creating Pandas DataFrames from Dictionaries
def dictionary_TO_dataframe(dictionary=None, startingYear=None, endingYear=None, scale_units_by=None):
    keys = list(dictionary.keys())
    dataFrame = pd.DataFrame([dictionary[x] for x in keys], columns=list(range(startingYear, endingYear+1)), index=keys)
    return dataFrame

def dataframe_TO_dictionary(dataframe=None):
    rowLabels = list(dataframe.index)
    #print("# of Row Labels:", len(rowLabels))
    #print("Corresponding Row Index:", list(range(0, len(rowLabels))))

    dictionaryToBeExported = {}
    for currentLabel, currentCount in zip(rowLabels, list(range(0, len(rowLabels)))):
        #print("Processing {", currentLabel, "} as INDEX(", currentCount, ")")
        dictionaryToBeExported[currentLabel] = list(dataframe.loc[rowLabels[currentCount]])
    return dictionaryToBeExported

def reformatStatement(input=None):
    def analyze_LineItem_History(specificStatement=None, specificLineItem=None, startingYear=None, endingYear=None):

        bop_Values, changes, percentChanges, averages, eop_Values = [], [], [], [], []
        for year in range(startingYear, int(endingYear + 1)):
            if (year == startingYear):
                beginningPeriodValue = "Not Available"
                endingPeriodValue = round(float(specificStatement[int(year)].loc[specificLineItem]), 2)
                changeThroughoutThePeriod = "Not Available"
                percentChangeThroughoutThePeriod = "Not Available"
                averageValueOfThePeriod = "Not Available"
            else:
                beginningPeriodValue = round(float(specificStatement[int(year - 1)].loc[specificLineItem]), 2)
                endingPeriodValue = round(float(specificStatement[int(year)].loc[specificLineItem]), 2)
                changeThroughoutThePeriod = round(float(endingPeriodValue - beginningPeriodValue), 2)

                if(beginningPeriodValue == 0.00):
                    percentChangeThroughoutThePeriod = "Not Available (division by zero)"
                else:
                    percentChangeThroughoutThePeriod = round((endingPeriodValue / beginningPeriodValue - 1) * 100, 2)
                averageValueOfThePeriod = round((beginningPeriodValue + endingPeriodValue) / 2, 2)

            # print(specificLineItem, "BoP", year, ":", beginningPeriodValue, "\n", specificLineItem, "Change during", year, ":",
            #       changeThroughoutThePeriod, "\n", specificLineItem, "EoP", year, ":", endingPeriodValue, "\n")

            bop_Values.append(beginningPeriodValue)
            changes.append(changeThroughoutThePeriod)
            percentChanges.append(percentChangeThroughoutThePeriod)
            averages.append(averageValueOfThePeriod)
            eop_Values.append(endingPeriodValue)

        data = {specificLineItem + " Beginning_of_Period_(BoP)": bop_Values,
                specificLineItem + " Change_during_Period_(Delta)": changes,
                specificLineItem + " Percent_Change_during_Period": percentChanges,
                specificLineItem + " End_of_Period_(EoP)": eop_Values,
                specificLineItem + " Average_between_Points_in_Time": averages}
        lineItemHistory = dictionary_TO_dataframe(dictionary=data, startingYear=startingYear, endingYear=endingYear,
                                                  scale_units_by="N/A")
        return lineItemHistory

    statement = input
    statement_specific_dictionary = {}
    individualLineItemsWithinStatement = list(statement.index)
    for lineItem in individualLineItemsWithinStatement:
        #print("##### Formatting '", lineItem, "' from '", statementTitle, "'")
        statement_specific_dictionary[lineItem] = analyze_LineItem_History(specificStatement=statement,
                                                                           specificLineItem=str(lineItem),
                                                                           startingYear=list(statement.columns)[0],
                                                                           endingYear=list(statement.columns)[-1])
    return statement_specific_dictionary

def handleShortcuts(input=None, task=None, dictionary=None, dataframe=None, dictionaryOfDataframes=None):
    output = ""
    if (str(task).lower() == "locatemetric"):
        #print("^^^^^ Now handling the MEASURING shortcut")
        measure = input
        if (measure.lower() == "Beginning-of-Period".lower() or measure.lower() == "Beginning_of_Period".lower() or
                measure.lower() == "BeginningOfPeriod".lower() or measure.lower() == "BoP".lower()):
            measure = "bop"
        elif (measure.lower() == "End-of-Period".lower() or measure.lower() == "End_of_Period".lower() or
              measure.lower() == "EndOfPeriod".lower() or measure.lower() == "EoP".lower()):
            measure = "eop"
        elif (  measure.lower() == "Change".lower() or measure.lower() == "RawChange".lower() or
                measure.lower() == "Raw-Change".lower() or measure.lower() == "Raw_Change".lower() or
                measure.lower() == "ChangeThroughoutPeriod".lower() or measure.lower() == "Change-Throughout-Period".lower() or
                measure.lower() == "Change_Throughout_Period".lower() or measure.lower() == "RawChangeThroughoutPeriod".lower() or
                measure.lower() == "Raw-Change-Throughout-Period".lower() or
                measure.lower() == "Raw_Change_Throughout_Period".lower() or measure.lower() == "ChangeDuringPeriod".lower() or
                measure.lower() == "Change-During-Period".lower() or measure.lower() == "Change_During_Period".lower() or
                measure.lower() == "RawChangeDuringPeriod".lower() or measure.lower() == "Raw-Change-During-Period".lower() or
                measure.lower() == "Raw_Change_During_Period".lower() or measure.lower() == "ChangeDuringYear".lower() or
                measure.lower() == "Change-During-Year".lower() or measure.lower() == "Change_During_Year".lower() or
                measure.lower() == "RawChangeDuringYear".lower() or measure.lower() == "Raw-Change-During-Year".lower() or
                measure.lower() == "Raw_Change_During_Year".lower()):
            measure = "delta"
        elif (measure.lower() == "PercentChange".lower() or measure.lower() == "Percent-Change".lower() or
              measure.lower() == "Percent_Change".lower() or measure.lower() == "%Change".lower() or
              measure.lower() == "%-Change".lower() or measure.lower() == "%_Change".lower()):
            measure = "percent"
        elif (measure.lower() == "AverageValueBetweenPointsInTime".lower() or
              measure.lower() == "Average-Value-Between-Points-In-Time".lower() or
              measure.lower() == "Average_Value_Between_Points_In_Time".lower() or
              measure.lower() == "AverageValue".lower() or measure.lower() == "Average-Value".lower() or
              measure.lower() == "Average_Value".lower() or measure.lower() == "AvgVal".lower() or
              measure.lower() == "Avg-Val".lower() or measure.lower() == "Avg_Val".lower() or
              measure.lower() == "AvgValue".lower() or measure.lower() == "Avg-Value".lower() or
              measure.lower() == "Avg_Value".lower() or measure.lower() == "AverageVal".lower() or
              measure.lower() == "Average-Val".lower() or measure.lower() == "Average_Val".lower()):
            measure = "average"

        narrowedResults = dictionaryOfDataframes
        inputFor_dot_loc = ""

        if (dictionary is None and dataframe is None):
            for x in list(narrowedResults.index):
                if (measure.lower() in str(x).lower()):
                    inputFor_dot_loc = x
            output = inputFor_dot_loc
        elif (dictionary is not None):
            for x in list(dictionary.keys()):
                if (measure.lower() in str(x).lower()):
                    inputFor_dot_loc = x
            output = inputFor_dot_loc
        elif (dataframe is not None and dictionary is None):
            for x in list(dataframe.index):
                if (measure.lower() in str(x).lower()):
                    inputFor_dot_loc = x
            output = inputFor_dot_loc


        #print("^^^^^ Reference '", output, "' was found for '", measure, "' query")

    elif (str(task).lower() == "locatelineitem"):
        #print("^^^^^ Now handling the LINEITEM shortcut")
        lineItem = input
        if (lineItem.lower() is "Cash".lower() or lineItem.lower() is "Cash_&_Equivalents".lower() or
                lineItem.lower() is "Cash-&-Equivalents".lower()):
            lineItem = "(Cash)"
        elif (lineItem.lower() is "AR".lower() or lineItem.lower() is "AcctRec".lower() or lineItem.lower() is "AcctsRec".lower() or
                lineItem.lower() is "AccountsRec".lower() or lineItem.lower() is "AccountsRec.".lower()):
            lineItem = "(AR)"
        elif (lineItem.lower() is "Property,Plant,Equipment".lower() or lineItem.lower() is "Property,Plant&Equipment".lower() or
                lineItem.lower() is "PPE".lower() or lineItem.lower() is "PP_&_E".lower()):
            lineItem = "(PP_&_E)"
        elif (lineItem.lower() is "Goodwill".lower()):
            lineItem = "(Goodwill)"
        elif (lineItem.lower() is "OtherCurrentAssets".lower()):
            lineItem = "(OCA)"
        elif (lineItem.lower() is "OtherNonCurrentAssets".lower() or lineItem.lower() is "Other_Non_Current_Assets".lower()):
            lineItem = "(ONCA)"
        elif (lineItem.lower() is "AccountsPayable".lower() or lineItem.lower() is "Accounts-Payable".lower() or
              lineItem.lower() is "Accounts_Payable".lower() or lineItem.lower() is "AccountsPbl".lower()):
            lineItem = "(AP)"
        elif (lineItem.lower() is "OtherCurrentLiabilities".lower()):
            lineItem = "(OCL)"
        elif (lineItem.lower() is "AccruedExpenses".lower() or lineItem.lower() is "Accrued-Expenses".lower() or
              lineItem.lower() is "Accrued_Expenses".lower() or lineItem.lower() is "DeferredRevenues".lower() or
              lineItem.lower() is "Deferred-Revenues".lower() or lineItem.lower() is "Deferred_Revenues".lower()):
            lineItem = "(AccrdExp)"
        elif (lineItem.lower() is "OtherNonCurrentLiabilities".lower()):
            lineItem = "(ONCL)"
        elif (lineItem.lower() is "CommonStock".lower() or lineItem.lower() is "Common-Stock".lower() or
              lineItem.lower() is "Common_Stock".lower() or lineItem.lower() is "CommonEquity".lower() or
              lineItem.lower() is "Common-Equity".lower() or lineItem.lower() is "Common_Equity".lower()):
            lineItem = "(CommonEquity)"
        elif (lineItem.lower() is "TreasuryStock".lower() or lineItem.lower() is "Treasury-Stock".lower() or
              lineItem.lower() is "Treasury_Stock".lower()):
            lineItem = "(TS)"
        elif (lineItem.lower() is "RE".lower() or lineItem.lower() is "RetainedEarnings".lower() or
              lineItem.lower() is "Retained_Earnings".lower() or lineItem.lower() is "Retained-Earnings".lower()):
            lineItem = "(RE)"
        elif (lineItem.lower() is "Revenue".lower() or lineItem.lower() is "Revenues".lower() or
              lineItem.lower() is "Sales".lower()):
            lineItem = "(Sales)"
        elif (lineItem.lower() is "COGS".lower() or lineItem.lower() is "CostOfGoodsSold".lower() or
              lineItem.lower() is "Cost-Of-Goods-Sold".lower() or lineItem.lower() is "Cost_Of_Goods_Sold".lower()):
            lineItem = "(COGS)"
        elif (lineItem.lower() is "R_&_D".lower() or lineItem.lower() is "R-&-D".lower() or lineItem.lower() is "R&D".lower() or
                lineItem.lower() is "Research&Development".lower() or lineItem.lower() is "Research_&_Development".lower()):
            lineItem = "(R_&_D)"
        elif (lineItem.lower() is "SGA".lower() or lineItem.lower() is "SG_&_A".lower() or
              lineItem.lower() is "SG-&-A".lower()):
            lineItem = "(SG_&_A)"
        elif (lineItem.lower() is "GrossProfit".lower() or lineItem.lower() is "Gross-Profit".lower() or
              lineItem.lower() is "Gross_Profit".lower() or lineItem.lower() is "GP".lower()):
            lineItem = "(GP)"
        elif (lineItem.lower() is "OperatingProfit".lower() or lineItem.lower() is "Operating-Profit".lower() or
              lineItem.lower() is "Operating_Profit".lower() or lineItem.lower() is "EBIT".lower()):
            lineItem = "(EBIT)"
        elif (lineItem.lower() is "InterestExpense".lower() or lineItem.lower() is "Interest-Expense".lower() or
              lineItem.lower() is "Interest_Expense".lower() or lineItem.lower() is "IE".lower()):
            lineItem = "(IE)"
        elif (lineItem.lower() is "PreTaxProfit".lower() or lineItem.lower() is "Pre-Tax-Profit".lower() or
              lineItem.lower() is "Pre_Tax_Profit".lower() or lineItem.lower() is "EBT".lower() or
              lineItem.lower() is "EarningsBeforeTaxes".lower() or lineItem.lower() is "Earnings-Before-Taxes".lower()):
            lineItem = "(EBT)"
        elif (lineItem.lower() is "NetIncome".lower() or lineItem.lower() is "Net-Income".lower() or
              lineItem.lower() is "NetEarnings".lower() or lineItem.lower() is "Net-Earnings".lower() or
              lineItem.lower() is "Net_Earnings".lower()):
            lineItem = "Net_Income"


        financialStatement = dictionaryOfDataframes
        identificationLabelForLineItemSoughtByAnalyst = ""
        for x in list(financialStatement.keys()):
            if (lineItem.lower() in str(x).lower() or lineItem.lower() == str(x).lower()):
                identificationLabelForLineItemSoughtByAnalyst = x
        output = identificationLabelForLineItemSoughtByAnalyst
        #print("^^^^^ Reference '", output, "' was found for '", lineItem, "' query")

    return output

def pullData(source=None, itemOfInterest=None, metric=None, specificYear=None, timeRange=None):
    #print("***** Processing analyst's query for '", itemOfInterest, "'")

    identificationLabel = handleShortcuts(task="LocateLineItem", input=itemOfInterest, dictionaryOfDataframes=source)

    narrowedResults = source[str(identificationLabel)]
    measure = handleShortcuts(task="LocateMetric", input=metric, dictionaryOfDataframes=narrowedResults)

    specificMetricSoughtByAnalyst = ""
    for x in list(narrowedResults.index):
        if(measure.lower() in str(x).lower()):
            specificMetricSoughtByAnalyst = x

    if(specificYear is None and timeRange is not None):
        requestedInformation = narrowedResults.loc[specificMetricSoughtByAnalyst]

    elif(specificYear is not None and timeRange is None):
        requestedInformation = narrowedResults.at[specificMetricSoughtByAnalyst, specificYear]

    return requestedInformation

def doVectorMath(listOfLists, operation="ADDITION"):

    initialList = [float(x) for x in listOfLists[0]]
    resultOfCalculation = np.array(initialList)
    #print("FirstList:",resultOfCalculation)
    for x in range(1, len(listOfLists)):
        currentList = [float(x) for x in listOfLists[x]]
        #print("SubsequentList:", currentList)
        if(operation is "ADDITION"):
            resultOfCalculation += np.array(currentList)
        elif (operation is "SUBTRACTION"):
            resultOfCalculation -= np.array(currentList)
        elif (operation is "DIVISION"):
            resultOfCalculation /= np.array(currentList)
        elif (operation is "MULTIPLICATION"):
            resultOfCalculation *= np.array(currentList)

    resultingList = resultOfCalculation.tolist()
    return resultingList

def analyzeWorkingCapital(source=None):

    incomeStatement = source["IncomeStatement"]
    balanceSheet = source["BalanceSheet"]
    timeRange = (list(balanceSheet["Revolver"].columns)[0], list(balanceSheet["Revolver"].columns)[-1])
    earliest, mostRecent = timeRange[0],  timeRange[1]

    #Total Debt (aka Gross Debt)
    totalDebt = doVectorMath([list(pullData(source=balanceSheet, itemOfInterest="Revolver",
                                            metric="eop", timeRange=(earliest, mostRecent))),
                              list(pullData(source=balanceSheet, itemOfInterest="(LTD)",
                                            metric="eop", timeRange=(earliest, mostRecent),))], operation="ADDITION")

    netDebt = doVectorMath([totalDebt, list(pullData(source=balanceSheet, itemOfInterest="Cash",
                                                     metric="eop", timeRange=(earliest, mostRecent)))], operation="SUBTRACTION")
    #print("[NetDebt] =", netDebt)

    netIncome = list(pullData(source=incomeStatement, itemOfInterest="Net_Income", metric="eop", timeRange=(earliest, mostRecent)))

    returnOnAssets = doVectorMath([netIncome, list(total_assets.sum())], operation="DIVISION")
    #print("[ROA] =", returnOnAssets)

    returnOnBookEquity = doVectorMath([netIncome, list(total_equity.sum())], operation="DIVISION")
    #print("[ROE (Book Value of Equity)] =", returnOnBookEquity)


    accountsReceivable = list(pullData(source=balanceSheet, itemOfInterest="(AR)",
                                       metric="eop", timeRange=(earliest, mostRecent)))
    revenue = list(pullData(source=incomeStatement, itemOfInterest="Revenue",
                            metric="eop", timeRange=(earliest, mostRecent)))
    accountsReceivables_TO_Sales = doVectorMath([accountsReceivable, revenue], operation="DIVISION")
    #print("[Accounts Receivables as % of Sales] =", np.round(np.dot(100, accountsReceivables_TO_Sales),decimals=2), "%")
    days_sales_outstanding = np.round(np.dot(365, accountsReceivables_TO_Sales), decimals=2).tolist()
    #print("[AR/Sales * 365] = [DSO] =", days_sales_outstanding, "days")


    cogs = np.abs(list(pullData(source=incomeStatement, itemOfInterest="(COGS)",
                                metric="eop", timeRange=(earliest, mostRecent))))
    inventory = list(pullData(source=balanceSheet, itemOfInterest="Inventory",
                              metric="eop", timeRange=(earliest, mostRecent)))
    inventoryTurnover = doVectorMath([cogs, inventory], operation="DIVISION")
    #print("[Inventory Turnover] =", inventoryTurnover)
    inventory_TO_COGS = doVectorMath([inventory, cogs], operation="DIVISION")
    #print("[Inventory as % of COGS] =", np.round(inventory_TO_COGS, decimals=2), "%")
    days_inventory_held = np.round(np.dot(365, inventory_TO_COGS), decimals=2).tolist()
    #print("[Inventory/COGS * 365] = [DIH] =", days_inventory_held, "days")


    accountsPayable = list(pullData(source=balanceSheet, itemOfInterest="(AP)",
                                    metric="eop", timeRange=(earliest, mostRecent)))
    accountsPayable_TO_COGS = doVectorMath([accountsPayable, cogs], operation="DIVISION")
    #print("[Accounts Payable as % of COGS] =", np.dot(100, accountsPayable_TO_COGS), "%")
    days_payable_outstanding = np.round(np.dot(365, accountsPayable_TO_COGS), decimals=2).tolist()
    #print("[AP/COGS * 365] = [DPO] =", days_payable_outstanding, "days")


    accruedExpenses_and_DeferredRevenues = list(pullData(source=balanceSheet, itemOfInterest="(AccrdExp)",
                                                         metric="eop", timeRange=(earliest, mostRecent)))
    accruedExpenses_TO_Sales = doVectorMath([accruedExpenses_and_DeferredRevenues, revenue], operation="DIVISION")
    #print("[Accrued Expenses as % of Revenue] =", np.round(np.dot(100, accruedExpenses_TO_Sales), decimals=2), "%")

    cashConversionCycle = doVectorMath([doVectorMath([days_inventory_held, days_sales_outstanding], operation="ADDITION"),
                                        days_payable_outstanding],                                  operation="SUBTRACTION")

    return reformatStatement(input=dictionary_TO_dataframe(dictionary={"AR_as_%_of_Sales": accountsReceivables_TO_Sales,
                                                                       "(DSO)": days_sales_outstanding,
                                                                       "InventoryTurnover": inventoryTurnover,
                                                                       "Inventory_as_%_of_COGS": inventory_TO_COGS,
                                                                       "(DIH)": days_inventory_held,
                                                                       "AP_as_%_of_COGS": accountsPayable_TO_COGS,
                                                                       "(DPO)": days_payable_outstanding,
                                                                       "AccrdExp_as_%_of_Sales": accruedExpenses_TO_Sales,
                                                                       "Length_of_Cash_Conversion_Cycle": cashConversionCycle},
                                                           startingYear=earliest,
                                                           endingYear=mostRecent))

def verifyBalance(dictionaryForDataframe=None, year=None):
    assets = [lineItem for lineItem in dictionaryForDataframe["Assets"].keys()]
    liabilities = [lineItem for lineItem in dictionaryForDataframe["Liabilities"].keys()]
    equity = [lineItem for lineItem in dictionaryForDataframe["Equity"].keys()]
    balance_for_ASSETS, balance_for_LIABILITIES, balance_for_EQUITY = 0, 0, 0
    for lineItem in assets:
        value = pullData(source=dictionaryForDataframe["Assets"], itemOfInterest=lineItem,
                         metric="EoP", specificYear=year)
        balance_for_ASSETS += float(value)
    for lineItem in liabilities:
        value = pullData(source=dictionaryForDataframe["Liabilities"], itemOfInterest=lineItem,
                         metric="EoP", specificYear=year)
        balance_for_LIABILITIES += float(value)
    for lineItem in equity:
        value = pullData(source=dictionaryForDataframe["Equity"], itemOfInterest=lineItem,
                         metric="EoP", specificYear=year)
        balance_for_EQUITY += float(value)
    balance_for_ASSETS = round(balance_for_ASSETS, 2)
    balance_for_LIABILITIES = round(balance_for_LIABILITIES, 2)
    balance_for_EQUITY = round(balance_for_EQUITY, 2)
    check = round((balance_for_ASSETS - (balance_for_LIABILITIES + balance_for_EQUITY)), 3)
    print(year, "BalanceCheck: [ (A =", balance_for_ASSETS, ") ] - [ (L =", balance_for_LIABILITIES, ") +",
          "(E =", balance_for_EQUITY, ") ] =", check)
    return check

def forecast(mostRecentEoP_Data=None, proportionAnchor=None, explicitGrowthRate=None, rule=None):

    futureBoP_Data = mostRecentEoP_Data["Figure"]
    forecastedValue = 0

    if(proportionAnchor is not None and explicitGrowthRate is None and rule is None):

        forecastedValue = round((proportionAnchor["Figure"] * proportionAnchor["Fraction"]), 2)
        print("Forecasting", mostRecentEoP_Data["Label"], "as", round(proportionAnchor["Fraction"]*100, 3), "% of",
              proportionAnchor["Reference"], ": (", proportionAnchor["Figure"], "*",
              round(proportionAnchor["Fraction"] * 100, 3), "% ) =", forecastedValue)

    elif(explicitGrowthRate is not None and proportionAnchor is None and rule is None):

        forecastedValue = round((mostRecentEoP_Data["Figure"] * (1 + explicitGrowthRate/100)), 2)
        print("Forecasting", explicitGrowthRate, "% growth for", mostRecentEoP_Data["Label"],
              ": [", mostRecentEoP_Data["Figure"], "* (1 +", round(explicitGrowthRate/100, 2), ") ] =", forecastedValue)

    elif(rule is not None and proportionAnchor is None and explicitGrowthRate is None):
        if(rule == "HOLD CONSTANT"):
            forecastedValue = round(mostRecentEoP_Data["Figure"] * (1), 2) # This holds the value constant
            print("Forecasting 0.00% growth for", mostRecentEoP_Data["Label"],"(holding value constant)")
        elif(rule[0] == "ADD_QUANTITY"):
            forecastedValue = round((mostRecentEoP_Data["Figure"] + rule[1]), 2)
        elif (rule[0] == "SUBTRACT_QUANTITY"):
            forecastedValue = round((mostRecentEoP_Data["Figure"] - rule[1]), 2)
        elif (rule[0] == "MULTIPLY_BY_QUANTITY"):
            forecastedValue = round((mostRecentEoP_Data["Figure"] * rule[1]), 2)
        elif (rule[0] == "DIVIDE_BY_QUANTITY"):
            forecastedValue = round((mostRecentEoP_Data["Figure"] / rule[1]), 2)

    futureEoP_Data = forecastedValue
    delta = (futureEoP_Data - futureBoP_Data)
    if(futureBoP_Data == 0.00):
        percentChangeThroughoutThePeriod = "Not Applicable (division by zero)"
    else:
        percentChangeThroughoutThePeriod = round((futureEoP_Data / futureBoP_Data - 1) * 100, 2)

    results = {"Future_BoP": futureBoP_Data, "Change": delta, "PercentChange": percentChangeThroughoutThePeriod,
               "Future_EoP": futureEoP_Data}
    return results

def forecastIncomeStatement(historicalSources=None, projectedSources=None, timeRange=None, stage=None):

    historicalIncomeStatements = historicalSources["IncomeStatement"]
    historicalBalanceSheets = historicalSources["BalanceSheet"]
    historicalCashflowStatements = historicalSources["CashflowStatement"]

    proj = None

    projectedIncomeStatement = {}

    if (stage == "1"):
        theOrderLineItemsAreToBeForecasted = ["Revenue_(Sales)", "Gross_Profit_(GP)", "Research_&_Development_(R_&_D)",
                                              "Selling,_General,_&_Administrative_(SG_&_A)", "Operating_Profit_(EBIT)",
                                              "Interest_INCOME", "Interest_EXPENSE_(IE)", "Other_Expense",
                                              "Pre-Tax_Profit_(EBT)",  "Taxes",  "Net_Income"]
    elif (stage == "2"):
        projectedIncomeStatements = projectedSources["IncomeStatement"]

        '''This loop force-updates the (IS) projections before the MODIFIED 'Net Income' is calculated'''
        for lineItem in list(projectedIncomeStatements.keys()):
            lineItemDataframe = projectedIncomeStatements[lineItem]
            lineItemDetails = dataframe_TO_dictionary(dataframe=lineItemDataframe)
            key = handleShortcuts(task="LocateMetric", input="EoP", dictionary=lineItemDetails)
            end_of_period_projections = lineItemDetails[key]
            # print("RETRIEVING STAGE( 1 )", lineItem, "EoP Projections:", end_of_period_projections)
            projectedIncomeStatement[lineItem] = end_of_period_projections

        projectedBalanceSheets = projectedSources["BalanceSheet"]
        projectedCashflowStatements = projectedSources["CashflowStatement"]

        theOrderLineItemsAreToBeForecasted = ["Interest_INCOME", "Interest_EXPENSE_(IE)", "Other_Expense",
                                              "Pre-Tax_Profit_(EBT)",  "Taxes",  "Net_Income"]

    print("\n")
    print("***** STAGE(", stage, ") INCOME STATEMENT FORECAST *****")
    for operation in theOrderLineItemsAreToBeForecasted:
        if (operation == "Revenue_(Sales)"):
            mostRecentlyReportedRevenue = pullData(source=historicalIncomeStatements, itemOfInterest="(Sales)",
                                                   specificYear=(timeRange[0] - 1), metric="EoP")
            revenueProjections = []
            for currentYear in range(timeRange[0], timeRange[1] + 1):
                results = forecast(mostRecentEoP_Data={"Label": "Revenue", "Figure": mostRecentlyReportedRevenue},
                                   explicitGrowthRate=5.0)
                revenueProjections.append(results["Future_EoP"])
                mostRecentlyReportedRevenue = results["Future_EoP"]
            projectedIncomeStatement[operation] = revenueProjections
            print("\n")
        elif (operation == "Gross_Profit_(GP)"):
            grossProfitProjections = []
            mostRecentlyReportedGrossProfit = pullData(source=historicalIncomeStatements, itemOfInterest="(GP)",
                                                       specificYear=(timeRange[0] - 1), metric="EoP")
            for currentYear in range(timeRange[0], timeRange[1] + 1):
                index = (currentYear - timeRange[0])
                results = forecast(
                    mostRecentEoP_Data={"Label": "Gross Profit", "Figure": mostRecentlyReportedGrossProfit},
                    proportionAnchor={"Reference": "Revenues", "Figure": revenueProjections[index],
                                      "Fraction": 0.374})
                grossProfitProjections.append(results["Future_EoP"])
                mostRecentlyReportedGrossProfit = results["Future_EoP"]
            cogsProjections = list(doVectorMath([revenueProjections, grossProfitProjections], operation="SUBTRACTION"))
            cogsProjections = list(np.dot(-1, cogsProjections))
            projectedIncomeStatement["Cost_of_Sales_(COGS)"] = cogsProjections
            projectedIncomeStatement[operation] = grossProfitProjections
            print("\n")
        elif (operation == "Research_&_Development_(R_&_D)"):
            research_and_devProjections = []
            mostRecentlyReported_R_and_D = pullData(source=historicalIncomeStatements, itemOfInterest="(R_&_D)",
                                                    specificYear=(timeRange[0] - 1), metric="EoP")
            for currentYear in range(timeRange[0], timeRange[1] + 1):
                index = (currentYear - timeRange[0])
                results = forecast(mostRecentEoP_Data={"Label": "R_&_D", "Figure": mostRecentlyReported_R_and_D},
                                   proportionAnchor={"Reference": "Revenues", "Figure": revenueProjections[index],
                                                     "Fraction": 0.031})
                research_and_devProjections.append(results["Future_EoP"])
                mostRecentlyReported_R_and_D = results["Future_EoP"]
            research_and_devProjections = list(np.dot(-1, research_and_devProjections))
            projectedIncomeStatement[operation] = research_and_devProjections
            print("\n")
        elif (operation == "Selling,_General,_&_Administrative_(SG_&_A)"):
            sgaProjections = []
            mostRecentlyReported_SGA = pullData(source=historicalIncomeStatements, itemOfInterest="(SG_&_A)",
                                                specificYear=(timeRange[0] - 1), metric="EoP")
            for currentYear in range(timeRange[0], timeRange[1] + 1):
                index = (currentYear - timeRange[0])
                results = forecast(mostRecentEoP_Data={"Label": "SG_&_A", "Figure": mostRecentlyReported_SGA},
                                   proportionAnchor={"Reference": "Revenues", "Figure": revenueProjections[index],
                                                     "Fraction": 0.068})
                sgaProjections.append(results["Future_EoP"])
                mostRecentlyReported_SGA = results["Future_EoP"]
            sgaProjections = list(np.dot(-1, sgaProjections))
            projectedIncomeStatement[operation] = sgaProjections
            print("\n")
        elif (operation == "Operating_Profit_(EBIT)"):
            ebitProjections = list(doVectorMath([projectedIncomeStatement["Gross_Profit_(GP)"],
                                                 projectedIncomeStatement["Research_&_Development_(R_&_D)"],
                                                 projectedIncomeStatement["Selling,_General,_&_Administrative_(SG_&_A)"]],
                                                operation="ADDITION"))
            ebitProjections = [round(eachYearsFigure, 2) for eachYearsFigure in ebitProjections]
            print("EBIT Projections:", ebitProjections)
            projectedIncomeStatement[operation] = ebitProjections
        elif (operation == "Interest_INCOME"):
            if (stage == "1"):
                interestIncomeProjections = [float(0.00) for currentYear in range(timeRange[0], timeRange[1] + 1)]
            elif (stage == "2"):
                interestIncomeProjections = []
                for currentYear in range(timeRange[0], timeRange[1] + 1):
                    currentYear_InterestIncomeFromCash = pullData(source=projectedBalanceSheets["SupplementalData"],
                                                                  itemOfInterest="InterestIncomeFromCashHoldings",
                                                                  metric="EoP", specificYear=currentYear)
                    interestIncomeProjections.append(currentYear_InterestIncomeFromCash)
                print("Operating Profit (EBIT) Projections:", projectedIncomeStatement["Operating_Profit_(EBIT)"])
            print("Interest Income Projections:", interestIncomeProjections)
            projectedIncomeStatement[operation] = interestIncomeProjections
        elif (operation == "Interest_EXPENSE_(IE)"):
            if (stage == "1"):
                ie_Projections = [float(0.00) for currentYear in range(timeRange[0], timeRange[1] + 1)]
            elif (stage == "2"):
                ie_Projections = []
                for currentYear in range(timeRange[0], timeRange[1] + 1):
                    ltd_IE = pullData(source=projectedBalanceSheets["SupplementalData"], itemOfInterest="InterestExpenseForLTD",
                                      metric="EoP", specificYear=currentYear)
                    revolver_IE = pullData(source=projectedBalanceSheets["SupplementalData"], itemOfInterest="InterestExpenseForRevolver",
                                           metric="EoP", specificYear=currentYear)
                    currentYear_Total_IE = (ltd_IE + revolver_IE)
                    ie_Projections.append(currentYear_Total_IE)

            print("Interest Expense Projections:", ie_Projections)
            projectedIncomeStatement[operation] = ie_Projections
        elif (operation == "Other_Expense"):
            otherExpensesProjections = []
            mostRecentlyReported_OtherExpense = pullData(source=historicalIncomeStatements, itemOfInterest="Other_Expense",
                                                         metric="EoP", specificYear=(timeRange[0] - 1))
            for currentYear in range(timeRange[0], timeRange[1] + 1):
                otherExpenseForecastResults = forecast(mostRecentEoP_Data={"Label": "Other Expenses",
                                                                           "Figure": mostRecentlyReported_OtherExpense},
                                                       rule="HOLD CONSTANT")
                otherExpensesProjections.append(otherExpenseForecastResults["Future_EoP"])
                mostRecentlyReported_OtherExpense = otherExpenseForecastResults["Future_EoP"]
            #otherExpensesProjections = list(np.dot(-1, otherExpensesProjections))
            print("Other Expenses Projections:", otherExpensesProjections)
            projectedIncomeStatement[operation] = otherExpensesProjections
        elif (operation == "Pre-Tax_Profit_(EBT)"):
            pretaxProfit = list(doVectorMath([projectedIncomeStatement["Operating_Profit_(EBIT)"],
                                              projectedIncomeStatement["Interest_INCOME"],
                                              projectedIncomeStatement["Interest_EXPENSE_(IE)"],
                                              projectedIncomeStatement["Other_Expense"]],
                                             operation="ADDITION"))
            print("EBT (Pre-Tax Profit) Projections:", pretaxProfit)
            projectedIncomeStatement[operation] = pretaxProfit
        elif (operation == "Taxes"):
            taxes = list(np.round(np.dot(-0.27, projectedIncomeStatement["Pre-Tax_Profit_(EBT)"]), decimals=2))
            print("Tax Projections:", taxes)
            projectedIncomeStatement[operation] = taxes
        elif (operation == "Net_Income"):
            netIncome = list(np.round(doVectorMath([projectedIncomeStatement["Pre-Tax_Profit_(EBT)"],
                                                    projectedIncomeStatement["Taxes"]],
                                                   operation="ADDITION"), decimals=2))
            if (stage == "1"):
                print("Net Income (BEFORE CASH FORECAST):", netIncome)
            elif (stage == "2"):
                print("Net Income (**AFTER** CASH FORECAST):", netIncome)
            projectedIncomeStatement[operation] = netIncome

    proj = reformatStatement(input=dictionary_TO_dataframe(dictionary=projectedIncomeStatement,
                                                           startingYear=timeRange[0],
                                                           endingYear=timeRange[1]))
    if (stage == "2"):
        projectedSources["IncomeStatement"] = proj

    return proj

def forecastBalanceSheet(historicalSources=None, projectedSources=None, timeRange=None, stage=None, operationsSequence=None):

    historicalIncomeStatements = historicalSources["IncomeStatement"]
    historicalBalanceSheets = historicalSources["BalanceSheet"]
    historicalCashflowStatements = historicalSources["CashflowStatement"]
    historical_NWC = analyzeWorkingCapital(source=historicalSources)

    projectedIncomeStatements = projectedSources["IncomeStatement"]

    proj = None

    assets, liabilities, equity, supportingItems = {}, {}, {}, {}

    if(stage == "1"):
        theOrderLineItemsAreToBeForecasted = ["(AR)", "(Invnt)", "(OCA)", "(Intan)", "(DTA)", "(ONCA)", "(PPE)", "(AP)",
                                              "(AccrdExp)", "(LTD)", "(ONCL)", "(CapStock)", "(TS)", "(RE)", "(OCI)"]

        assets["Cash_&_Equivalents_(including_ST_&_LT_Securities)_(Cash)"] = [0.00 for year in range(timeRange[0], (timeRange[1] + 1))]
        supportingItems["InterestIncomeFromCashHoldings"] = [0.00 for year in range(timeRange[0], (timeRange[1] + 1))]
        liabilities["Revolver"] = [0.00 for year in range(timeRange[0], (timeRange[1] + 1))]
        supportingItems["delta_Revolver"] = [0.00 for year in range(timeRange[0], (timeRange[1] + 1))]
        supportingItems["InterestExpenseForRevolver"] = [0.00 for year in range(timeRange[0], (timeRange[1] + 1))]
    elif(stage == "2"):
        projectedBalanceSheets = projectedSources["BalanceSheet"]
        projectedCashflowStatements = projectedSources["CashflowStatement"]

        '''This nested loop force-updates the (BS) projections before 'Cash' & 'Revolver' are recursively found'''

        for section in ["Assets", "Liabilities", "Equity", "SupplementalData"]:
            for lineItem in list(projectedBalanceSheets[section].keys()):
                lineItemDataframe = projectedBalanceSheets[section][lineItem]
                lineItemDetails = dataframe_TO_dictionary(dataframe=lineItemDataframe)
                key = handleShortcuts(task="LocateMetric", input="EoP", dictionary=lineItemDetails)
                end_of_period_projections = lineItemDetails[key]
                #print(lineItem, "EoP Projections:", end_of_period_projections)
                if(section == "Assets"):
                    assets[lineItem] = end_of_period_projections
                elif(section == "Liabilities"):
                    liabilities[lineItem] = end_of_period_projections
                elif (section == "Equity"):
                    equity[lineItem] = end_of_period_projections
                elif (section == "SupplementalData"):
                    supportingItems[lineItem] = end_of_period_projections

        theOrderLineItemsAreToBeForecasted = operationsSequence

    print("\n")
    print("***** STAGE(", stage, ") BALANCE SHEET FORECAST *****")
    for operation in theOrderLineItemsAreToBeForecasted:
        if (operation == "(AR)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ACCOUNTS RECEIVABLES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            accountsReceivablesProjections_BoP, accountsReceivablesProjections_EoP, delta_AR = [], [], []
            mostRecentlyReported_AR_Balance = pullData(source=historicalBalanceSheets, itemOfInterest="(AR)",
                                                       metric="EoP", specificYear=(timeRange[0] - 1))

            margin = pullData(source=historical_NWC, itemOfInterest="AR_as_%_of_Sales",
                              metric="Average", specificYear=timeRange[0]-1)
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                revenue = pullData(source=projectedIncomeStatements, itemOfInterest="(Sales)",
                                   specificYear=currentYear,
                                   metric="EoP")
                results = forecast(mostRecentEoP_Data={"Label": "(AR)", "Figure": mostRecentlyReported_AR_Balance},
                                   proportionAnchor={"Reference": "Revenues", "Figure": revenue,
                                                     "Fraction": margin})
                mostRecentlyReported_AR_Balance = results["Future_EoP"]
                priorPeriod_AR_Balance = results["Future_BoP"]
                delta_AR.append(results["Change"])
                accountsReceivablesProjections_BoP.append(priorPeriod_AR_Balance)
                accountsReceivablesProjections_EoP.append(mostRecentlyReported_AR_Balance)
            delta_AR = [round(eachYearsFigure, 2) for eachYearsFigure in delta_AR]
            print("ACCOUNT RECEIVABLES BALANCE (BoP) PROJECTIONS =", accountsReceivablesProjections_BoP)
            print("ACCOUNT RECEIVABLES CHANGE PROJECTIONS        =", delta_AR)
            print("ACCOUNT RECEIVABLES BALANCE (EoP) PROJECTIONS =", accountsReceivablesProjections_EoP)
            assets["Accounts_Receivable_(AR)"] = accountsReceivablesProjections_EoP

        elif (operation == "(Invnt)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ INVENTORY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            inventoryProjections_BoP, inventoryProjections_EoP, delta_Inventory = [], [], []
            mostRecentlyReported_Inventory_Balance = pullData(source=historicalBalanceSheets, itemOfInterest="Inventory",
                                                      metric="EoP", specificYear=(timeRange[0] - 1), )
            margin = abs(pullData(source=historical_NWC, itemOfInterest="Inventory_as_%_of_COGS",
                                  metric="Avg", specificYear=timeRange[0]-1))

            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                cogs = abs(pullData(source=projectedIncomeStatements, itemOfInterest="(COGS)",
                                    metric="EoP", specificYear=currentYear))
                results = forecast(mostRecentEoP_Data={"Label": "Inventory", "Figure": mostRecentlyReported_Inventory_Balance},
                                   proportionAnchor={"Reference": "COGS", "Figure": cogs, "Fraction": margin})
                priorPeriodsReported_Inventory_Balance = results["Future_BoP"]
                changesDuringPeriod_Inventory_Balance = results["Change"]
                mostRecentlyReported_Inventory_Balance = results["Future_EoP"]
                inventoryProjections_BoP.append(priorPeriodsReported_Inventory_Balance)
                delta_Inventory.append(changesDuringPeriod_Inventory_Balance)
                inventoryProjections_EoP.append(mostRecentlyReported_Inventory_Balance)
            delta_Inventory = [round(eachYearsFigure, 2) for eachYearsFigure in delta_Inventory]
            print("INVENTORY BALANCE (BoP) PROJECTIONS =", inventoryProjections_BoP)
            print("INVENTORY CHANGE PROJECTIONS        =", delta_Inventory)
            print("INVENTORY BALANCE (EoP) PROJECTIONS =", inventoryProjections_EoP)
            assets["Inventory"] = inventoryProjections_EoP

        elif (operation == "(OCA)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ OTHER CURRENT ASSETS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            mostRecentlyReported_OCA_Balance = pullData(source=historicalBalanceSheets,
                                                        itemOfInterest="Other_Current_Assets_(including_Non-Trade_Receivable",
                                                        metric="EoP", specificYear=(timeRange[0] - 1))
            otherCurrentAssetProjections_BoP, otherCurrentAssetProjections_EoP, delta_OCA = [], [], []
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                ocaForecastResults = forecast(mostRecentEoP_Data={"Label": "Other Current Assets",
                                                                  "Figure": mostRecentlyReported_OCA_Balance},
                                              rule="HOLD CONSTANT")
                priorPeriodsReported_OCA_Balance = ocaForecastResults["Future_BoP"]
                changesDuringPeriod_OCA_Balance = ocaForecastResults["Change"]
                mostRecentlyReported_OCA_Balance = ocaForecastResults["Future_EoP"]
                otherCurrentAssetProjections_BoP.append(priorPeriodsReported_OCA_Balance)
                delta_OCA.append(changesDuringPeriod_OCA_Balance)
                otherCurrentAssetProjections_EoP.append(mostRecentlyReported_OCA_Balance)

            print("OTHER CURRENT ASSET BALANCE (BoP) PROJECTIONS =", otherCurrentAssetProjections_BoP)
            print("OTHER CURRENT ASSET BALANCE (EoP) PROJECTIONS =", otherCurrentAssetProjections_EoP)
            assets["Other_Current_Assets_(including_Non-Trade_Receivables)_(OCA)"] = otherCurrentAssetProjections_EoP

        elif (operation == "(Intan)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ INTANGIBLE ASSETS & AMORTIZATION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            expectedFutureAmortizationExpense = [[2014, 1050], [2015, 985], [2016, 833], [2017, 606], [2018, 434]]
            expectedFutureAmortizationExpense = pd.DataFrame(expectedFutureAmortizationExpense,
                                                             columns=['Year', 'Amount'])
            expectedFutureAmortizationExpense.set_index("Year", inplace=True)
            # ExpectedFutureAmortization is reported in MILLIONS (refer to the Intangible Assets section in 10-K)

            intangibleAssetProjections_BoP, intangibleAssetProjections_EoP, intangibleAssetPurchases = [], [], []
            mostRecentlyReported_IntanAssets = pullData(source=historicalBalanceSheets, itemOfInterest="(Goodwill)",
                                                        metric="EoP", specificYear=(timeRange[0] - 1))
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                purchaseForecastResults = forecast(
                    mostRecentEoP_Data={"Label": "IntangibleAssetPurchases", "Figure": 0.00},
                    rule="HOLD CONSTANT")
                purchases = purchaseForecastResults["Future_EoP"]
                intangibleAssetPurchases.append(purchases)

                delta_IntangibleAsset = (purchases - expectedFutureAmortizationExpense.at[currentYear, "Amount"])

                intangibleAssetForecastResults = forecast(mostRecentEoP_Data={"Label": "IntangibleAssets",
                                                                              "Figure": mostRecentlyReported_IntanAssets},
                                                          rule=("ADD_QUANTITY", delta_IntangibleAsset))
                mostRecentlyReported_IntanAssets = intangibleAssetForecastResults["Future_EoP"]
                intangibleAssetProjections_BoP.append(intangibleAssetForecastResults["Future_BoP"])
                intangibleAssetProjections_EoP.append(mostRecentlyReported_IntanAssets)
            amortizationExpenseProjections = list(expectedFutureAmortizationExpense["Amount"])
            amortizationExpenseProjections = list(np.dot(-1, amortizationExpenseProjections))
            print("INTANGIBLE ASSET BALANCE (BoP) PROJECTIONS =", intangibleAssetProjections_BoP)
            print("INTANGIBLE ASSET PURCHASE PROJECTIONS      =", intangibleAssetPurchases)
            print("INTANGIBLE ASSET AMORTIZATION PROJECTIONS  =", amortizationExpenseProjections)
            print("INTANGIBLE ASSET BALANCE (EoP) PROJECTIONS =", intangibleAssetProjections_EoP)
            assets["Acquired_Intangibles_(Goodwill)"] = intangibleAssetProjections_EoP
            supportingItems["IntangibleAssetPurchases"] = intangibleAssetPurchases
            supportingItems["Amortization"] = amortizationExpenseProjections

        elif (operation == "(DTA)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ DEFERRED TAX ASSETS (DTA) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            mostRecentlyReported_DTA = pullData(source=historicalBalanceSheets, itemOfInterest="Deferred_Tax_Assets_(DTA)",
                                                metric="EoP", specificYear=(timeRange[0] - 1))
            deferredTaxAssetProjections = []
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                dtaForecastResults = forecast(mostRecentEoP_Data={"Label": "Deferred Tax Assets (DTA)",
                                                                  "Figure": mostRecentlyReported_DTA},
                                              rule="HOLD CONSTANT")
                deferredTaxAssetProjections.append(dtaForecastResults["Future_EoP"])
                mostRecentlyReported_DTA = dtaForecastResults["Future_EoP"]
            print("DEFERRED TAX ASSET PROJECTIONS =", deferredTaxAssetProjections)
            assets["Deferred_Tax_Assets_(DTA)"] = deferredTaxAssetProjections

        elif (operation == "(ONCA)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ OTHER NON-CURRENT ASSETS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            mostRecentlyReported_ONCA = pullData(source=historicalBalanceSheets,
                                                 itemOfInterest="Other_Non-Current_Assets",
                                                 metric="EoP", specificYear=(timeRange[0] - 1))
            otherNonCurrentAssetProjections = []
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                oncaForecastResults = forecast(mostRecentEoP_Data={"Label": "Other Non-Current Assets",
                                                                   "Figure": mostRecentlyReported_ONCA},
                                               rule="HOLD CONSTANT")
                otherNonCurrentAssetProjections.append(oncaForecastResults["Future_EoP"])
                mostRecentlyReported_ONCA = oncaForecastResults["Future_EoP"]
            print("OTHER NON-CURRENT ASSET PROJECTIONS =", otherNonCurrentAssetProjections)
            assets["Other_Non-Current_Assets_(ONCA)"] = otherNonCurrentAssetProjections

        elif (operation == "(PPE)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ PROPERTY, PLANT, & EQUIPMENT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            depreciation = pullData(source=historicalCashflowStatements, itemOfInterest="Depreciation",
                                    timeRange=(2012, (timeRange[0] - 1)),
                                    metric="EoP")
            capex = pullData(source=historicalCashflowStatements, itemOfInterest="CapEx",
                             timeRange=(2012, (timeRange[0] - 1)),
                             metric="EoP")
            revenue = pullData(source=historicalIncomeStatements, itemOfInterest="Revenue_(Sales)",
                               timeRange=(2012, (timeRange[0] - 1)),
                               metric="EoP")

            capex_TO_sales = doVectorMath([capex, revenue], operation="DIVISION")
            depreciaton_TO_sales = doVectorMath([depreciation, revenue], operation="DIVISION")
            depreciaton_TO_capex = doVectorMath([depreciation, capex], operation="DIVISION")

            depreciationRatios = dictionary_TO_dataframe(dictionary={"CapEx_TO_Sales": capex_TO_sales,
                                                                     "Depreciation_TO_Sales": depreciaton_TO_sales,
                                                                     "Depreciation_TO_CapEx": depreciaton_TO_capex},
                                                         startingYear=2012, endingYear=timeRange[0] - 1,
                                                         scale_units_by="*(1e0)")

            historicalAverage_CapEx_TO_Sales = abs(float(depreciationRatios.loc["CapEx_TO_Sales"].mean()))
            historicalAverage_Depreciaction_TO_Sales = abs(
                float(depreciationRatios.loc["Depreciation_TO_Sales"].mean()))
            historicalAverage_Depreciaction_TO_CapEx = abs(
                float(depreciationRatios.loc["Depreciation_TO_CapEx"].mean()))

            mostRecentlyReported_CapEx = pullData(source=historicalCashflowStatements, itemOfInterest="CapEx",
                                                  metric="EoP", specificYear=(timeRange[0] - 1))
            mostRecentlyReported_Depreciation = pullData(source=historicalCashflowStatements,
                                                         itemOfInterest="Depreciation",
                                                         metric="EoP", specificYear=(timeRange[0] - 1))
            mostRecentlyReported_ppe = pullData(source=historicalBalanceSheets, itemOfInterest="(PP_&_E)",
                                                metric="EoP", specificYear=(timeRange[0] - 1))

            capexProjections, ppeProjections_BoP, ppeProjections_EoP, depreciationProjections = [], [], [], []
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                revenue = pullData(source=projectedIncomeStatements, itemOfInterest="(Sales)",
                                   specificYear=currentYear,
                                   metric="EoP")

                capexForecastResults = forecast(mostRecentEoP_Data={"Label": "Capital Expenditures",
                                                                    "Figure": mostRecentlyReported_CapEx},
                                                proportionAnchor={"Reference": "Revenues", "Figure": revenue,
                                                                  "Fraction": historicalAverage_CapEx_TO_Sales})
                mostRecentlyReported_CapEx = capexForecastResults["Future_EoP"]
                capexProjections.append(mostRecentlyReported_CapEx)

                depreciationForecastResults = forecast(mostRecentEoP_Data={"Label": "Depreciation",
                                                                           "Figure": mostRecentlyReported_Depreciation},
                                                       proportionAnchor={"Reference": "Capital Expenditures",
                                                                         "Figure": mostRecentlyReported_CapEx,
                                                                         "Fraction": historicalAverage_Depreciaction_TO_CapEx})
                mostRecentlyReported_Depreciation = depreciationForecastResults["Future_EoP"]
                depreciationProjections.append(mostRecentlyReported_Depreciation)

                delta_PPE = (mostRecentlyReported_CapEx - mostRecentlyReported_Depreciation)
                ppeForecastResults = forecast(mostRecentEoP_Data={"Label": "PropertyPlantEquipment",
                                                                  "Figure": mostRecentlyReported_ppe},
                                              rule=("ADD_QUANTITY", delta_PPE))
                ppeProjections_BoP.append(ppeForecastResults["Future_BoP"])
                ppeProjections_EoP.append(ppeForecastResults["Future_EoP"])
                mostRecentlyReported_ppe = ppeForecastResults["Future_EoP"]
            depreciationProjections = list(np.dot(-1, depreciationProjections))
            print("Future PROPERTY/PLANT/EQUIPMENT (BoP) Projections =", ppeProjections_BoP)
            print("Future CAPEX Projections                          =", capexProjections)
            print("Future DEPRECIATION Projections                   =", depreciationProjections)
            print("Future PROPERTY/PLANT/EQUIPMENT (EoP) Projections =", ppeProjections_EoP)
            assets["Property,_Plant,_&_Equipment_(PP_&_E)"] = ppeProjections_EoP
            supportingItems["CapitalExpenditures"] = capexProjections
            supportingItems["Depreciation"] = depreciationProjections

        elif (operation == "(AP)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ACCOUNTS PAYABLE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            accountsPayableProjections = []
            mostRecentlyReported_AP = pullData(source=historicalBalanceSheets, itemOfInterest="(AP)",
                                               metric="EoP", specificYear=(timeRange[0] - 1))
            margin = pullData(source=historical_NWC, itemOfInterest="AP_as_%_of_COGS",
                              metric="Average", specificYear=timeRange[0]-1)
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                cogs = abs(pullData(source=projectedIncomeStatements, itemOfInterest="(COGS)", specificYear=currentYear,
                                    metric="EoP"))
                results = forecast(
                    mostRecentEoP_Data={"Label": "Accounts Payable (AP)", "Figure": mostRecentlyReported_AP},
                    proportionAnchor={"Reference": "COGS", "Figure": cogs, "Fraction": margin})
                accountsPayableProjections.append(results["Future_EoP"])
                mostRecentlyReported_AP = results["Future_EoP"]
            print("Accounts Payable (AP) Projection =", accountsPayableProjections)
            liabilities["Accounts_Payable_(AP)"] = accountsPayableProjections

        elif (operation == "(AccrdExp)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ACCRUED EXPENSES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            accruedExpensesProjections = []
            mostRecentlyReported_AccrdExp = pullData(source=historicalBalanceSheets, itemOfInterest="(AccrdExp)",
                                                     metric="EoP", specificYear=(timeRange[0] - 1))
            margin = pullData(source=historical_NWC, itemOfInterest="AccrdExp_as_%_of_Sales",
                              metric="Avg", specificYear=timeRange[0]-1)
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                sales = pullData(source=projectedIncomeStatements, itemOfInterest="(Sales)",
                                 specificYear=currentYear,
                                 metric="EoP")
                results = forecast(
                    mostRecentEoP_Data={"Label": "Accrued Expenses", "Figure": mostRecentlyReported_AccrdExp},
                    proportionAnchor={"Reference": "Revenue", "Figure": sales, "Fraction": margin})
                accruedExpensesProjections.append(results["Future_EoP"])
                mostRecentlyReported_AccrdExp = results["Future_EoP"]
            print("Accrued Expenses (AccrdExp) Projection =", accruedExpensesProjections)
            liabilities["Accrued_Expenses_&_Deferred_Revenues_(AccrdExp)"] = accruedExpensesProjections

        elif (operation == "(LTD)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LONG-TERM DEBT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            debtSchedule = [[2016, "Floating-Rate", 1000.00, 0.51],
                            [2016, "Fixed-Rate",    1500.00, 0.51],
                            [2018, "Floating-Rate", 2000.00, 1.10],
                            [2018, "Fixed-Rate",    4000.00, 1.08],
                            [2023, "Fixed-Rate",    5500.00, 2.44],
                            [2043, "Fixed-Rate",    3000.00, 3.91]]
            # Notional amounts are in MILLIONS (refer to the Long-Term Debt section in 10-K)
            debtSchedule = pd.DataFrame(debtSchedule, columns=['Maturity', 'Type', 'Principal', 'EffectiveRate'])
            debtSchedule.set_index("Maturity", inplace=True)
            plannedEvents = [[2014, 0.00,     0.00, 100.00],
                             [2015, 0.00,     0.00, 100.00],
                             [2016, 0.00, -2500.00, 100.00],
                             [2017, 0.00,     0.00, 100.00],
                             [2018, 0.00, -6000.00, 100.00]]
            # Repayment amounts are in MILLIONS (refer to the Long-Term Debt section in 10-K)
            plannedEvents = pd.DataFrame(plannedEvents,
                                         columns=['Year', 'Borrowings', '(Payments)', '%_of_IE_paid_via_CASH'])
            plannedEvents.set_index("Year", inplace=True)

            ltdProjections_BoP, ltdProjections_EoP, paymentProjections, borrowingProjections, = [], [], [], []
            pikAccrualProjections, ltdIEprojections = [], []
            mostRecentlyReported_LTD_Balance = pullData(source=historicalBalanceSheets, itemOfInterest="(LTD)",
                                                        specificYear=(timeRange[0] - 1), metric="EoP")

            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                amt_BORROWED_ForCurrentYear, amt_PAID_ForCurrentYear = 0.00, 0.00
                pik_accrual_for_the_year, interestExpenseForTheYear = 0.00, 0.00

                if (currentYear in list(debtSchedule.index)):
                    debtSchedule = debtSchedule.drop(currentYear)
                    interestExpenseForTheYear = debtSchedule["EffectiveRate"].div(100).multiply(
                        debtSchedule["Principal"]).sum()
                else:
                    interestExpenseForTheYear = debtSchedule["EffectiveRate"].div(100).multiply(
                        debtSchedule["Principal"]).sum()
                print("The firm will pay $", interestExpenseForTheYear, "in Long-Term Debt (LTD) interest expense (IE)",
                      "for FY", currentYear)
                ltdIEprojections.append(interestExpenseForTheYear)

                if (float(plannedEvents.at[currentYear, "%_of_IE_paid_via_CASH"]) < 100.00):
                    percentOf_IE_as_PIK_accrual = (
                            1 - float(plannedEvents.at[currentYear, "%_of_IE_paid_via_CASH"]) / 100)
                    pik_accrual_for_the_year = (interestExpenseForTheYear * percentOf_IE_as_PIK_accrual)
                    print("The firm has opted for", round(percentOf_IE_as_PIK_accrual * 100, 2),
                          "% PIK accrual from interest expense (IE) for FY",
                          currentYear)
                pikAccrualProjections.append(pik_accrual_for_the_year)

                if (float(plannedEvents.at[currentYear, "Borrowings"]) > 0.00):
                    amt_BORROWED_ForCurrentYear = float(plannedEvents.at[currentYear, "Borrowings"])
                    print("The firm borrowed $", amt_BORROWED_ForCurrentYear, "for FY", currentYear)
                borrowingProjections.append(amt_BORROWED_ForCurrentYear)

                if (float(plannedEvents.at[currentYear, "(Payments)"]) < 0.00):
                    amt_PAID_ForCurrentYear = float(plannedEvents.at[currentYear, "(Payments)"])
                    print("The firm made principal payments of $", amt_PAID_ForCurrentYear * -1, "for FY",
                          currentYear)
                paymentProjections.append(amt_PAID_ForCurrentYear)

                changeToLTDduringPeriod = (amt_BORROWED_ForCurrentYear + amt_PAID_ForCurrentYear + pik_accrual_for_the_year)

                ltdForecastResults = forecast(mostRecentEoP_Data={"Label": "Long Term Debt",
                                                                  "Figure": mostRecentlyReported_LTD_Balance},
                                              rule=("ADD_QUANTITY", changeToLTDduringPeriod))
                ltdProjections_BoP.append(ltdForecastResults["Future_BoP"])
                ltdProjections_EoP.append(ltdForecastResults["Future_EoP"])

                priorPeriod_LTD_Balance = ltdForecastResults["Future_BoP"]
                mostRecentlyReported_LTD_Balance = ltdForecastResults["Future_EoP"]
                average_LTD_Balance = ((priorPeriod_LTD_Balance + mostRecentlyReported_LTD_Balance) / 2)
                impliedInterestRate = (interestExpenseForTheYear / average_LTD_Balance)
                print("The firm had an implied weighted-average interest rate of [(", interestExpenseForTheYear, "/",
                      round(average_LTD_Balance, 2), ") =", round(impliedInterestRate * 100, 2), "%] for FY", currentYear)

            ltdIEprojections = list(np.dot(-1, ltdIEprojections))
            paymentProjections = list(np.dot(-1, paymentProjections))
            print("LTD Balance Projections (BoP)       =", ltdProjections_BoP)
            print("LTD Interest Expense Projections    =", list(np.dot(-1, ltdIEprojections)))
            print("LTD PIK Accrual Projections         =", pikAccrualProjections)
            print("LTD Borrowing Projections           =", borrowingProjections)
            print("LTD Principal Repayment Projections =", list(np.dot(-1, paymentProjections)))
            print("LTD Balance Projections (EoP)       =", ltdProjections_EoP)
            liabilities["Long_Term_Debt_(LTD)"] = ltdProjections_EoP
            supportingItems["Borrowing"] = borrowingProjections
            supportingItems["PIK_Accruals"] = pikAccrualProjections
            supportingItems["InterestExpenseForLTD"] = ltdIEprojections
            supportingItems["DebtRepayments"] = paymentProjections

        elif (operation == "(ONCL)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ OTHER NON-CURRENT LIABILITIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            mostRecentlyReported_ONCL = pullData(source=historicalBalanceSheets,
                                                 itemOfInterest="Other_Non-Current_Liabilities",
                                                 metric="EoP", specificYear=(timeRange[0] - 1))
            otherNonCurrentLiabilitiesProjections = []
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                onclForecastResults = forecast(mostRecentEoP_Data={"Label": "Other Non-Current Liabilities",
                                                                   "Figure": mostRecentlyReported_ONCL},
                                               rule=("ADD_QUANTITY", 3000.00))
                otherNonCurrentLiabilitiesProjections.append(onclForecastResults["Future_EoP"])
                mostRecentlyReported_ONCL = onclForecastResults["Future_EoP"]
            print("OTHER NON-CURRENT LIABILITIES PROJECTIONS =", otherNonCurrentLiabilitiesProjections)
            liabilities["Other_Non-Current_Liabilities_(ONCL)"] = otherNonCurrentLiabilitiesProjections

        elif (operation == "(CapStock)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CAPITAL STOCK ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            mostRecentlyReported_CommonStock = pullData(source=historicalBalanceSheets, itemOfInterest="(APIC)",
                                                        metric="EoP", specificYear=(timeRange[0] - 1))
            mostRecentlyReported_StockComp = pullData(source=historicalCashflowStatements, itemOfInterest="StockBasedCompensation",
                                                      metric="EoP", specificYear=(timeRange[0] - 1))
            mostRecentlyReported_SGA = pullData(source=historicalIncomeStatements, itemOfInterest="(SG_&_A)",
                                                metric="EoP", specificYear=(timeRange[0] - 1))
            mostRecentlyReported_R_and_D = pullData(source=historicalIncomeStatements, itemOfInterest="(R_&_D)",
                                                    metric="EoP", specificYear=(timeRange[0] - 1))
            mostRecentlyReported_COGS = pullData(source=historicalIncomeStatements, itemOfInterest="(COGS)",
                                                 metric="EoP", specificYear=(timeRange[0] - 1))

            stockComp_TO_OperatingExpenses = (mostRecentlyReported_StockComp / (mostRecentlyReported_SGA + mostRecentlyReported_R_and_D + mostRecentlyReported_COGS))

            commonStockProjections_BoP, commonStockProjections_EoP = [], []
            stockCompProjections, stockIssuanceProjections = [], []
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                currentYear_COGS = pullData(source=projectedIncomeStatements, itemOfInterest="Cost_of_Sales_(COGS)",
                                            metric="EoP", specificYear=int(currentYear))
                currentYear_SGA = pullData(source=projectedIncomeStatements, itemOfInterest="(SG_&_A)",
                                           metric="EoP", specificYear=currentYear)
                currentYear_R_and_D = pullData(source=projectedIncomeStatements, itemOfInterest="(R_&_D)",
                                               metric="EoP", specificYear=currentYear)
                currentYear_OperatingExpenses = (currentYear_COGS + currentYear_SGA + currentYear_R_and_D)

                stockCompForecastResults = forecast(mostRecentEoP_Data={"Label": "Stock-Based Compensation",
                                                                        "Figure": mostRecentlyReported_StockComp},
                                                    proportionAnchor={"Reference": "Operating Expenses",
                                                                      "Figure": abs(currentYear_OperatingExpenses),
                                                                      "Fraction": abs(stockComp_TO_OperatingExpenses)})
                stockCompProjections.append(stockCompForecastResults["Future_EoP"])
                mostRecentlyReported_StockComp = stockCompForecastResults["Future_EoP"]

                stockIssuanceForecastResults = forecast(mostRecentEoP_Data={"Label": "Stock Issuance", "Figure": 0.00},
                                                        rule="HOLD CONSTANT")
                stockIssuanceProjections.append(stockIssuanceForecastResults["Future_EoP"])

                changeInCommonStockDuringPeriod = (
                            stockCompForecastResults["Future_EoP"] + stockIssuanceForecastResults["Future_EoP"])

                commonStockForecastResults = forecast(mostRecentEoP_Data={"Label": "Common Stock",
                                                                          "Figure": mostRecentlyReported_CommonStock},
                                                      rule=("ADD_QUANTITY", changeInCommonStockDuringPeriod))
                commonStockProjections_BoP.append(commonStockForecastResults["Future_BoP"])
                commonStockProjections_EoP.append(commonStockForecastResults["Future_EoP"])
                mostRecentlyReported_CommonStock = commonStockForecastResults["Future_EoP"]

            print("COMMON STOCK BALANCE PROJECTIONS (BoP)  =", commonStockProjections_BoP)
            print("COMMON STOCK COMPENSATION PROJECTIONS   =", stockCompProjections)
            print("COMMON STOCK ISSUANCE PROJECTIONS       =", stockIssuanceProjections)
            print("COMMON STOCK BALANCE PROJECTIONS (EoP)  =", commonStockProjections_EoP)
            equity["Common_Stock_/_Additional_Paid-In_Capital_(APIC)_(CommonEquity)"] = commonStockProjections_EoP
            supportingItems["StockCompensation"] = stockCompProjections
            supportingItems["StockIssuance"] = stockIssuanceProjections

        elif (operation == "(TS)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TREASURY STOCK ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            mostRecentlyReported_TreasuryStock = 0.00
            mostRecentlyReported_StockBuyback = pullData(source=historicalCashflowStatements,
                                                         itemOfInterest="StockBuyback",
                                                         metric="EoP", specificYear=(timeRange[0] - 1))
            treasuryStockProjections_BoP, treasuryStockProjections_EoP, stockBuybackProjections = [], [], []
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                stockBuybackForecastResults = forecast(mostRecentEoP_Data={"Label": "Stock Repurchases",
                                                                           "Figure": mostRecentlyReported_StockBuyback},
                                                       rule="HOLD CONSTANT")
                stockBuybackProjections.append(stockBuybackForecastResults["Future_EoP"])
                mostRecentlyReported_StockBuyback = stockBuybackForecastResults["Future_EoP"]

                treasuryStockForecastResults = forecast(mostRecentEoP_Data={"Label": "Treasury Stock",
                                                                            "Figure": mostRecentlyReported_TreasuryStock},
                                                        rule=("ADD_QUANTITY", mostRecentlyReported_StockBuyback))
                treasuryStockProjections_BoP.append(treasuryStockForecastResults["Future_BoP"])
                treasuryStockProjections_EoP.append(treasuryStockForecastResults["Future_EoP"])
                mostRecentlyReported_TreasuryStock = treasuryStockForecastResults["Future_EoP"]

            print("TREASURY STOCK PROJECTIONS (BoP) =", treasuryStockProjections_BoP)
            print("COMMON STOCK REPURCHASES         =", stockBuybackProjections)
            print("TREASURY STOCK PROJECTIONS (EoP) =", treasuryStockProjections_EoP)
            equity["Treasury_Stock_(TS)"] = treasuryStockProjections_EoP
            supportingItems["StockBuybacks"] = stockBuybackProjections

        elif (operation == "(RE)"):
            ''' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RETAINED EARNINGS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            mostRecentlyReported_NetIncome = pullData(source=historicalIncomeStatements, itemOfInterest="Net_Income",
                                                      specificYear=(timeRange[0] - 1), metric="EoP")
            mostRecentlyReported_RetainedEarnings = pullData(source=historicalBalanceSheets, itemOfInterest="(RE)",
                                                             metric="EoP", specificYear=(timeRange[0] - 1))
            mostRecentlyReported_DividendPayout = pullData(source=historicalCashflowStatements,
                                                           itemOfInterest="DividendsPaid",
                                                           specificYear=(timeRange[0] - 1), metric="EoP")
            mostRecentlyReported_PayoutRatio = abs(mostRecentlyReported_DividendPayout / mostRecentlyReported_NetIncome)

            netIncomeProjections = []
            retainedEarningsProjections_BoP, retainedEarningsProjections_EoP, dividendPayoutProjections = [], [], []
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                currentYearNetIncome = pullData(source=projectedIncomeStatements, itemOfInterest="Net_Income",
                                                metric="EoP", specificYear=currentYear)
                netIncomeProjections.append(currentYearNetIncome)

                dividendPayoutForecastResults = forecast(mostRecentEoP_Data={"Label": "Dividend Payout",
                                                                             "Figure": mostRecentlyReported_DividendPayout},
                                                         proportionAnchor={"Reference": "Net Income",
                                                                           "Figure": currentYearNetIncome,
                                                                           "Fraction": mostRecentlyReported_PayoutRatio})
                mostRecentlyReported_DividendPayout = dividendPayoutForecastResults["Future_EoP"]
                changeInRetainedEarningsForCurrentYear = (currentYearNetIncome - mostRecentlyReported_DividendPayout)
                dividendPayoutProjections.append(mostRecentlyReported_DividendPayout)
                retainedEarningsForecastResults = forecast(mostRecentEoP_Data={"Label": "Retained Earnings",
                                                                               "Figure": mostRecentlyReported_RetainedEarnings},
                                                           rule=("ADD_QUANTITY", changeInRetainedEarningsForCurrentYear))
                retainedEarningsProjections_BoP.append(retainedEarningsForecastResults["Future_BoP"])
                retainedEarningsProjections_EoP.append(retainedEarningsForecastResults["Future_EoP"])
                mostRecentlyReported_RetainedEarnings = retainedEarningsForecastResults["Future_EoP"]
            dividendPayoutProjections = list(np.dot(-1, dividendPayoutProjections))
            print("RETAINED EARNINGS PROJECTIONS (BoP) =", retainedEarningsProjections_BoP)
            print("NET EARNINGS PROJECTIONS            =", netIncomeProjections)
            print("DIVIDEND PAYOUT PROJECTIONS         =", dividendPayoutProjections)
            print("RETAINED EARNINGS PROJECTIONS (EoP) =", retainedEarningsProjections_EoP)
            equity["Retained_Earnings_/_Accumulated_Deficit_(RE)"] = retainedEarningsProjections_EoP
            supportingItems["DividendPayout"] = dividendPayoutProjections

        elif (operation == "(OCI)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ OTHER COMPREHENSIVE INCOME ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            mostRecentlyReported_OCI = pullData(source=historicalBalanceSheets,
                                                itemOfInterest="Other_Comprehensive_Earnings",
                                                metric="EoP", specificYear=(timeRange[0] - 1))
            otherComprehensiveIncomeProjections = []
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                ociForecastResults = forecast(mostRecentEoP_Data={"Label": "Other Comprehensive Income (OCI)",
                                                                  "Figure": mostRecentlyReported_OCI},
                                              rule="HOLD CONSTANT")
                otherComprehensiveIncomeProjections.append(ociForecastResults["Future_EoP"])
                mostRecentlyReported_OCI = ociForecastResults["Future_EoP"]
            print("OTHER COMPREHENSIVE INCOME PROJECTIONS =", otherComprehensiveIncomeProjections)
            equity["Other_Comprehensive_Earnings"] = otherComprehensiveIncomeProjections

        elif (operation == "(Cash)"):
            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CASH & EQUIVALENTS & INTEREST INCOME ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
            # SPECIAL NOTE: Forecasting 'Cash' (BS) & 'Revolver' (BS) requires:  * PROJECTED(BS) & PROJECTED(SCF) for INPUT
            #                                                                    * PROJECTED(IS) & PROJECTED(SCF) for OUTPUT
            minimumCashBalanceDesired = [[2014, 5000.00, 0.0103, 0.02],
                                         [2015, 5000.00, 0.0103, 0.02],
                                         [2016, 5000.00, 0.0103, 0.02],
                                         [2017, 5000.00, 0.0103, 0.02],
                                         [2018, 5000.00, 0.0103, 0.02]]
            minimumCashBalanceDesired = pd.DataFrame(minimumCashBalanceDesired,
                                                     columns=['Year', 'ReqMin', 'CashRoR', 'RevolverIR'])
            minimumCashBalanceDesired.set_index('Year', inplace=True)

            revolverProjections_BoP, revolverProjections_EoP, delta_RevolverProjections = [], [], []
            revolverIE_Projections, netCashflowThroughoutPeriodProjections = [], []
            cashProjections_BoP, cashProjections_EoP, interestIncomeProjections = [], [], []

            mostRecentlyReported_CashBalance = pullData(source=historicalBalanceSheets, itemOfInterest="(Cash)",
                                                        metric="EoP", specificYear=(timeRange[0] - 1))
            mostRecentlyReported_RevolverBalance = pullData(source=historicalBalanceSheets, itemOfInterest="Revolver",
                                                            metric="EoP", specificYear=(timeRange[0] - 1))

            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                currentYear_NET_TOTAL_CASHFLOW = pullData(source=projectedCashflowStatements["NetCashflow"], itemOfInterest="Total_CF",
                                                          metric="EoP", specificYear=currentYear)

                changeInCashOverTheYear = currentYear_NET_TOTAL_CASHFLOW
                netCashflowThroughoutPeriodProjections.append(changeInCashOverTheYear)

                cashForecastResults = forecast(mostRecentEoP_Data={"Label": "Cash & Equivalents",
                                                                   "Figure": mostRecentlyReported_CashBalance},
                                               rule=("ADD_QUANTITY", changeInCashOverTheYear))
                priorPeriod_Cash_Balance = cashForecastResults["Future_BoP"]
                currentPeriod_Cash_Balance = cashForecastResults["Future_EoP"]

                cashProjections_BoP.append(priorPeriod_Cash_Balance)
                cashProjections_EoP.append(currentPeriod_Cash_Balance)

                expectedRateOfReturnOnCash = minimumCashBalanceDesired.at[currentYear, "CashRoR"]

                currentPeriod_Avg_Cash_Balance = ((priorPeriod_Cash_Balance + currentPeriod_Cash_Balance) / 2)

                interestIncomeFromCashHoldings = round((expectedRateOfReturnOnCash * currentPeriod_Avg_Cash_Balance), 2)
                interestIncomeProjections.append(interestIncomeFromCashHoldings)
                mostRecentlyReported_CashBalance = currentPeriod_Cash_Balance

            print("CASH BALANCE PROJECTIONS (BoP) =", cashProjections_BoP)
            print("NET CASHFLOW THROUGHOUT PERIOD =", netCashflowThroughoutPeriodProjections)
            print("CASH BALANCE PROJECTIONS (EoP) =", cashProjections_EoP)
            print("\n")
            print("CASH INTEREST PROJECTIONS      =", interestIncomeProjections)
            assets["Cash_&_Equivalents_(including_ST_&_LT_Securities)_(Cash)"] = cashProjections_EoP
            supportingItems["InterestIncomeFromCashHoldings"] = interestIncomeProjections
            print("\n")

            '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ REVOLVING LINE OF CREDIT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

            for currentYear in range(timeRange[0], (timeRange[1] + 1)):

                currentYear_AR_Forecast = pullData(source=projectedBalanceSheets["Assets"], itemOfInterest="(AR)",
                                                   metric="EoP", specificYear=currentYear)
                currentYear_Inventory_Forecast = pullData(source=projectedBalanceSheets["Assets"], itemOfInterest="Inventory",
                                                          metric="EoP", specificYear=currentYear)

                currentYear_CF_from_OPS = pullData(source=projectedCashflowStatements["NetCashflow"],
                                                   itemOfInterest="CF_from_OPS",
                                                   metric="EoP", specificYear=currentYear)
                currentYear_CF_from_INV = pullData(source=projectedCashflowStatements["NetCashflow"],
                                                   itemOfInterest="CF_from_INV",
                                                   metric="EoP", specificYear=currentYear)
                currentYear_CF_from_FIN_EXCLUDING_REVOLVER_CASHFLOWS = 0.00
                for lineItem in list(projectedCashflowStatements["Financing"].keys()):
                    if(lineItem == "delta_Revolver"):
                        continue

                    currentYear_lineItemValue = pullData(source=projectedCashflowStatements["Financing"],
                                                         itemOfInterest=lineItem,
                                                         metric="EoP", specificYear=currentYear)

                    currentYear_CF_from_FIN_EXCLUDING_REVOLVER_CASHFLOWS += currentYear_lineItemValue

                currentYear_NET_TOTAL_CASHFLOW = (currentYear_CF_from_OPS +
                                                  currentYear_CF_from_INV +
                                                  currentYear_CF_from_FIN_EXCLUDING_REVOLVER_CASHFLOWS)

                '''How much does the firm need to draw from the Revolver? (Revolver Needs Analysis)'''

                cash_BoP = cashProjections_BoP[currentYear - timeRange[0]]
                cash_req = minimumCashBalanceDesired.at[currentYear, "ReqMin"]
                cash_SURPLUS_or_DEFICIT = (cash_BoP - cash_req)
                cash_AVAILABLE_or_NEEDED_to_PAYDOWN_or_DRAW_from_revolver = (cash_SURPLUS_or_DEFICIT + currentYear_NET_TOTAL_CASHFLOW)

                deltaRev = -1 * min(mostRecentlyReported_RevolverBalance, cash_AVAILABLE_or_NEEDED_to_PAYDOWN_or_DRAW_from_revolver)
                delta_RevolverProjections.append(deltaRev)
                revolverForecastResults = forecast(mostRecentEoP_Data={"Label": "Revolver",
                                                                       "Figure": mostRecentlyReported_RevolverBalance},
                                                   rule=("ADD_QUANTITY", deltaRev))
                revolverProjections_BoP.append(revolverForecastResults["Future_BoP"])
                revolverProjections_EoP.append(revolverForecastResults["Future_EoP"])
                mostRecentlyReported_RevolverBalance = revolverForecastResults["Future_EoP"]

                currentYear_InterestRateOnRevolver = minimumCashBalanceDesired.at[currentYear, "RevolverIR"]
                currentYear_AvgRevolverBalance = ((revolverForecastResults["Future_BoP"] + revolverForecastResults["Future_EoP"]) / 2)
                currentYear_InterestExpenseForRevolver = (currentYear_InterestRateOnRevolver * currentYear_AvgRevolverBalance)
                revolverIE_Projections.append(currentYear_InterestExpenseForRevolver)

                props = (0.90, 0.70)
                revolverCreditLimit = ((props[0] * currentYear_AR_Forecast) + (props[1] * currentYear_Inventory_Forecast))

                # print(currentYear, "(AR) =", currentYear_AR_Forecast, "|",
                #       currentYear, "Inventory =", round(currentYear_Inventory_Forecast, 2), "|",
                #       currentYear, "Revolving Credit Limit = [(", props[0], ") * (AR) + (", props[1], ") * (Invnt)] =",
                #       round(revolverCreditLimit, 2))

                if(revolverForecastResults["Future_EoP"] > revolverCreditLimit):
                    print("^^^^^ WARNING: FIRM HAS EXCEEDED ITS REVOLVING CREDIT LIMIT! ^^^^^")

            revolverIE_Projections = list(np.dot(-1, revolverIE_Projections))
            print("REVOLVER BALANCE PROJECTIONS (BoP)         =", revolverProjections_BoP)
            print("REVOLVER DRAW / (RePMT) PROJECTIONS        =", delta_RevolverProjections)
            print("REVOLVER INTEREST EXPENSE PROJECTIONS      =", list(np.dot(-1, revolverIE_Projections)))
            print("REVOLVER BALANCE PROJECTIONS (EoP)         =", revolverProjections_EoP)
            liabilities["Revolver"] = revolverProjections_EoP
            supportingItems["delta_Revolver"] = delta_RevolverProjections
            supportingItems["InterestExpenseForRevolver"] = revolverIE_Projections

        temp = {"Assets": reformatStatement(input=dictionary_TO_dataframe(dictionary=assets,
                                                                          startingYear=timeRange[0],
                                                                          endingYear=timeRange[1])),
                "Liabilities": reformatStatement(input=dictionary_TO_dataframe(dictionary=liabilities,
                                                                               startingYear=timeRange[0],
                                                                               endingYear=timeRange[1])),
                "Equity": reformatStatement(input=dictionary_TO_dataframe(dictionary=equity,
                                                                          startingYear=timeRange[0],
                                                                          endingYear=timeRange[1])),
                "SupplementalData": reformatStatement(input=dictionary_TO_dataframe(dictionary=supportingItems,
                                                                                    startingYear=timeRange[0],
                                                                                    endingYear=timeRange[1]))}
        projectedSources["BalanceSheet"] = temp
        print("{", operation, "POST-PROJECTION BALANCE CHECK}")
        for currentYear in range(timeRange[0], (timeRange[1] + 1)):
            verifyBalance(dictionaryForDataframe=temp, year=currentYear)
        print("\n")

    if (stage == "1"):
        proj = projectedSources["BalanceSheet"]
    elif (stage == "2"):
        residualImbalances = []
        for yearToBeTested in range(timeRange[0], (timeRange[1] + 1)):
            residualImbalances.append(verifyBalance(dictionaryForDataframe=projectedSources["BalanceSheet"],
                                                    year=yearToBeTested))
        if(sum(residualImbalances) != 0.0 and operationsSequence[0] == "(Cash)"):
            projected["IncomeStatement"] = forecastIncomeStatement(historicalSources=historicalSources,
                                                                   projectedSources=projectedSources,
                                                                   timeRange=(timeRange[0], timeRange[1]), stage="2")
            projected["BalanceSheet"] = forecastBalanceSheet(historicalSources=historicalSources,
                                                             projectedSources=projectedSources,
                                                             timeRange=(timeRange[0], timeRange[1]),
                                                             stage="2", operationsSequence=["(RE)"])
        elif (sum(residualImbalances) != 0.0 and operationsSequence[0] == "(RE)"):
            projectedSources["CashflowStatement"] = forecastCashflowStatement(historicalSources=historicalSources,
                                                                              projectedSources=projectedSources,
                                                                              timeRange=(timeRange[0], timeRange[1]))
            projectedSources["BalanceSheet"] = forecastBalanceSheet(historicalSources=historicalSources,
                                                                    projectedSources=projectedSources,
                                                                    timeRange=(timeRange[0], timeRange[1]),
                                                                    stage="2", operationsSequence=["(Cash)"])
        print("{*** PROJECTED MODEL HAS SUCCESSFULLY BALANCED ***}")
        proj = projectedSources
    return proj

def forecastCashflowStatement(historicalSources=None, projectedSources=None, timeRange=None):
    def reconcileRecords(historicalSources=None, projectedSources=None):

        historicalIncomeStatements = historicalSources["IncomeStatement"]
        historicalBalanceSheets = historicalSources["BalanceSheet"]
        historicalCashflowStatements = historicalSources["CashflowStatement"]

        projectedIncomeStatements = projectedSources["IncomeStatement"]
        projectedBalanceSheets = projectedSources["BalanceSheet"]

        for section in ["Assets", "Liabilities", "Equity"]:
            for lineItem in list(projectedBalanceSheets[section].keys()):
                year = list(historicalBalanceSheets[lineItem].columns)[-1]  # reference LAST year in HISTORICAL
                #print("*** RECONCILING PROJECTED '", lineItem, "' OF {", section, "} WITH", year, "HISTORICAL '", lineItem, "'")
                requestedInfo = historicalBalanceSheets[lineItem].at[lineItem + " End_of_Period_(EoP)", year]
                delta = (projectedBalanceSheets[section][lineItem].at[lineItem + " End_of_Period_(EoP)", (year + 1)] - requestedInfo)

                if(requestedInfo == 0.00):
                    percentChange = "Not Available (division by zero)"
                else:
                    percentChange = (((requestedInfo + delta) / requestedInfo) - 1) * 100
                averageValue = round((requestedInfo + (requestedInfo + delta)) / 2, 2)

                projectedBalanceSheets[section][lineItem].at[
                    lineItem + " Beginning_of_Period_(BoP)", (year + 1)] = requestedInfo
                projectedBalanceSheets[section][lineItem].at[
                    lineItem + " Change_during_Period_(Delta)", (year + 1)] = delta
                projectedBalanceSheets[section][lineItem].at[
                    lineItem + " Percent_Change_during_Period", (year + 1)] = percentChange
                projectedBalanceSheets[section][lineItem].at[
                    lineItem + " Average_between_Points_in_Time", (year + 1)] = averageValue

    projectedIncomeStatements = projectedSources["IncomeStatement"]
    projectedBalanceSheets = projectedSources["BalanceSheet"]

    reconcileRecords(historicalSources=historicalSources, projectedSources=projectedSources)

    netIncomeProjections, stockCompProjections, depre_AND_amortProjections = [], [], []
    delta_AR_Projections, delta_Inventory_Projections, delta_OCA_Projections = [], [], []
    delta_DTA_Projections, delta_ONCA_Projections, delta_AP_Projections = [], [], []
    delta_AccrdExp_Projections, delta_ONCL_Projections, delta_PIK_AccrualProjections = [], [], []
    capexProjections, intangibleAssetPurchaseProjections = [], []
    delta_LTD_Projections, dividendPayoutProjections = [], []
    stockIssuanceProjections, stockBuybackProjections, delta_OCI_Projections = [], [], []
    delta_Revolver_Projections = []

    cashflow_from_ops, cashflow_from_inv, cashflow_from_fin, net_cashflow = {}, {}, {}, {}
    cf_from_OPS_Projections, cf_from_INV_Projections, cf_from_FIN_Projections = [], [], []

    proj = None

    theOrderLineItemsAreToBeForecasted_OPS = ["Net_Income", "Depreciation_&_Amortization_(D_&_A)", "Stock_Compensation",
                                              "delta_(AR)", "delta_Inventory", "delta_(OCA)", "delta_(DTA)", "delta_(ONCA)",
                                              "delta_(AP)", "delta_(AccrdExp)", "delta_(ONCL)", "PIK_Accrual"]
    theOrderLineItemsAreToBeForecasted_INV = ["Capital_Expenditures_(CapEx)", "Intangible_Asset_Purchases"]
    theOrderLineItemsAreToBeForecasted_FIN = ["delta_(LTD)", "Dividends_Paid", "Stock_Buybacks", "Stock_Issuance",
                                              "delta_(OCI)", "delta_Revolver"]

    '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CF from OPERATIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
    print("*******************************")
    print("*** PROCESSING CF_from_OPS ***")
    print("*******************************")
    for cf_from_OPS_item in theOrderLineItemsAreToBeForecasted_OPS:
        if (cf_from_OPS_item == "Net_Income"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                netIncome = pullData(source=projectedIncomeStatements, itemOfInterest="Net_Income",
                                     metric="EoP", specificYear=currentYear)
                netIncomeProjections.append(netIncome)
                print(currentYear, "Net Income =", netIncome)
            cashflow_from_ops[cf_from_OPS_item] = netIncomeProjections
        elif (cf_from_OPS_item == "Depreciation_&_Amortization_(D_&_A)"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                depreciation = pullData(source=projectedBalanceSheets["SupplementalData"], itemOfInterest="Depreciation",
                                        metric="EoP", specificYear=currentYear)
                amortization = pullData(source=projectedBalanceSheets["SupplementalData"], itemOfInterest="Amortization",
                                        metric="EoP", specificYear=currentYear)
                depre_AND_amort = abs(depreciation + amortization) # For the (SCF), we take the ABSOLUTE VALUE of this
                depre_AND_amortProjections.append(depre_AND_amort)
                print(currentYear, "abs[(Depreciation =", depreciation, ") + (Amortization =", amortization, ")] =", depre_AND_amort)
            cashflow_from_ops[cf_from_OPS_item] = depre_AND_amortProjections
        elif (cf_from_OPS_item == "Stock_Compensation"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                stockComp = pullData(source=projectedBalanceSheets["SupplementalData"], itemOfInterest="StockCompensation",
                                     metric="EoP", specificYear=currentYear)
                stockCompProjections.append(stockComp)
                print(currentYear, "Stock-Based Compensation =", stockComp)
            cashflow_from_ops[cf_from_OPS_item] = stockCompProjections
        elif (cf_from_OPS_item == "delta_(AR)"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                delta_AR = pullData(source=projectedBalanceSheets["Assets"], itemOfInterest="(AR)",
                                    metric="Delta", specificYear=currentYear)


                delta_AR_Projections.append(-1 * delta_AR)


                print(currentYear, "Change in (AR) Balance =", delta_AR)
            cashflow_from_ops[cf_from_OPS_item] = delta_AR_Projections
        elif (cf_from_OPS_item == "delta_Inventory"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                delta_Inventory = pullData(source=projectedBalanceSheets["Assets"], itemOfInterest="Inventory",
                                           metric="Delta", specificYear=currentYear)


                delta_Inventory_Projections.append(-1 * delta_Inventory)


                print(currentYear, "Change in (Inventory) Balance =", delta_Inventory)
            cashflow_from_ops[cf_from_OPS_item] = delta_Inventory_Projections
        elif (cf_from_OPS_item == "delta_(OCA)"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                delta_OCA = pullData(source=projectedBalanceSheets["Assets"], itemOfInterest="(OCA)",
                                     metric="Delta", specificYear=currentYear)


                delta_OCA_Projections.append(-1 * delta_OCA)


                print(currentYear, "Change in (OCA) Balance =", delta_OCA)
            cashflow_from_ops[cf_from_OPS_item] = delta_OCA_Projections
        elif (cf_from_OPS_item == "delta_(DTA)"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                delta_DTA = pullData(source=projectedBalanceSheets["Assets"], itemOfInterest="(DTA)",
                                     metric="Delta", specificYear=currentYear)

                delta_DTA_Projections.append(-1 * delta_DTA)


                print(currentYear, "Change in (DTA) Balance =", delta_DTA)
            cashflow_from_ops[cf_from_OPS_item] = delta_DTA_Projections
        elif (cf_from_OPS_item == "delta_(ONCA)"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                delta_ONCA = pullData(source=projectedBalanceSheets["Assets"], itemOfInterest="(ONCA)",
                                      metric="Delta", specificYear=currentYear)


                delta_ONCA_Projections.append(-1 * delta_ONCA)


                print(currentYear, "Change in (ONCA) Balance =", delta_ONCA)
            cashflow_from_ops[cf_from_OPS_item] = delta_ONCA_Projections
        elif (cf_from_OPS_item == "delta_(AP)"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                delta_AP = pullData(source=projectedBalanceSheets["Liabilities"], itemOfInterest="(AP)",
                                    metric="Delta", specificYear=currentYear)
                delta_AP_Projections.append(delta_AP)
                print(currentYear, "Change in (AP) Balance=", delta_AP)
            cashflow_from_ops[cf_from_OPS_item] = delta_AP_Projections
        elif (cf_from_OPS_item == "delta_(AccrdExp)"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                delta_AccrdExp = pullData(source=projectedBalanceSheets["Liabilities"], itemOfInterest="(AccrdExp)",
                                          metric="Delta", specificYear=currentYear)
                delta_AccrdExp_Projections.append(delta_AccrdExp)
                print(currentYear, "Change in (AccrdExp) Balance =", delta_AccrdExp)
            cashflow_from_ops[cf_from_OPS_item] = delta_AccrdExp_Projections
        elif (cf_from_OPS_item == "delta_(ONCL)"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                delta_ONCL = pullData(source=projectedBalanceSheets["Liabilities"], itemOfInterest="(ONCL)",
                                      metric="Delta", specificYear=currentYear)
                delta_ONCL_Projections.append(delta_ONCL)
                print(currentYear, "Change in (ONCL) Balance =", delta_ONCL)
            cashflow_from_ops[cf_from_OPS_item] = delta_ONCL_Projections
        elif (cf_from_OPS_item == "PIK_Accrual"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                pik_Accrual = pullData(source=projected["BalanceSheet"]["SupplementalData"],
                                       itemOfInterest="PIK_Accruals",
                                       metric="EoP", specificYear=currentYear)
                delta_PIK_AccrualProjections.append(pik_Accrual)
                print(currentYear, "PIK Accrual =", pik_Accrual)
            cashflow_from_ops[cf_from_OPS_item] = delta_PIK_AccrualProjections
        print("\n")

    '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CF from INVESTING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
    print("*******************************")
    print("*** PROCESSING CF_from_INV ***")
    print("*******************************")
    for cf_from_INV_item in theOrderLineItemsAreToBeForecasted_INV:
        if (cf_from_INV_item == "Capital_Expenditures_(CapEx)"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                capex = -1 * pullData(source=projectedBalanceSheets["SupplementalData"],
                                      itemOfInterest="CapitalExpenditures",
                                      metric="EoP", specificYear=currentYear)
                capexProjections.append(capex)
                print(currentYear, "Capital Expenditures =", capex)
            cashflow_from_inv[cf_from_INV_item] = capexProjections
        elif (cf_from_INV_item == "Intangible_Asset_Purchases"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                intangibleAssetPurchases = -1 * pullData(source=projectedBalanceSheets["SupplementalData"],
                                                         itemOfInterest="IntangibleAssetPurchases",
                                                         metric="EoP", specificYear=currentYear)
                intangibleAssetPurchaseProjections.append(intangibleAssetPurchases)
                print(currentYear, "Intangible Asset PURCHASES =", intangibleAssetPurchases)
            cashflow_from_inv[cf_from_INV_item] = intangibleAssetPurchaseProjections
        print("\n")

    '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CF from FINANCING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
    print("*******************************")
    print("*** PROCESSING CF_from_FIN ***")
    print("*******************************")
    for cf_from_FIN_item in theOrderLineItemsAreToBeForecasted_FIN:
        if (cf_from_FIN_item == "delta_(LTD)"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                borrowing = pullData(source=projectedBalanceSheets["SupplementalData"], itemOfInterest="Borrowing",
                                     metric="EoP", specificYear=currentYear)
                repayment = pullData(source=projectedBalanceSheets["SupplementalData"], itemOfInterest="DebtRepayment",
                                     metric="EoP", specificYear=currentYear)
                delta_LTD = (borrowing - abs(repayment))
                delta_LTD_Projections.append(delta_LTD)
                print(currentYear, "Change in (LTD) Balance =", delta_LTD)
            cashflow_from_fin[cf_from_FIN_item] = delta_LTD_Projections
        elif (cf_from_FIN_item == "Dividends_Paid"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                dividendsPaid = pullData(source=projectedBalanceSheets["SupplementalData"], itemOfInterest="DividendPayout",
                                         metric="EoP", specificYear=currentYear)
                dividendPayoutProjections.append(dividendsPaid)
                print(currentYear, "Common Equity Dividends PAID =", dividendsPaid)
            cashflow_from_fin[cf_from_FIN_item] = dividendPayoutProjections
        elif (cf_from_FIN_item == "Stock_Buybacks"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                buybacks = pullData(source=projectedBalanceSheets["SupplementalData"], itemOfInterest="StockBuybacks",
                                    metric="EoP", specificYear=currentYear)
                stockBuybackProjections.append(buybacks)
                print(currentYear, "Common Equity Repurchases =", buybacks)
            cashflow_from_fin[cf_from_FIN_item] = stockBuybackProjections
        elif (cf_from_FIN_item == "Stock_Issuance"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                stockIssues = pullData(source=projectedBalanceSheets["SupplementalData"], itemOfInterest="StockIssuance",
                                       metric="EoP", specificYear=currentYear)
                stockIssuanceProjections.append(stockIssues)
                print(currentYear, "Common Equity New Issuance =", stockIssues)
            cashflow_from_fin[cf_from_FIN_item] = stockIssuanceProjections
        elif (cf_from_FIN_item == "delta_(OCI)"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                delta_OCI = pullData(source=projectedBalanceSheets["Equity"],
                                     itemOfInterest="Other_Comprehensive_Earnings",
                                     metric="Delta", specificYear=currentYear)
                delta_OCI_Projections.append(delta_OCI)
                print(currentYear, "Change in (OCI) Balance=", delta_OCI)
            cashflow_from_fin[cf_from_FIN_item] = delta_OCI_Projections
        elif (cf_from_FIN_item == "delta_Revolver"):
            for currentYear in range(timeRange[0], (timeRange[1] + 1)):
                delta_Revolver = pullData(source=projectedBalanceSheets["Liabilities"], itemOfInterest="Revolver",
                                          metric="Delta", specificYear=currentYear)
                delta_Revolver_Projections.append(delta_Revolver)
                print(currentYear, "Change in (Revolver) Balance=", delta_Revolver)
            cashflow_from_fin[cf_from_FIN_item] = delta_Revolver_Projections
        print("\n")

    '''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ NET CASHFLOW CALC ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
    print("********************************")
    print("*** PROCESSING SUMMARIZATION ***")
    print("********************************")
    for currentYear in range(timeRange[0], (timeRange[1] + 1)):
        cashflow_from_operations = 0.00
        for key in list(cashflow_from_ops.keys()):
            cashflow_from_operations += cashflow_from_ops[key][currentYear - timeRange[0]]
        cf_from_OPS_Projections.append(cashflow_from_operations)
    net_cashflow["CF_from_OPS"] = cf_from_OPS_Projections
    for currentYear in range(timeRange[0], (timeRange[1] + 1)):
        cashflow_from_investing = 0.00
        for key in list(cashflow_from_inv.keys()):
            cashflow_from_investing += cashflow_from_inv[key][currentYear - timeRange[0]]
        cf_from_INV_Projections.append(cashflow_from_investing)
    net_cashflow["CF_from_INV"] = cf_from_INV_Projections
    for currentYear in range(timeRange[0], (timeRange[1] + 1)):
        cashflow_from_financing = 0.00
        for key in list(cashflow_from_fin.keys()):
            cashflow_from_financing += cashflow_from_fin[key][currentYear - timeRange[0]]
        cf_from_FIN_Projections.append(cashflow_from_financing)
    net_cashflow["CF_from_FIN"] = cf_from_FIN_Projections
    net_cashflow["Total_CF"] = list(doVectorMath([cf_from_OPS_Projections, cf_from_INV_Projections, cf_from_FIN_Projections],
                                                  operation="ADDITION"))

    temp = {"Operations": reformatStatement(input=dictionary_TO_dataframe(dictionary=cashflow_from_ops,
                                                                          startingYear=timeRange[0],
                                                                          endingYear=timeRange[1])),
            "Investing": reformatStatement(input=dictionary_TO_dataframe(dictionary=cashflow_from_inv,
                                                                         startingYear=timeRange[0],
                                                                         endingYear=timeRange[1])),
            "Financing": reformatStatement(input=dictionary_TO_dataframe(dictionary=cashflow_from_fin,
                                                                         startingYear=timeRange[0],
                                                                         endingYear=timeRange[1])),
            "NetCashflow": reformatStatement(input=dictionary_TO_dataframe(dictionary=net_cashflow,
                                                                           startingYear=timeRange[0],
                                                                           endingYear=timeRange[1]))}

    for currentYear in range(timeRange[0], (timeRange[1] + 1)):
        for section in list(temp["NetCashflow"].keys()):
            lineItemDetails = temp["NetCashflow"][section]
            key = handleShortcuts(task="LocateMetric", input="EoP", dataframe=lineItemDetails)
            print(currentYear, section, lineItemDetails.at[key, currentYear])
        print("\n")

    proj = temp
    return proj

historicalWindow = (2012, 2013)

"HISTORICAL INCOME STATEMENT"
data = {"Revenue_(Sales)":                                                   [156508.00,  170910.00],
        "Cost_of_Sales_(COGS)":                                              [-87846.00, -106606.00],
        "Gross_Profit_(GP)":                                                 [68662.00,    64303.00],
        "Research_&_Development_(R_&_D)":                                    [-3381.00,    -4475.00],
        "Selling,_General,_&_Administrative_(SG_&_A)":                       [-10040.00,  -10830.00],
        "Operating_Profit_(EBIT)":                                           [55241.00,    48999.00],
        "Interest_INCOME":                                                   [1088.00,      1616.00],
        "Interest_EXPENSE_(IE)":                                             [-0.00,        -136.00],
        "Other_Expense":                                                     [-566.00,      -324.00],
        "Pre-Tax_Profit_(EBT)":                                              [55763.00,    50155.00],
        "Taxes":                                                             [-14030.00,  -13118.00],
        "Net_Income":                                                        [41733.00,    37037.00]}
incomeStatement_PART_ONE = dictionary_TO_dataframe(dictionary=data, startingYear=historicalWindow[0], endingYear=historicalWindow[1], scale_units_by="*(1e3)")
data = {"Basic_Shares_OUTSTANDING":                                          [935.00,        925.00],
        "Impact_of_Dilutive_Securities":                                     [11.00,           6.00],
        "Diluted_Shares_OUTSTANDING":                                        [945.00,        932.00]}
incomeStatement_PART_TWO = dictionary_TO_dataframe(dictionary=data, startingYear=historicalWindow[0], endingYear=historicalWindow[1], scale_units_by="*(1e0)")
data = {"Basic_EPS":                                                         [44.64,          40.03],
        "Diluted_EPS":                                                       [44.15,          39.75]}
incomeStatement_PART_THREE = dictionary_TO_dataframe(dictionary=data, startingYear=historicalWindow[0], endingYear=historicalWindow[1], scale_units_by="*(1e0)")
incomeStatement = reformatStatement(input=(pd.concat([incomeStatement_PART_ONE, incomeStatement_PART_TWO, incomeStatement_PART_THREE])))

"HISTORICAL BALANCE SHEET"
data = {"Cash_&_Equivalents_(including_ST_&_LT_Securities)_(Cash)":          [121251.00,  146761.00],
        "Accounts_Receivable_(AR)":                                          [10930.00,    13102.00],
        "Inventory":                                                         [791.00,       1764.00],
        "Deferred_Tax_Assets_(DTA)":                                         [2583.00,      3453.00],
        "Other_Current_Assets_(including_Non-Trade_Receivables)_(OCA)":      [14220.00,    14421.00]}
currentAssets = dictionary_TO_dataframe(dictionary=data, startingYear=historicalWindow[0], endingYear=historicalWindow[1], scale_units_by="*(1e3)")
data = {"Property,_Plant,_&_Equipment_(PP_&_E)":                             [15452.00,    16597.00],
        "Acquired_Intangibles_(Goodwill)":                                   [5359.00,      5756.00],
        "Other_Non-Current_Assets_(ONCA)":                                   [5478.00,      5146.00]}
nonCurrentAssets = dictionary_TO_dataframe(dictionary=data, startingYear=historicalWindow[0], endingYear=historicalWindow[1], scale_units_by="*(1e3)")
total_assets = pd.concat([currentAssets, nonCurrentAssets])
data = {"Accounts_Payable_(AP)":                                             [21175.00,    22367.00]}
currentLiabilities = dictionary_TO_dataframe(dictionary=data, startingYear=historicalWindow[0], endingYear=historicalWindow[1], scale_units_by="*(1e3)")
data = {"Accrued_Expenses_&_Deferred_Revenues_(AccrdExp)":                   [20015.00,    23916.00],
        "Revolver":                                                          [0.00,            0.00],
        "Long_Term_Debt_(LTD)":                                              [0.00,        16960.00],
        "Other_Non-Current_Liabilities_(ONCL)":                              [16664.00,    20208.00]}
nonCurrentLiabilities = dictionary_TO_dataframe(dictionary=data, startingYear=historicalWindow[0], endingYear=historicalWindow[1], scale_units_by="*(1e3)")
total_liabilities = pd.concat([currentLiabilities, nonCurrentLiabilities])
data = {"Common_Stock_/_Additional_Paid-In_Capital_(APIC)_(CommonEquity)":   [16422.00,    19764.00],
        "Treasury_Stock_(TS)":                                               [0.00,            0.00],
        "Retained_Earnings_/_Accumulated_Deficit_(RE)":                      [101289.00,  104256.00],
        "Other_Comprehensive_Earnings":                                      [499.00,       -471.00]}
total_equity = dictionary_TO_dataframe(dictionary=data, startingYear=historicalWindow[0], endingYear=historicalWindow[1], scale_units_by="*(1e3)")
balanceSheet = reformatStatement(input=pd.concat([total_assets, total_liabilities, total_equity]))

# for yearInQuestion in historicalWindow:
#     verifyBalance(dictionaryForDataframe={"Assets": reformatStatement(input=total_assets),
#                                           "Liabilities": reformatStatement(input=total_liabilities),
#                                           "Equity": reformatStatement(input=total_equity)}, year=yearInQuestion)

"HISTORICAL CASHFLOW STATEMENT"
data = {"D_&_A":                                                             [3277.00,      6757.00],
        "Amortization":                                                      [605.00,        960.00],
        "Depreciation":                                                      [2672.00,      5797.00],
        "StockBasedCompensation":                                            [1740.00,      2253.00],
        "CapEx":                                                             [-8295.00,    -8165.00],
        "Intangible_Asset_Purchases":                                        [-1107.00,     -911.00],
        "CommonStockIssuance":                                               [665.00,        530.00],
        "StockBuyback":                                                      [0.00,       -22860.00],
        "DividendsPaid":                                                     [-2488.00,   -10564.00]}
cashflowStatement = reformatStatement(input=dictionary_TO_dataframe(dictionary=data, startingYear=2012, endingYear=2013,
                                                                    scale_units_by="*(1e6)"))

historical = {"IncomeStatement": incomeStatement, "BalanceSheet": balanceSheet, "CashflowStatement": cashflowStatement}

projectionWindow = (2014, 2018)

projected = {}

projected["IncomeStatement"] = forecastIncomeStatement(historicalSources=historical,
                                                       timeRange=projectionWindow, stage="1")
projected["BalanceSheet"] = forecastBalanceSheet(historicalSources=historical, projectedSources=projected,
                                                 timeRange=projectionWindow, stage="1")
projected["CashflowStatement"] = forecastCashflowStatement(historicalSources=historical, projectedSources=projected,
                                                           timeRange=projectionWindow)
projected = forecastBalanceSheet(historicalSources=historical, projectedSources=projected,
                                 timeRange=projectionWindow, stage="2", operationsSequence=["(Cash)"])

print("PROJECTED Cash:\n", pullData(source=projected["BalanceSheet"]["Assets"], itemOfInterest="(Cash)",
                                    metric="EoP", timeRange=projectionWindow))




# print("***[", year, item, "]***\n", projected["BalanceSheet"]["Equity"][item][year])

# year = 2014
# span = (2014, 2018)
# apple = ["CommonEquity", "Treasury_Stock_(TS)", "Retained_Earnings"]
# for item in apple:
#     requested = pullData(source=projected["BalanceSheet"]["Equity"], itemOfInterest=item,
#                          metric="EoP", timeRange=span)
#     print(year, item, ":", requested)



# for section in ["Assets", "Liabilities", "Equity"]:
#     for lineItem in list(projected["BalanceSheet"][section].keys()):
#         print(projected["BalanceSheet"][section][lineItem][2014])


# year = 2014
# item = "Cash_&_Equivalents_(including_ST_&_LT_Securities)_(Cash)"
# print("***[", year, item, "]***\n", projected["BalanceSheet"]["Assets"][item][year])

#
# "delta_Revolver"
# "InterestExpenseForLTD"
# "InterestExpenseForRevolver"
# "InterestIncomeFromCashHoldings"
#
# year = 2014
# item = "InterestExpenseForLTD"
#
# print("***[", year, item, "]***\n", projected["BalanceSheet"]["SupplementalData"][item][year])




# projected = {title : x for x, title in zip(, ["IncomeStatement", "BalanceSheet", "CashflowStatement"])}

# margin = pullData(source=analyzeWorkingCapital(source=historical), itemOfInterest="AccrdExp_as_%_of_Sales",
#                   metric="Average", specificYear=2013)

# print(projected["BalanceSheet"]["SupplementalData"]["PIK_Accruals"])

#
# # dividends = pullData(source=projected["BalanceSheet"]["SupplementalData"], itemOfInterest="DividendPayout",
# #                      metric="DELTA", timeRange=(2014, 2018))
# #
# # print("Projected Dividends:\n", dividends)
# #
# # print(projected["BalanceSheet"]["PrimaryData"])