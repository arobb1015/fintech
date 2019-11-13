import pandas as pd
import numpy as np
from datetime import date
from math import *
from wallStreetPrep import *

todaysCurrentDate = date.today()
nextDate_for_FY_EoP = date(2020, 9, 30)
time_Until_Next_FY_EoP = (nextDate_for_FY_EoP - todaysCurrentDate)
percent_Of_Year_Remaining_Until_Next_FY_EoP = (time_Until_Next_FY_EoP.days / 365.2425) # Accurate up to the 400-year exception to account for leap years
print(percent_Of_Year_Remaining_Until_Next_FY_EoP)

def normalizeLastCashflowInProjectionWindow(unleveredFCF=None, stockBasedCompensation=None, netWorkingCapital=None):
    normalized_Unlevered_FCF = (unleveredFCF + stockBasedCompensation + netWorkingCapital)
    return normalized_Unlevered_FCF

def discountFigure(figure=None, rate=None, periodExponent=None, intraPeriodDiscountTiming=None):
    discountRate = rate
    partOfPeriodInWhichCashflowsAreGenerated = intraPeriodDiscountTiming

    if(partOfPeriodInWhichCashflowsAreGenerated == "MoP"):
        midperiodAdjustmentFactor = ((1 + discountRate) ** 0.5)
        discountFactor = (1 / ((1 + discountRate) ** (periodExponent - (0.50 * midperiodAdjustmentFactor))))
    elif(partOfPeriodInWhichCashflowsAreGenerated == "EoP"):
        midperiodAdjustmentFactor = 1.00
        discountFactor = (1 / ((1 + discountRate) ** (periodExponent - (0.00 * midperiodAdjustmentFactor))))
    discountedFigure = (figure * discountFactor)
    return discountedFigure

def calcTerminalValue_GGM(mre_FCF_Figure=None,
                          mostRecentFiguresDiscountingInputs=None,
                          mre_ReferenceFigureForMultiple=None,
                          mre_LongTermGrowthRate=None,
                          mre_WACC=None, intraPeriodDiscountTiming=None):
    '''The 'NON-DISCOUNTED TERMINAL VALUE' is the PV @ EoP of the MOST RECENT PERIOD'S FIGURE'''
    onePeriodAheadOfTheMostRecentFigure = (mre_FCF_Figure * (1 + mre_LongTermGrowthRate))
    mre_nondiscountedTerminalValue = (onePeriodAheadOfTheMostRecentFigure / (mre_WACC - mre_LongTermGrowthRate))
    if(intraPeriodDiscountTiming == "MoP"):
        midperiodAdjustmentFactor = ((1 + mre_WACC) ** 0.5)
        mre_nondiscountedTerminalValue *= midperiodAdjustmentFactor
    discountRate = mostRecentFiguresDiscountingInputs[0]
    period = mostRecentFiguresDiscountingInputs[1]
    mre_presentValueOfTerminalValue = discountFigure(figure=mre_nondiscountedTerminalValue,
                                                     rate=mre_WACC, periodExponent=period)
    mre_ImpliedExitMultiple = (mre_nondiscountedTerminalValue / mre_ReferenceFigureForMultiple)
    return mre_presentValueOfTerminalValue

def calcTerminalValue_EMM(mostRecentReferenceFigureForMultiple=None, mre_FCF_Figure=None, mre_WACC=None,
                          exitMultipleAssumption=None,
                          mostRecentFiguresDiscountingInputs=None, intraPeriodDiscountTiming=None):
    '''The inputted 'ExitMultipleAssumption' comes from the median value of a CompsAnalysis'''

    '''The 'NON-DISCOUNTED TERMINAL VALUE' is the PV @ EoP of the MOST RECENT PERIOD'S FIGURE'''
    mre_nondiscountedTerminalValue = (mostRecentReferenceFigureForMultiple * exitMultipleAssumption)

    discountRate = mostRecentFiguresDiscountingInputs[0]
    period = mostRecentFiguresDiscountingInputs[1]
    mre_PresentValueOfTerminalValue = discountFigure(figure=mre_nondiscountedTerminalValue,
                                                     rate=discountRate, periodExponent=period)

    if(intraPeriodDiscountTiming == "MoP"):
        midperiodAdjustmentFactor = ((1 + mre_WACC) ** 0.5)
        mre_FCF_Figure *= midperiodAdjustmentFactor

    mre_ImpliedPerpetualGrowthRate = ((mre_WACC - (mre_FCF_Figure / mre_nondiscountedTerminalValue)) / \
                                      (1 + (mre_FCF_Figure / mre_nondiscountedTerminalValue)))

    return mre_PresentValueOfTerminalValue

enterpriseValue = 100.00
mrp_TaxLiabilityOnTrappedCash = 0.00 #the amount of tax owed on 'Cash' thats currently trapped abroad and hasnt been repatriated yet

mrp_Cash = pullData(source=historical["BalanceSheet"]["Liabilities"], itemOfInterest="(Cash)",
                    metric="EoP", specificYear=2013)
mrp_LTD = pullData(source=historical["BalanceSheet"]["Liabilities"], itemOfInterest="(LTD)",
                   metric="EoP", specificYear=2013)
mrp_NetDebt = (mrp_LTD - mrp_Cash)
mre_MarketEquityValue = (enterpriseValue - mrp_NetDebt - mrp_TaxLiabilityOnTrappedCash)

mrp_BasicSharesOutstanding = 4.00 # pull this from either the latest 10-Q or Press Release (whichever is most recent)
mrp_stockOptionsOutstanding = 2.4
mrp_MarketValueOfCommonStockPricePerShare = 200.00
mrp_weightedAverageExercisePricePerShare = 157.93

if(mrp_weightedAverageExercisePricePerShare < mrp_MarketValueOfCommonStockPricePerShare):
    mre_number_of_in_the_money_exercisable_options = mrp_stockOptionsOutstanding
else:
    mre_number_of_in_the_money_exercisable_options = 0.000
mre_proceeds_from_exercised_options = (mrp_weightedAverageExercisePricePerShare * mre_number_of_in_the_money_exercisable_options)
mre_number_of_CommonStockSharesRepurchased = (mre_proceeds_from_exercised_options / mrp_MarketValueOfCommonStockPricePerShare)

'''When calculating Diluted Shares Outstanding with the TSM, 
   we assume that the proceeds from options that were exercised are
   immediately/instantaneously used to repurchase publicly issued
   common stock so as to mitigate the dilutive effect of stock 
   options on the publicly traded equity'''

mre_net_dilutive_options = (mrp_stockOptionsOutstanding - mre_number_of_CommonStockSharesRepurchased)
mrp_Restricted_Stock_Units_OriginalBalance = 13326 #in thousands
mrp_Restricted_Stock_Units_Granted = 6964 #in thousands
mrp_Restricted_Stock_Units_Vesting = 2626 #in thousands
mrp_Restricted_Stock_Units_Cancelled = 440 #in thousands
mrp_Restricted_Stock_Units_Outstanding = (mrp_Restricted_Stock_Units_OriginalBalance +
                                          mrp_Restricted_Stock_Units_Granted -
                                          mrp_Restricted_Stock_Units_Vesting -
                                          mrp_Restricted_Stock_Units_Cancelled)
mre_Dilutive_Impact_From_Other_Securities = 0.00
mre_Net_Diluted_Shares_Outstanding = (mrp_BasicSharesOutstanding +
                                      mre_net_dilutive_options +
                                      mre_Dilutive_Impact_From_Other_Securities)
mre_MarketEquityValuePerShare = (mre_MarketEquityValue / mre_Net_Diluted_Shares_Outstanding)
mre_MarketPremium_OR_Discount_TO_FairValue = ((mrp_MarketValueOfCommonStockPricePerShare / mre_MarketEquityValuePerShare) - 1)
mre_MarketCapitalization = (mrp_MarketValueOfCommonStockPricePerShare * mre_Net_Diluted_Shares_Outstanding) #Use current MV shareprice but with MRE Net Dilutive Shares outstanding

mre_marginal_tax_rate = 0.26 # use the average of the projected tax rates
mre_pre_tax_cost_of_debt = 0.02
mre_after_tax_cost_of_debt = (mre_pre_tax_cost_of_debt * (1 - mre_marginal_tax_rate))

mre_book_value_of_debt_as_proxy_for_market_value = mrp_NetDebt
mre_capital = (mre_MarketCapitalization + mre_book_value_of_debt_as_proxy_for_market_value)
mre_Debt_TO_Capital_Ratio = (mre_book_value_of_debt_as_proxy_for_market_value / mre_capital)
mre_Equity_TO_Capital_Ratio = (1 - mre_Debt_TO_Capital_Ratio)

mrp_TEN_Year_US_Treasury_Yield = 0.025
mrp_SIXTY_MONTH_RegressionBeta = 0.93
mre_capm_parameters = ({"Beta": mrp_SIXTY_MONTH_RegressionBeta,
                        "RiskFreeRate": mrp_TEN_Year_US_Treasury_Yield,
                        "EquityMarketRiskPremium": 0.08},
                       {"Beta": 0.90,
                        "RiskFreeRate": mrp_TEN_Year_US_Treasury_Yield,
                        "EquityMarketRiskPremium": 0.05})

mre_costOfEquity = (mre_capm_parameters[0]["RiskFreeRate"] + mre_capm_parameters[0]["Beta"] * mre_capm_parameters[0]["EquityMarketRiskPremium"])
mre_wacc = ((mre_after_tax_cost_of_debt * mre_Debt_TO_Capital_Ratio) + (mre_costOfEquity * mre_Equity_TO_Capital_Ratio))