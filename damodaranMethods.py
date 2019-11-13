
import numpy as np

def calculateTerminalValue(lastYearOfData, expected_GrowthRate_for_PERPETUITY, expected_WACC_for_PERPETUITY):

    terminalValue = (lastYearOfData * (1 + expected_GrowthRate_for_PERPETUITY)) / \
                    (expected_WACC_for_PERPETUITY - expected_GrowthRate_for_PERPETUITY)
    return terminalValue

def do_3_Stage_FCFE(initialStage=None, stableStage=None, costOfEquityAssumptions=None):
    '''From Damodaran Valuation (Ch 14) pg. 368-370'''
    # initialStage = {"Revenue_PREVIOUS": 1598.00,
    #                 "Revenue_MOSTRECENT": 2253,
    #                 "NetIncome_MOSTRECENT": 72.36e6,
    #                 "BookValueOfEquity_MOSTRECENT": 2588.00e6,
    #                 "NonCashWorkingCapital_MOSTRECENT": 180.0e6,
    #                 "CapEx_MOSTRECENT": 335.0e6,
    #                 "Depreciation_MOSTRECENT": 204.0e6,
    #                 "BVofDebt-to-Capital_MOSTRECENT": 0.4094}

    def analyzeStage(startIndex, endIndex, numericScale, transitionalStage=None):

        durationOfTransition, degree, linearDecrementOfGrowth, linearDecrementOfCostOfEquity, scale = 0, 0, 0, 0, 1
        if(numericScale is "BILLIONS"):
            scale = 1e9
        elif(numericScale is "MILLIONS"):
            scale = 1e6
        elif (numericScale is "THOUSANDS"):
            scale = 1e3
        for x in range(startIndex, endIndex):
            if(transitionalStage is None):
                degree = 0
            elif(transitionalStage is True):
                degree += 1
                durationOfTransition = (endIndex - startIndex)
                linearDecrementOfGrowth = ((expected_GrowthRate_for_INITIAL_STAGE - expected_GrowthRate_for_PERPETUITY) / durationOfTransition)
                linearDecrementOfCostOfEquity = ((current_CostOfEquity - expected_CostOfEquity_for_PERPETUITY) / durationOfTransition)

            modifiedGrowthRate = (expected_GrowthRate_for_INITIAL_STAGE - linearDecrementOfGrowth * degree)
            projected_NetIncome = round(projections["NetIncome"][x - 1] * (1 + modifiedGrowthRate), 2)
            projections["ExpectedGrowthRate"].append(modifiedGrowthRate)
            projections["NetIncome"].append(projected_NetIncome)

            projected_FCFE = round(projected_NetIncome * (1 - currentEquityReinvestmentRate), 2)
            projections["EquityReinvestmentRate"].append(currentEquityReinvestmentRate)
            projections["FCFE"].append(projected_FCFE)

            modifiedCostOfEquity = (current_CostOfEquity - linearDecrementOfCostOfEquity * degree)
            projected_PV_of_FCFE = round((projected_FCFE / ((1 + modifiedCostOfEquity) ** x)), 2)
            projections["PV_of_FCFE"].append(projected_PV_of_FCFE)
            projections["CostOfEquity"].append(modifiedCostOfEquity)

            print("PROJECTED Growth for Year(", x, "):", round(100 * modifiedGrowthRate, 2), "%")
            print("PROJECTED NetIncome for Year(", x, "):", round(projected_NetIncome / scale, 2))
            print("PROJECTED EquityReinvestment for Year(", x, "):", round(currentEquityReinvestmentRate * 100, 2), "%")
            print("PROJECTED FCFE for Year(", x, "):", round(projected_FCFE / scale, 2))
            print("PROJECTED CoE for Year(", x, "):", round(100 * modifiedCostOfEquity, 2), "%")
            print("PROJECTED PV_of_FCFE for Year(", x, "):", round(projected_PV_of_FCFE / scale, 2))
            print('\n')

        return projections

    changeInRevenue_YoY = (initialStage["Revenue_MOSTRECENT"]-initialStage["Revenue_PREVIOUS"])
    delta_NonCashNWC_NORMALIZED = changeInRevenue_YoY * \
                                  (initialStage["NonCashWorkingCapital_MOSTRECENT"]/initialStage["Revenue_MOSTRECENT"])
    totalReinvestment_NORMALIZED = (initialStage["CapEx_MOSTRECENT"]-initialStage["Depreciation_MOSTRECENT"]+delta_NonCashNWC_NORMALIZED)
    equityReinvestment_NORMALIZED = (totalReinvestment_NORMALIZED * (1-initialStage["BVofDebt-to-Capital_MOSTRECENT"]))
    currentEquityReinvestmentRate = (equityReinvestment_NORMALIZED / initialStage["NetIncome_MOSTRECENT"])
    current_ROE = (initialStage["NetIncome_MOSTRECENT"] / initialStage["BookValueOfEquity_MOSTRECENT"])
    current_CostOfEquity = (costOfEquityAssumptions[0]["RiskFreeRate"] + costOfEquityAssumptions[0]["Beta"] * \
                            costOfEquityAssumptions[0]["EquityMarketPremium"])


    initialStageLength = initialStage["DURATION"]
    expected_ROE_for_INITIAL_STAGE = initialStage["ExpectedReturnOnEquity"]
    temp = (((expected_ROE_for_INITIAL_STAGE - current_ROE) / current_ROE)**(1/initialStageLength))-1
    expected_GrowthRate_for_INITIAL_STAGE = (currentEquityReinvestmentRate * expected_ROE_for_INITIAL_STAGE + temp)

    expected_GrowthRate_for_PERPETUITY = stableStage["ExpectedGrowthRate"]
    expected_ROE_for_PERPETUITY = stableStage["ExpectedReturnOnEquity"]
    expected_EquityReinvestmentRate_for_PERPETUITY = (expected_GrowthRate_for_PERPETUITY / expected_ROE_for_PERPETUITY)
    expected_CostOfEquity_for_PERPETUITY = (costOfEquityAssumptions[1]["RiskFreeRate"] + costOfEquityAssumptions[1]["Beta"] * \
                                            costOfEquityAssumptions[1]["EquityMarketPremium"])

    projections = {"ExpectedGrowthRate": [], "NetIncome": [initialStage["NetIncome_MOSTRECENT"]],
                   "EquityReinvestmentRate": [], "FCFE": [], "PV_of_FCFE": [],  "CostOfEquity": []}

    intialStageResults = analyzeStage(1, initialStageLength+1, "MILLIONS")
    transitionalStageResults = analyzeStage(initialStageLength+1, 2*initialStageLength+1, "MILLIONS", transitionalStage=True)

    mostRecenctlyProjectedNetIncome = transitionalStageResults["NetIncome"][-1]
    termVal = calculateTerminalValue(mostRecenctlyProjectedNetIncome * (1 - expected_EquityReinvestmentRate_for_PERPETUITY),
                                     expected_GrowthRate_for_PERPETUITY, expected_CostOfEquity_for_PERPETUITY)
    print("TerminalValue = ", round(termVal/1e6, 2), "million")
    pv_of_TerminalValue = (termVal * np.prod(np.array([((1 + x) ** -1) for x in projections["CostOfEquity"]])))
    pv_of_TerminalValue = round(pv_of_TerminalValue, 2)
    print("PV_of_TerminalValue = ", round(pv_of_TerminalValue/1e6, 2), "million")

    #'''Estimating Growth in FCFE pg 358 Ch14 Damodaran'''
    # earningsRetentionRatio = 10
    # expected_GrowthRate_for_DIVIDENDS_PER_SHARE = (earningsRetentionRatio * current_ROE)
    # expected_GrowthRate_for_DIVIDENDS_PER_SHARE = (currentEquityReinvestmentRate * current_ROE)
    #
    # cash_AND_marketableSec = 10
    # afterTaxIncomeFromCash_AND_MarketableSec = 10
    # noncashROE = (projected_NetIncome - afterTaxIncomeFromCash_AND_MarketableSec) / \
    #              (initialStage["BookValueOfEquity_MOSTRECENT"] - cash_AND_marketableSec)
    #
    # expected_GrowthRate_for_FCFE = (currentEquityReinvestmentRate * noncashROE)

    return 10

def perform_3_Stage_FCFE(initialStage, transitionStage, stableStage):
    '''From Damodaran Valuation (Ch 14) pg. 374'''
    netIncome = 10
    interestIncome_AFTER_TAX = 10
    netIncome_from_NON_CASH_ASSETS = (netIncome - interestIncome_AFTER_TAX)

    balanceSheet_CashBalance = 10
    bookValueOfEquity = 15

    returnOnEquity_NON_CASH = (netIncome_from_NON_CASH_ASSETS / (bookValueOfEquity - balanceSheet_CashBalance))


    capex = 10
    depreciation = 10
    delta_NWC = 10
    netDebtIssued = 10
    equityReinvestmentRate = ((capex - depreciation + delta_NWC - netDebtIssued) / netIncome_from_NON_CASH_ASSETS)

    return 10

def estimateExpectedCurrent_PE_Ratio(initialStage, stableStage):
    '''From Damodaran Valuation (Ch 18) pg. 472'''
    #The Expected Current PE Ratio is derived from a TWO-STAGE FRAMEWORK:

    #The Expected Growth Rate in EPS is derived from the ROE formula
    initialStage = {"GrowthRate": 10,
                    "CostOfEquity": 10,
                    "PayoutRatio": 10,
                    "Duration": 2}

    stableStage = {"GrowthRate": 10,
                   "CostOfEquity": 10,
                   "PayoutRatio": 10}

    ip_1 = (initialStage["PayoutRatio"] * (1 + initialStage["GrowthRate"]))
    ip_2 = (1 - ((1 + initialStage["GrowthRate"]) ** initialStage["Duration"]) / (
                (1 + initialStage["CostOfEquity"]) ** initialStage["Duration"]))
    ip_3 = (initialStage["CostOfEquity"] - initialStage["GrowthRate"])
    initial_stage_component = ((ip_1 * ip_2) / ip_3)

    sp_1 = stableStage["PayoutRatio"] * ((1 + initialStage["GrowthRate"]) ** initialStage["Duration"]) * (
                1 + stableStage["GrowthRate"])
    sp_2 = (stableStage["CostOfEquity"] - stableStage["GrowthRate"]) * (
                (1 + initialStage["CostOfEquity"]) ** initialStage["Duration"])
    stable_stage_component = (sp_1 / sp_2)

    expected_CURRENT_PE_Ratio = (initial_stage_component + stable_stage_component)
    return expected_CURRENT_PE_Ratio

def estimateExpectedCurrent_Price_TO_Sales(initialStage, stableStage, netMargin):
    '''From Damodaran Valuation (Ch 20) pg. 544-547'''
    #The Expected Current Price-to-Sales Ratio is derived from a TWO-STAGE FRAMEWORK (almost identical to P/E):

    "This 'NetProfitMargin' can be inputted as either the CURRENT measure or the FUTURE TARGET/IDEAL"
    netProfitMargin = netMargin
    price_TO_earnings_ratio = estimateExpectedCurrent_PE_Ratio(initialStage, stableStage)
    price_TO_sales_ratio = (netProfitMargin * price_TO_earnings_ratio)

    "EXPECTED GROWTH IN EQUITY from page 550"
    currentRetentionRatio = 10
    revenue = 10
    bookValueOfEquity = 10

    equityTurnoverRatio = (revenue / bookValueOfEquity)
    expectedGrowthRateInEQUITY = (currentRetentionRatio * netProfitMargin * equityTurnoverRatio) # a.k.a. Implied ROE

    "EXPECTED GROWTH IN FIRM from page 550"
    reinvestmentRate = 10

    afterTaxOperatingMargin = 10 # a.k.a. (EBIT(1-t) / Sales)

    investedCapital = 10

    capitalTurnoverRatio = (revenue / investedCapital)

    expectedGrowthRateInFIRM = (reinvestmentRate * afterTaxOperatingMargin * capitalTurnoverRatio) # a.k.a. Implied ROC



    return price_TO_sales_ratio


def estimate_FORWARD_LOOKING_2_STAGE_Ratio(payoutRatios, costOfCapitals, earningsGrowthRates, initialStageDuration):

    '''Calculation'''

    # 1st Term of Equation
    step1 = (1 + earningsGrowthRates[0]) ** initialStageDuration
    step2 = (1 + costOfCapitals[0]) ** initialStageDuration
    step3 = (payoutRatios[0]) * (1 + earningsGrowthRates[0]) * (1 - (step1 / step2))
    step4 = step3 / (costOfCapitals[0] - earningsGrowthRates[0])
    print("---------------------\n1st Term of Equation:\n---------------------")
    step1Work = "((1 + " + str(round(100*earningsGrowthRates[0], 2)) + "%)^"+ str(initialStageDuration)+")"
    step2Work = "((1 + " + str(round(100*costOfCapitals[0], 2)) + "%)^"+ str(initialStageDuration)+")"
    step3Work = "("+str(round(100*payoutRatios[0], 2)) + "%) * (1 + " + str(round(100*earningsGrowthRates[0], 2)) + "%)"
    print("{", step3Work, "* [ 1 -", step1Work, "/", step2Work, "] } / {", str(round(100*costOfCapitals[0], 2)), "% -",
          str(round(100*earningsGrowthRates[0], 2)) + "%} =", str(round(step4, 3)))


    # 2nd Term of Equation
    step5 = step1
    step6 = (payoutRatios[1]) * (1 + earningsGrowthRates[1])
    step7 = (costOfCapitals[1] - earningsGrowthRates[1]) * step2 # this line handles the DENOMINATOR of the 2nd term
    step8 = (step5 * step6) / (step7)
    ratio = round((step4 + step8), 3)
    print("---------------------\n2nd Term of Equation:\n---------------------")
    step5Work = "((1 + " + str(round(100*earningsGrowthRates[0], 2)) + "%)^"+ str(initialStageDuration)+")"
    step6Work = "("+str(round(100*payoutRatios[1], 2)) + "%) * (1 + " + str(round(100*earningsGrowthRates[1], 2)) + "%)"
    print("{ [", step6Work, "*", step5Work, "] / [ (", str(round(100*costOfCapitals[1], 2)), "% -",
          str(round(100*earningsGrowthRates[1], 2)), "%) *", step2Work, "] } =", str(round(step8, 3)))

    return ratio

#This ratio is the most accurate PRICE TO SALE
def estimate_FORWARD_LOOKING_Price_TO_Sales(initialStageDuration, costOfEquityAssumptions=None):
    '''Based on Damodaran Ch20 pg. 547 - all figures in MILLIONS'''

    # This Price-to-Sales Ratio is built using a TWO-STAGE FRAMEWORK that draws upon BOTH CURRENT METRICS & PROJECTIONS

    '''Actually Observed Metrics'''
    mostRecentPeriod_EndOfPeriod_NET_INCOME = 246.0
    mostRecentPeriod_EndOfPeriod_REVENUE = 9006.0
    current_NetProfitMargin = (mostRecentPeriod_EndOfPeriod_NET_INCOME / mostRecentPeriod_EndOfPeriod_REVENUE)

    periodPRIORToMostRecent_EndOfPeriod_bookValueOfEquity = 1628.0
    current_ROE = (mostRecentPeriod_EndOfPeriod_NET_INCOME / periodPRIORToMostRecent_EndOfPeriod_bookValueOfEquity)

    '''Assumptions & Expectations'''
    durationOfInitialStage = 10 #years

    # Payout Ratio - INITIAL STAGE ASSUMPTIONS
    intialStage_ExpectedGrowthRateFor_NET_INCOME = 0.10
    initialStage_PAYOUT_RATIO = (1 - (intialStage_ExpectedGrowthRateFor_NET_INCOME / current_ROE))

    # Cost of Equity - INITIAL STAGE ASSUMPTIONS
    initialStage_RiskFreeRate = 0.035
    initialStage_EquityRiskPremium = 0.05
    initialStage_FirmBeta = 1.00
    initialStage_CostOfEquity = (initialStage_RiskFreeRate + initialStage_FirmBeta * initialStage_EquityRiskPremium)

    # Return on Equity & Payout Ratio - STABLE STAGE / PERPETUAL ASSUMPTIONS
    stableStage_ExpectedGrowthRateFor_NET_INCOME = 0.03
    stableStage_Expected_ROE = 0.10
    stableStage_PAYOUT_RATIO = (1 - (stableStage_ExpectedGrowthRateFor_NET_INCOME / stableStage_Expected_ROE))

    # Cost of Equity - STABLE STAGE / PERPETUAL ASSUMPTIONS
    stableStage_RiskFreeRate = initialStage_RiskFreeRate
    stableStage_EquityRiskPremium = initialStage_EquityRiskPremium
    stableStage_FirmBeta = 0.90
    stableStage_CostOfEquity = (stableStage_RiskFreeRate + stableStage_FirmBeta * stableStage_EquityRiskPremium)


    # Resulting Figure
    growthRates = (intialStage_ExpectedGrowthRateFor_NET_INCOME, stableStage_ExpectedGrowthRateFor_NET_INCOME)
    temp = estimate_FORWARD_LOOKING_2_STAGE_Ratio((initialStage_PAYOUT_RATIO, stableStage_PAYOUT_RATIO),
                                                  (initialStage_CostOfEquity, stableStage_CostOfEquity),
                                                  growthRates, durationOfInitialStage)
    price_TO_sales = round((current_NetProfitMargin * temp), 3)

    # '''Calculation'''
    # # 1st Term of Equation
    # step1 = (1 + intialStage_ExpectedGrowthRateFor_NET_INCOME) ** durationOfInitialStage
    # step2 = (1 + initialStage_CostOfEquity) ** durationOfInitialStage
    # step3 = (initialStage_PAYOUT_RATIO) * (1 + intialStage_ExpectedGrowthRateFor_NET_INCOME) * (1 - (step1 / step2))
    # step4 = step3 / (initialStage_CostOfEquity - intialStage_ExpectedGrowthRateFor_NET_INCOME)
    #
    # # 2nd Term of Equation
    # step5 = step1
    # step6 = (stableStage_PAYOUT_RATIO) * (1 + stableStage_ExpectedGrowthRateFor_NET_INCOME)
    # step7 = (stableStage_CostOfEquity - stableStage_ExpectedGrowthRateFor_NET_INCOME) * (step2)
    # step8 = (step5 * step6) / (step7)
    #
    # # Resulting Figure
    # price_TO_sales = current_NetProfitMargin * (step4 + step8)
    # price_TO_sales = round(price_TO_sales, 3)

    return price_TO_sales

def estimate_FORWARD_LOOKING_EV_TO_Sales(initialStageDuration, costOfEquityAssumptions=None):
    '''Based on Damodaran Ch20 pg. 548-549 - all figures in MILLIONS'''

    # This EV-to-Sales Ratio is built using a TWO-STAGE FRAMEWORK that draws upon BOTH CURRENT METRICS & PROJECTIONS

    '''Actually Observed Metrics'''
    periodPRIORToMostRecent_EndOfPeriod_bookValueOfEquity = 24799.00
    periodPRIORToMostRecent_EndOfPeriod_bookValueOfDebt = 11859.00
    periodPRIORToMostRecent_EndOfPeriod_bookValueOfCash = 4979.00
    periodPRIORToMostRecent_EndOfPeriod_InvestedCapital = (periodPRIORToMostRecent_EndOfPeriod_bookValueOfEquity + \
                                                           periodPRIORToMostRecent_EndOfPeriod_bookValueOfDebt - \
                                                           periodPRIORToMostRecent_EndOfPeriod_bookValueOfCash)

    mostRecentPeriod_EndOfPeriod_REVENUE = 35119.0
    mostRecentPeriod_EndOfPeriod_EBIT = 8449.0
    mostRecentPeriod_EndOfPeriod_TaxRate = 0.40
    mostRecentPeriod_EndOfPeriod_EBIAT = mostRecentPeriod_EndOfPeriod_EBIT * (1 - mostRecentPeriod_EndOfPeriod_TaxRate)
    mostRecentPeriod_EndOfPeriod_ATOM = (mostRecentPeriod_EndOfPeriod_EBIAT / mostRecentPeriod_EndOfPeriod_REVENUE)
    mostRecentPeriod_EndOfPeriod_Sales_TO_Capital = (periodPRIORToMostRecent_EndOfPeriod_InvestedCapital /
                                                     mostRecentPeriod_EndOfPeriod_REVENUE)
    print("Most Recent Figure for Sales-to-Capital:", round(mostRecentPeriod_EndOfPeriod_Sales_TO_Capital, 2), "=",
          mostRecentPeriod_EndOfPeriod_REVENUE, "/", periodPRIORToMostRecent_EndOfPeriod_InvestedCapital)


    mostRecentPeriod_EndOfPeriod_ROIC = (mostRecentPeriod_EndOfPeriod_ATOM * mostRecentPeriod_EndOfPeriod_Sales_TO_Capital)
    print("Most Recent Figure for ATOM:", round(100 * mostRecentPeriod_EndOfPeriod_ATOM, 2), "%")
    print("Most Recent Figure for ROIC:", round(100 * mostRecentPeriod_EndOfPeriod_ROIC, 2), "%")


    currentExisting_DebtToCapital = 0.0723

    '''Assumptions & Expectations'''

    # Earnings Growth, ATOM, ROIC - INITIAL STAGE ASSUMPTIONS
    intialStage_ExpectedGrowthRateFor_EBIT = 0.096
    intialStage_ROIC = mostRecentPeriod_EndOfPeriod_ROIC
    intialStage_ATOM = mostRecentPeriod_EndOfPeriod_ATOM
    intialStage_ReinvestmentOfATOMrate = 0.60
    intialStage_Sales_TO_Capital = mostRecentPeriod_EndOfPeriod_Sales_TO_Capital

    # Cost of Capital - INITIAL STAGE ASSUMPTIONS
    initialStage_CostOfEquity = (costOfEquityAssumptions[0]["RiskFreeRate"] + costOfEquityAssumptions[0]["Beta"] * \
                                 costOfEquityAssumptions[0]["EquityMarketPremium"])
    initialStage_PreTaxCostOfDebt = 0.045
    initialStage_TaxRate = mostRecentPeriod_EndOfPeriod_TaxRate
    initialStage_DebtToCapital = currentExisting_DebtToCapital
    initialStage_CostOfCapital = initialStage_CostOfEquity * (1 - initialStage_DebtToCapital) + \
                                 initialStage_PreTaxCostOfDebt * (1 - initialStage_TaxRate) * initialStage_DebtToCapital
    print("WACC for INITIAL Stage:", round(100 * initialStage_CostOfCapital, 2), "%")


    # Earnings Growth, ATOM, ROIC - STABLE STAGE / PERPETUAL ASSUMPTIONS
    stableStage_ExpectedGrowthRateFor_EBIT = 0.035
    stableStage_ROIC = 0.12
    stableStage_ATOM = 0.12
    stableStage_ReinvestmentOfATOMrate = (stableStage_ExpectedGrowthRateFor_EBIT / stableStage_ROIC)
    stableStage_Sales_TO_Capital = 1.00

    # Cost of Capital - STABLE STAGE / PERPETUAL ASSUMPTIONS
    stableStage_CostOfEquity = (costOfEquityAssumptions[1]["RiskFreeRate"] + costOfEquityAssumptions[1]["Beta"] * \
                                costOfEquityAssumptions[1]["EquityMarketPremium"])
    stableStage_PreTaxCostOfDebt = initialStage_PreTaxCostOfDebt
    stableStage_TaxRate = initialStage_TaxRate
    stableStage_DebtToCapital = 0.20
    stableStage_CostOfCapital = stableStage_CostOfEquity * (1 - stableStage_DebtToCapital) + \
                                stableStage_PreTaxCostOfDebt * (1 - stableStage_TaxRate) * stableStage_DebtToCapital
    print("WACC for STABLE Stage:", round(100 * stableStage_CostOfCapital, 2), "%")


    # Resulting Figure
    growthRates = (intialStage_ExpectedGrowthRateFor_EBIT, stableStage_ExpectedGrowthRateFor_EBIT)
    temp = estimate_FORWARD_LOOKING_2_STAGE_Ratio(((1 - intialStage_ReinvestmentOfATOMrate), (1 - stableStage_ReinvestmentOfATOMrate)),
                                                  (initialStage_CostOfCapital, stableStage_CostOfCapital),
                                                  growthRates, initialStageDuration)
    ev_TO_sales = round((intialStage_ATOM * temp), 3)

    # '''Calculation'''
    # # 1st Term of Equation
    # step1 = (1 + intialStage_ExpectedGrowthRateFor_EBIT) ** durationOfInitialStage #VERIFIED
    # step2 = (1 + initialStage_CostOfCapital) ** durationOfInitialStage #VERIFIED
    # step3 = (1 - intialStage_ReinvestmentOfATOMrate) * (1 + intialStage_ExpectedGrowthRateFor_EBIT) * (1 - (step1 / step2)) #VERIFIED
    # step4 = step3 / (initialStage_CostOfCapital - intialStage_ExpectedGrowthRateFor_EBIT) #VERIFIED
    #
    # # 2nd Term of Equation
    # step5 = step1 #VERIFIED
    # step6 = (1 - stableStage_ReinvestmentOfATOMrate) * (1 + stableStage_ExpectedGrowthRateFor_EBIT) #VERIFIED
    # step7 = (stableStage_CostOfCapital - stableStage_ExpectedGrowthRateFor_EBIT) * (step2) #VERIFIED
    # step8 = (step5 * step6) / (step7) #VERIFIED
    #
    # ev_TO_sales = intialStage_ATOM * (step4 + step8)
    # ev_TO_sales = round(ev_TO_sales, 3)

    return ev_TO_sales

def estimate_FORWARD_LOOKING_EV_TO_EBITDA(initialStageDuration, costOfEquityAssumptions=None):
    '''Based on Damodaran Ch18 pg. 500-506 - all figures in MILLIONS'''

    return 10

def estimate_FORWARD_LOOKING_Price_TO_Earnings(initialStageDuration, costOfEquityAssumptions=None):
    '''Based on Damodaran Ch18 pg. 473 - all figures in MILLIONS'''

    initialStage_CostOfEquity = (costOfEquityAssumptions[0]["RiskFreeRate"] + costOfEquityAssumptions[0]["Beta"] * \
                                 costOfEquityAssumptions[0]["EquityMarketPremium"])
    stableStage_CostOfEquity = (costOfEquityAssumptions[1]["RiskFreeRate"] + costOfEquityAssumptions[1]["Beta"] * \
                                costOfEquityAssumptions[1]["EquityMarketPremium"])


    # Return on Equity & Payout Ratio - INITIAL STAGE ASSUMPTIONS
    current_ROE = 10
    intialStage_ExpectedGrowthRateFor_EPS = 0.10
    initialStage_PAYOUT_RATIO = (1 - (intialStage_ExpectedGrowthRateFor_EPS / current_ROE))

    # Return on Equity & Payout Ratio - STABLE STAGE / PERPETUAL ASSUMPTIONS
    stableStage_Expected_ROE = 0.10
    stableStage_ExpectedGrowthRateFor_EPS = 0.03
    stableStage_PAYOUT_RATIO = (1 - (stableStage_ExpectedGrowthRateFor_EPS / stableStage_Expected_ROE))

    growthRates = (intialStage_ExpectedGrowthRateFor_EPS, stableStage_ExpectedGrowthRateFor_EPS)
    temp = estimate_FORWARD_LOOKING_2_STAGE_Ratio((initialStage_PAYOUT_RATIO, stableStage_PAYOUT_RATIO),
                                                               (initialStage_CostOfEquity, stableStage_CostOfEquity),
                                                               growthRates,
                                                               initialStageDuration)

    price_TO_earnings = round(temp, 3)
    return price_TO_earnings


parametersForCOE = ({"Beta": 0.90, "RiskFreeRate": 0.035, "EquityMarketPremium": 0.05},
                    {"Beta": 0.90, "RiskFreeRate": 0.035, "EquityMarketPremium": 0.05})

#estimate_FORWARD_LOOKING_Price_TO_Earnings(costOfEquityAssumptions=parametersForCOE)

#estimate_FORWARD_LOOKING_Price_TO_Sales(costOfEquityAssumptions=parametersForCOE)

# apple = estimate_FORWARD_LOOKING_EV_TO_Sales(10, costOfEquityAssumptions=({"Beta": 0.90, "RiskFreeRate": 0.035, "EquityMarketPremium": 0.055},
#                                                                           {"Beta": 1.00, "RiskFreeRate": 0.035, "EquityMarketPremium": 0.055}))


def do_2_Stage_FCFF(initialStageDuration, costOfEquityAssumptions=None, exchangeRateAssumptions=None):
    '''
    This section is based on Damodaran Ch. 15 pg 387-389
    FCFF = [EBIAT - Reinvestment]
    FCFF = [EBIAT - NetCapEx + ChangeInNonCashNWC + ChangeInPVofLeases]
    FCFF = [EBIAT - (CapEx - Depreciation) + ChangeInNonCashNWC + ChangeInPVofLeases]
    '''

    def accountForOperatingLeases(reportedOperatingIncome, reportedDebt, leaseCommitments, prexTaxCostOfDebt):

        numYearsToAnnualizeLumpSum = (leaseCommitments[-1][0][1] - leaseCommitments[-1][0][0] + 1)
        annualizationOfLumpSum = (leaseCommitments[-1][1] / numYearsToAnnualizeLumpSum)

        presentValueOfCommitments = []
        for x in range(0, len(leaseCommitments)):
            pv = leaseCommitments[x][0] / (1 + prexTaxCostOfDebt) ** leaseCommitments[x][1]
            presentValueOfCommitments.append(pv)

            if (x is len(leaseCommitments) - 1):
                # Present Value of Annuity
                pvOfAnnuity_INCOMPLETE = (1 - (1 + prexTaxCostOfDebt) ** (
                            -1 * numYearsToAnnualizeLumpSum)) / prexTaxCostOfDebt
                pvOfAnnuity_COMPLETED = pvOfAnnuity_INCOMPLETE / (1 + prexTaxCostOfDebt) ** (leaseCommitments[-1][0][0])
                presentValueOfCommitments.append(pvOfAnnuity_COMPLETED)

        debtValueOfLeases = sum(presentValueOfCommitments)
        currentYearsDepreciationOnLeasedAsset = (debtValueOfLeases / leaseCommitments[-1][0][1])
        mostRecentPeriod_EoP_AdjustedOperatingIncome = (reportedOperatingIncome - currentYearsDepreciationOnLeasedAsset)
        mostRecentPeriod_EoP_AdjustedDebt = (reportedDebt + debtValueOfLeases)

        return (mostRecentPeriod_EoP_AdjustedOperatingIncome, mostRecentPeriod_EoP_AdjustedDebt)

    '''Actually Observed Metrics'''
    futureLeaseCommitments = [(1, 190.00), (2, 189.00), (3, 187.00), (4, 147.00), (5, 141.00), ((6, 23), 3100.00)]
    mostRecentPeriod_EoP_EBIT = 5252.00
    mostRecentPeriod_EoP_ReportedDebt = 15726.00
    mostRecentPeriod_EoP_ReportedCashBalance = 1712.00
    mostRecentPeriod_EoP_SharesOutstanding = 689.13 #million
    prexTaxCoD = 0.045

    mostRecentPeriod_EoP_AdjustedEBIT, mostRecentPeriod_EoP_AdjustedDebt = accountForOperatingLeases(mostRecentPeriod_EoP_EBIT,
                                                                                                     mostRecentPeriod_EoP_ReportedDebt,
                                                                                                     futureLeaseCommitments, prexTaxCoD)

    taxRate = 0.38
    mostRecentPeriod_EoP_AdjustedEBIAT = (mostRecentPeriod_EoP_AdjustedEBIT * (1 - taxRate))
    periodPRIORToMostRecent_EndOfPeriod_bookValueOfCash = 2200.00
    periodPRIORToMostRecent_EndOfPeriod_bookValueOfDebt = 16814.00
    periodPRIORToMostRecent_EndOfPeriod_presentValLeases = 2353.00
    periodPRIORToMostRecent_EndOfPeriod_bookValueOfEquity = 15347.00
    denominator = (periodPRIORToMostRecent_EndOfPeriod_bookValueOfDebt +
                   periodPRIORToMostRecent_EndOfPeriod_presentValLeases +
                   periodPRIORToMostRecent_EndOfPeriod_bookValueOfEquity -
                   periodPRIORToMostRecent_EndOfPeriod_bookValueOfCash)

    mostRecentPeriod_EndOfPeriod_ReturnOnCapital = (mostRecentPeriod_EoP_AdjustedEBIT * (1 - taxRate)) / denominator
    mostRecentPeriod_EoP_CapEx = 2129.00
    mostRecentPeriod_EoP_Depreciation = 2084.00
    mostRecentPeriod_EndOfPeriod_NetCapEx = (mostRecentPeriod_EoP_CapEx - mostRecentPeriod_EoP_Depreciation)
    mostRecentPeriod_EndOfPeriod_ChangeInPVofLeases = (1 - periodPRIORToMostRecent_EndOfPeriod_presentValLeases)
    mostRecentPeriod_EndOfPeriod_ChangeInNonCashNWC= 332.00
    mostRecentPeriod_EndOfPeriod_ReinvestmentRate = ((mostRecentPeriod_EndOfPeriod_NetCapEx +
                                                      mostRecentPeriod_EndOfPeriod_ChangeInPVofLeases +
                                                      mostRecentPeriod_EndOfPeriod_ChangeInNonCashNWC) /
                                                      mostRecentPeriod_EoP_AdjustedEBIAT)

    mostRecentPeriod_EoP_AfterTaxCostOfDebt = (prexTaxCoD * (1 - taxRate))
    mostRecentPeriod_EoP_MarketCap = 34346.00
    mostRecentPeriod_EoP_DebtToCapital = (mostRecentPeriod_EoP_AdjustedDebt / (mostRecentPeriod_EoP_AdjustedDebt + mostRecentPeriod_EoP_MarketCap))
    mostRecentPeriod_EoP_EquitytToCapital = (1 - mostRecentPeriod_EoP_DebtToCapital)

    '''Assumptions & Expectations'''
    initialStage_ExpectedReinvestmentRate = 0.40
    initialStage_ExpectedGrowthRateFor_EBIAT = (mostRecentPeriod_EndOfPeriod_ReturnOnCapital * initialStage_ExpectedReinvestmentRate)
    initialStage_CostOfEquity = (costOfEquityAssumptions[0]["RiskFreeRate"] + costOfEquityAssumptions[0]["Beta"] * \
                                 costOfEquityAssumptions[0]["EquityMarketPremium"])
    mostRecentPeriod_EoP_WACC = ((mostRecentPeriod_EoP_DebtToCapital * mostRecentPeriod_EoP_AfterTaxCostOfDebt) +
                                 (mostRecentPeriod_EoP_EquitytToCapital * initialStage_CostOfEquity))
    initialStage_WACC = mostRecentPeriod_EoP_WACC

    stableStage_ExpectedGrowthRateFor_EBIAT = 0.03
    stableStage_WACC = initialStage_WACC
    stableStage_ROIC = stableStage_WACC
    stableStage_ExpectedReinvestmentRate = (stableStage_ExpectedGrowthRateFor_EBIAT / stableStage_ROIC)

    '''Calculations'''
    outputTable = {"RateOfGrowthFromPriorYear": [], "ReinvestmentRate": [], "EBIAT": [],
                   "Reinvestment": [], "FCFF": [], "WACC": [], "PVofFCFF": []}
    temp = mostRecentPeriod_EoP_AdjustedEBIAT
    for x in range(0, initialStageDuration):
        ebiat = round(temp * (1 + initialStage_ExpectedGrowthRateFor_EBIAT), 2)
        reinvestment = round((ebiat * initialStage_ExpectedReinvestmentRate), 2)
        fcff = round((ebiat - reinvestment), 2)
        pvFCFF = round((fcff / (1 + initialStage_WACC)**(x + 1)), 2)
        print("(EBIAT = ", ebiat, ") - (Reinvestment = ", reinvestment, ") = (FCFF = ", fcff, ")")
        print("[PV of FCFF @", round(100*initialStage_WACC, 2), "% =", pvFCFF, "]")
        outputTable["RateOfGrowthFromPriorYear"].append(initialStage_ExpectedGrowthRateFor_EBIAT)
        outputTable["ReinvestmentRate"].append(initialStage_ExpectedReinvestmentRate)
        outputTable["EBIAT"].append(ebiat)
        outputTable["Reinvestment"].append(reinvestment)
        outputTable["FCFF"].append(fcff)
        outputTable["WACC"].append(initialStage_WACC)
        outputTable["PVofFCFF"].append(pvFCFF)
        temp = ebiat

    terminalValue = calculateTerminalValue(outputTable["EBIAT"][-1] * (1 - stableStage_ExpectedReinvestmentRate),
                                           stableStage_ExpectedGrowthRateFor_EBIAT, stableStage_WACC)
    pvTerminalValue = (terminalValue / (1 + stableStage_WACC) ** (initialStageDuration))
    valueOfOperatingAssets = round((sum(outputTable["PVofFCFF"]) + pvTerminalValue), 2)
    valueOfEquity = round((valueOfOperatingAssets +
                           mostRecentPeriod_EoP_ReportedCashBalance -
                           mostRecentPeriod_EoP_AdjustedDebt), 2)
    valueOfEquityPerShare = round((valueOfEquity / mostRecentPeriod_EoP_SharesOutstanding), 2)

    return valueOfOperatingAssets

def adjustedPresentValue(initialStageDuration, amountOfDebtFinancingForAcquisiton, costOfEquityAssumptions=None, creditRiskAssumptions=None):
    '''This is section is based on Damodaran's Ch.15 pgs 398-401'''
    '''Actually Observed Metrics'''
    mostRecentPeriod_EoP_EBIT = 230.00# million
    mostRecentPeriod_EoP_Revenue = 1722.00

    '''Assumptions & Expectations'''
    probabilityOfDefault = creditRiskAssumptions["DefaultRisk"]
    costs_AS_percentOfFirmValue = creditRiskAssumptions["BankruptcyCostMargin"]

    preTaxCostOfDebt = 0.07
    taxRate = 0.35
    est_UnleveredCOE = (costOfEquityAssumptions[0]["RiskFreeRate"] + costOfEquityAssumptions[0]["Beta"] * \
                        costOfEquityAssumptions[0]["EquityMarketPremium"])

    stableStage_ExpectedGrowthRateFor_EBIT = 0.035
    stableStage_ExpectedROC = 0.14
    stableStage_ExpectedReinvestmentRate = round((stableStage_ExpectedGrowthRateFor_EBIT / stableStage_ExpectedROC), 3)

    mostRecentPeriod_EoP_EBIAT = (mostRecentPeriod_EoP_EBIT * (1 - taxRate))
    mostRecentPeriod_EoP_FCFF = mostRecentPeriod_EoP_EBIAT * (1 - stableStage_ExpectedReinvestmentRate)

    expectedForNextPeriod_FCFF = mostRecentPeriod_EoP_FCFF * (1 + stableStage_ExpectedGrowthRateFor_EBIT)
    estimated_UnleveredFirmValue = expectedForNextPeriod_FCFF / (est_UnleveredCOE - stableStage_ExpectedGrowthRateFor_EBIT)

    '''Calculations'''
    outputTable = {"AmtDebtDue_at_BoP": [], "Payment": [], "InterestExpense": [], "TaxBenefit": [], "PVofTaxBenefit":[]}
    temp = amountOfDebtFinancingForAcquisiton
    plannedFixedAnnualRePMT = 150.00
    for x in range(initialStageDuration):
        amountOfDebtDue = round(temp, 2)
        payment = plannedFixedAnnualRePMT
        interestExpense = round((amountOfDebtDue * preTaxCostOfDebt), 2)
        taxBenefit = round((interestExpense * taxRate), 2)
        pvTaxBenefit = round(taxBenefit / ((1 + preTaxCostOfDebt)**(x + 1)), 2)

        outputTable["AmtDebtDue_at_BoP"].append(amountOfDebtDue)
        outputTable["Payment"].append(payment)
        outputTable["InterestExpense"].append(interestExpense)
        outputTable["TaxBenefit"].append(taxBenefit)
        outputTable["PVofTaxBenefit"].append(pvTaxBenefit)
        temp -= plannedFixedAnnualRePMT

    pvPerpetualTaxBenfit = (outputTable["TaxBenefit"][-1] / preTaxCostOfDebt) / (1 + preTaxCostOfDebt) ** initialStageDuration
    pvTaxBenefits = round((sum(outputTable["PVofTaxBenefit"]) + pvPerpetualTaxBenfit), 2)

    expectedBankruptcyCost = ((estimated_UnleveredFirmValue + pvTaxBenefits) * costs_AS_percentOfFirmValue * probabilityOfDefault)
    expectedBankruptcyCost = round(expectedBankruptcyCost, 2)
    valueOfFirm = round((estimated_UnleveredFirmValue + pvTaxBenefits - expectedBankruptcyCost), 2)

    outputTable["PVofPerpetualTaxBenefit"] = pvPerpetualTaxBenfit
    outputTable["ExpectedBankruptcyCosts"] = expectedBankruptcyCost
    outputTable["FirmValue_via_APV"] = valueOfFirm

    return outputTable

def capitalize_R_and_D_Expense(currentYears_R_and_D_Expense, historical_R_and_D_Expenses):
    '''This is based on Damodaran's Ch. 9 pgs 234-235'''

    '''Actually Observed Metrics'''
    mostRecentPeriod_EoP_EBIT = 5594.00
    mostRecentPeriod_EoP_R_and_D_Expense = 3030.00
    mostRecentPeriod_EoP_NetIncome = 4196.00

    periodPRIORToMostRecent_EndOfPeriod_valueOfResearchAsset = 11948.00
    periodPRIORToMostRecent_EndOfPeriod_BookValueOfEquity = 17869.00
    periodPRIORToMostRecent_EndOfPeriod_BookValueOfCapital = 21985.00

    '''Calculations'''
    amortizableLifeOfAssets = len(historical_R_and_D_Expenses)
    annualPercentUnamortized = (1 / amortizableLifeOfAssets)
    output = {"UnamortizedAmount": [], "AmortizationForTheYear": []}
    for x in range(0, len(historical_R_and_D_Expenses)):

        unamortizedPortion = (historical_R_and_D_Expenses[x] * (1 - ((x + 1) * annualPercentUnamortized)))
        amountAmortizedForYear = (historical_R_and_D_Expenses[x] - unamortizedPortion)
        output["UnamortizedAmount"].append(round(unamortizedPortion, 2))
        output["AmortizationForTheYear"].append(round(amountAmortizedForYear, 2))
    mostRecentPeriod_EoP_valueOfResearchAsset = sum(output["UnamortizedAmount"])
    mostRecentPeriod_EoP_amountToAmortizeForThisYear = sum(output["AmortizationForTheYear"])


    mostRecentPeriod_EoP_AdjustedEBIT = (mostRecentPeriod_EoP_EBIT + mostRecentPeriod_EoP_R_and_D_Expense - mostRecentPeriod_EoP_amountToAmortizeForThisYear)
    mostRecentPeriod_EoP_AdjustedNetIncome = (mostRecentPeriod_EoP_NetIncome + mostRecentPeriod_EoP_R_and_D_Expense - mostRecentPeriod_EoP_amountToAmortizeForThisYear)


    periodPRIORToMostRecent_EndOfPeriod_AdjBookValueOfEquity = (periodPRIORToMostRecent_EndOfPeriod_BookValueOfEquity + \
                                                                periodPRIORToMostRecent_EndOfPeriod_valueOfResearchAsset)
    periodPRIORToMostRecent_EndOfPeriod_AdjBookValueOfCapital = (periodPRIORToMostRecent_EndOfPeriod_BookValueOfCapital + \
                                                                 periodPRIORToMostRecent_EndOfPeriod_valueOfResearchAsset)

    return output

def adjust_NetIncome(mostRecentPeriod_EoP_NetIncomeFromContinuingOperations, factorsToBeAdjustedForIndividualYear,
                     historicalSales, historicalOtherExpenses):
    '''From Damodaran Ch. 9 pgs243-247  ***You should verify if this is the same as pg 46 in Rosenbaum & Pearl'''

    def normalizeFigureForOtherExpenses(historyOfOtherExpenses, historicalSales):

        temp = sum([(otherExpense / revenue) for otherExpense, revenue in zip(historyOfOtherExpenses, historicalSales)])
        averageRatioOfOtherExpensesToSales = (temp / len(historicalSales))
        return averageRatioOfOtherExpensesToSales

    factorsToBeAdjusted = factorsToBeAdjustedForIndividualYear
    taxRate = factorsToBeAdjusted["MarginalTaxRate"]
    firmsEquityInTheEarningsOfOtherFirms = factorsToBeAdjusted["FirmsEquityInTheNetIncomeOfUnconsolidatedAffiliates"]
    firmsMinorityInterestInTheEarningsOfOtherFirms = factorsToBeAdjusted["MinorityInterestsInEarningsOfSubsidiaries"]
    factorsToBeAdjusted["InventoryCharges"]
    factorsToBeAdjusted["RestructuringCharges"] #or Asset Impairment
    factorsToBeAdjusted["OtherExpenses"]

    avgRatioOfOtherExpensesToSales = normalizeFigureForOtherExpenses(historicalOtherExpenses, historicalSales)

    netAdj = -1 * firmsEquityInTheEarningsOfOtherFirms + firmsMinorityInterestInTheEarningsOfOtherFirms + \
             (1 - taxRate) * (factorsToBeAdjusted["InventoryCharges"] + factorsToBeAdjusted["RestructuringCharges"]) + \
             (1 - taxRate) * (factorsToBeAdjusted["OtherExpenses"] - historicalSales[-1] * avgRatioOfOtherExpensesToSales)

    adjustedNetIncomeFromContinuingOperations = (mostRecentPeriod_EoP_NetIncomeFromContinuingOperations + netAdj)

    print(mostRecentPeriod_EoP_NetIncomeFromContinuingOperations, " = {UN}ADJUSTED Net Income from CONTINUING OPERATIONS\n" 
          "subtract", round(firmsEquityInTheEarningsOfOtherFirms, 2), "\n",
          "add back", round(firmsMinorityInterestInTheEarningsOfOtherFirms, 2), "\n",
          "add back Inventory Charges: (1 -", round(taxRate, 2), ") *", round(factorsToBeAdjusted["InventoryCharges"], 2), "\n",
          "add back Restructuring Charges: (1 -", round(taxRate, 2), ") *", round(factorsToBeAdjusted["RestructuringCharges"], 2), "\n",
          "add back Other Expenses: (1 -", round(taxRate, 2), ") *", round(factorsToBeAdjusted["OtherExpenses"], 2), "\n",
          "subtract Normalization of Other Expenses: (", round(avgRatioOfOtherExpensesToSales, 3), "*", round(historicalSales[-1], 2), ")", "\n",
          "---------", "\n",
          round(adjustedNetIncomeFromContinuingOperations, 2), " = ADJUSTED Net Income from CONTINUING OPERATIONS\n")

    return adjustedNetIncomeFromContinuingOperations