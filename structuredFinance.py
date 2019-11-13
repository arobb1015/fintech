import pandas as pd
import numpy as np
import datetime
from math import *

'''
This module is based off of the 2009 book by William Preinitz (A Fast Track to Structured Finance)
'''

# Note on Nomenclature/Abbreviations:
#                                   'mre' stands for 'MOST RECENT ESTIMATE' (the ESTIMATE you most recently made)
#                                   'mrp' stands for 'MOST RECENT PERIOD'S' (an actually reported/observed official figure)
#                                   'pp'  stands for 'PRIOR PERIOD'S' (an actually reported/observed official figure)
#                                   'cp'  stands for 'CURRENT PERIOD'S' (an actually reported/observed official figure)
#                                   'np'  stands for 'NEXT PERIOD'S' (an actually reported/observed official figure)

'''These 2 Variables are sourced/inputted from the function's PARAMETERS'''
currentPeriod = 1
pp_Amt_EoP_DELINQUENCY_RESERVE_BAL_CAP = 10.00

dictionary = {}
keys = list(dictionary.keys())
# dataFrame = pd.DataFrame([dictionary[x] for x in keys], columns=list(range(startingYear, endingYear + 1)), index=keys)

collateralCashflows = pd.DataFrame([dictionary[x] for x in keys],
                         columns=["BoP_Principal_Balance",
                                  "BoP_Pool_Factor",
                                  "Amount_of_Regular_Amortization_of_Principal",
                                  "Amount_of_Prepayment_of_Principal",
                                  "Amount_of_Principal Defaulted",
                                  "EoP_Principal_Balance",
                                  "Amount_of_Principal_Retired",
                                  "Amount_of_Coupon_Income",
                                  "Amount_of_Principal_Recovered"], index=range(0, 370))
expenses = pd.DataFrame([dictionary[x] for x in keys],
                         columns=["BoP_Program_Fee_Amount_Due",
                                  "Amount_of_Program_Fee_PAID",
                                  "Amount_of_Program_Fee_UNPAID",
                                  "Cash_Available_POST_Program_Fee",
                                  "BoP_Service_Fee_Amount_Due",
                                  "Amount_of_Service_Fee_PAID",
                                  "Amount_of_Service_Fee_UNPAID",
                                  "Cash_Available_POST_Program_Fee_&_Service_Fee"], index=range(0, 370))
conduitInterest = pd.DataFrame([dictionary[x] for x in keys],
                         columns=["BoP_Interest_Expense_Amount_Due",
                                  "Amount_of_IE_covered_by_CASH",
                                  "Amount_of_IE_covered_by_DRA",
                                  "Amount_of_IE_UNPAID",
                                  "Cash_Available_POST_Fees_&_IE"], index=range(0, 370))
conduitPrincipal = pd.DataFrame([dictionary[x] for x in keys],
                         columns=["BoP_Principal_Amount_Due",
                                  "Amount_of_Principal_PAID",
                                  "Cash_Available_POST_Principal_RePMT"], index=range(0, 370))
excessCashTreatment = pd.DataFrame([dictionary[x] for x in keys],
                         columns=["Amount_added_to_DRA",
                                  "Amount_covered_from_DRA",
                                  "Amount_released_from_DRA_for_SELLER"], index=range(0, 370))
conduitSummary = pd.DataFrame([dictionary[x] for x in keys],
                         columns=["BoP_CONDUIT_Balance",
                                  "EoP_CONDUIT_Balance_as_%_of_STARTING_Balance",
                                  "EoP_CONDUIT_Balance_as_%_of_BoP_CONDUIT_Balance",
                                  "Amount_of_PRINCIPAL_reduced_during_Period",
                                  "Amount_of_IE_serviced_during_Period",
                                  "UNKNOWN_PARAMETER_(A)", "UNKNOWN_PARAMETER_(B)"], index=range(0, 370))
dra_Activity = pd.DataFrame([dictionary[x] for x in keys],
                         columns=["BoP_DRA_Cap",
                                  "BoP_DRA_Balance",
                                  "Amount_drawn_from_DRA",
                                  "Amount_added_to_DRA",
                                  "Amount_released_to_SELLER"
                                  "EoP_DRA_Balance"], index=range(0, 370))
dealTriggerStatuses = pd.DataFrame([dictionary[x] for x in keys],
                         columns=["Event_Triggered",
                                  "Clean-Up_Triggered",
                                  "Default_Triggered",
                                  "Global_Triggered"], index=range(0, 370))


def generateRecordsForPeriod(dataframe=None, currentPeriod=None, pp_Amt_EoP_DELINQUENCY_RESERVE_BAL_CAP=None,
                             pp_CLEANUP_TRIGGER_STATUS=None, cp_Rate_BoP_3_MONTH_ROLLING_AVERAGE_DEFAULT=None,
                             cp_Rate_CONDUIT_FUNDING_COUPON=None):

    all_pp_Rate_CONDUIT_FUNDING_PRESENT_VALUE_FACTORS = []
    there_hasnt_been_a_non_credit_event_throughout_the_period = True
    firstPeriod_Amt_BoP_CONDUIT_PRINCIPAL_BAL = 0.000
    firstPeriod_Amt_BoP_DELINQUENCY_RESERVE_BAL_CAP = 0.000
    firstPeriod_Amt_EoP_DELINQUENCY_RESERVE_BAL_CAP = firstPeriod_Amt_BoP_DELINQUENCY_RESERVE_BAL_CAP
    firstPeriod_Amt_BoP_DELINQUENCY_RESERVE_BAL = 0.000
    firstPeriod_Amt_EoP_DELINQUENCY_RESERVE_BAL = firstPeriod_Amt_BoP_DELINQUENCY_RESERVE_BAL
    firstPeriod_BoP_CONDUIT_PRINCIPAL_BAL = 20.00

    cp_Amt_BoP_CONDUIT_PRINCIPAL_BAL = 10.00
    cp_Ratio_BoP_POOL_FACTOR = (cp_Amt_BoP_CONDUIT_PRINCIPAL_BAL / firstPeriod_BoP_CONDUIT_PRINCIPAL_BAL)

    cp_Amt_REGULARLY_AMORTIZED_PRINCIPAL = 5.00
    cp_Amt_PREPAID_PRINCIPAL = 5.00
    cp_Amt_TOTAL_PRINCIPAL_RETIRED = (cp_Amt_REGULARLY_AMORTIZED_PRINCIPAL + cp_Amt_PREPAID_PRINCIPAL)

    cp_Amt_INCOME_FROM_COUPONS = 10.00
    cp_Amt_RECOVERIES_OF_PRINCIPAL = 10.00
    pp_Amt_RELEASED_FROM_DELINQUENT_RESERVE_ACCOUNT = 10.0
    cp_Amt_CASH_AVAIL_FOR_WATERFALL = (cp_Amt_TOTAL_PRINCIPAL_RETIRED + cp_Amt_INCOME_FROM_COUPONS +
                                       cp_Amt_RECOVERIES_OF_PRINCIPAL + pp_Amt_RELEASED_FROM_DELINQUENT_RESERVE_ACCOUNT)

    pp_Amt_PROGRAM_EXPENSE_UNPAID = 5.00
    cp_Rate_PROGRAM_EXPENSE_DUE = 0.075
    cp_Amt_PROGRAM_EXPENSE_DUE = (cp_Rate_PROGRAM_EXPENSE_DUE * (cp_Amt_BoP_CONDUIT_PRINCIPAL_BAL / 12) + pp_Amt_PROGRAM_EXPENSE_UNPAID)
    cp_Amt_PROGRAM_EXPENSE_PAID = min(cp_Amt_CASH_AVAIL_FOR_WATERFALL, cp_Amt_PROGRAM_EXPENSE_DUE)
    cp_Amt_PROGRAM_EXPENSE_UNPAID = (cp_Amt_PROGRAM_EXPENSE_DUE - cp_Amt_PROGRAM_EXPENSE_PAID)
    cp_Amt_CASH_AVAIL_AFTER_PAYING_PROGRAM_EXPENSE = (cp_Amt_CASH_AVAIL_FOR_WATERFALL - cp_Amt_PROGRAM_EXPENSE_PAID)

    pp_Amt_SERVICING_FEE_UNPAID = 5.00
    cp_Rate_SERVICING_FEE_DUE = 0.03
    cp_Amt_SERVICING_FEE_DUE = (cp_Rate_SERVICING_FEE_DUE * (cp_Amt_BoP_CONDUIT_PRINCIPAL_BAL / 12) + pp_Amt_SERVICING_FEE_UNPAID)
    cp_Amt_SERVICING_FEE_PAID = min(cp_Amt_CASH_AVAIL_AFTER_PAYING_PROGRAM_EXPENSE, cp_Amt_SERVICING_FEE_DUE)
    cp_Amt_SERVICING_FEE_UNPAID = (cp_Amt_SERVICING_FEE_DUE - cp_Amt_SERVICING_FEE_PAID)
    cp_Amt_CASH_AVAIL_AFTER_PAYING_PROGRAM_EXPENSE_AND_SERVICING_FEE = (cp_Amt_CASH_AVAIL_AFTER_PAYING_PROGRAM_EXPENSE - cp_Amt_SERVICING_FEE_PAID)

    pp_Amt_INTEREST_EXPENSE_UNPAID = 5.00
    cp_Rate_CONDUIT_FUNDING_COUPON = 0.38
    cp_Amt_BoP_DELINQUENCY_RESERVE_BAL = 50.00
    cp_Amt_INTEREST_EXPENSE_DUE = (cp_Amt_BoP_CONDUIT_PRINCIPAL_BAL * (cp_Rate_CONDUIT_FUNDING_COUPON / 12) + pp_Amt_INTEREST_EXPENSE_UNPAID)
    cp_Amt_INTEREST_EXPENSE_COVERED_BY_AVAIL_CASH = min(cp_Amt_CASH_AVAIL_AFTER_PAYING_PROGRAM_EXPENSE_AND_SERVICING_FEE, cp_Amt_INTEREST_EXPENSE_DUE)
    cp_Amt_INTEREST_EXPENSE_UNCOVERED = (cp_Amt_CASH_AVAIL_AFTER_PAYING_PROGRAM_EXPENSE_AND_SERVICING_FEE - cp_Amt_INTEREST_EXPENSE_COVERED_BY_AVAIL_CASH)
    cp_Amt_INTEREST_EXPENSE_COVERED_BY_DELINQUENCY_RESERVE = min(cp_Amt_INTEREST_EXPENSE_UNCOVERED,
                                                                 cp_Amt_BoP_DELINQUENCY_RESERVE_BAL)
    cp_Amt_INTEREST_EXPENSE_UNPAID = (cp_Amt_INTEREST_EXPENSE_UNCOVERED - cp_Amt_INTEREST_EXPENSE_COVERED_BY_DELINQUENCY_RESERVE)
    cp_Amt_CASH_AVAIL_AFTER_PAYING_PROGRAM_EXPENSE_AND_SERVICING_FEE_AND_INTEREST_EXPENSE = (cp_Amt_INTEREST_EXPENSE_DUE - cp_Amt_INTEREST_EXPENSE_COVERED_BY_AVAIL_CASH)

    cp_Amt_CONDUIT_PRINCIPAL_DUE = 30.00
    cp_Amt_CONDUIT_PRINCIPAL_PAID = min(cp_Amt_CASH_AVAIL_AFTER_PAYING_PROGRAM_EXPENSE_AND_SERVICING_FEE_AND_INTEREST_EXPENSE, cp_Amt_CONDUIT_PRINCIPAL_DUE)
    cp_Amt_CASH_AVAIL_AFTER_PAYING_CONDUIT_PRINCIPAL = (cp_Amt_CASH_AVAIL_AFTER_PAYING_PROGRAM_EXPENSE_AND_SERVICING_FEE_AND_INTEREST_EXPENSE - cp_Amt_CONDUIT_PRINCIPAL_PAID)

    if (currentPeriod >= 1):
        cp_Amt_BoP_DELINQUENCY_RESERVE_BAL_CAP = pp_Amt_EoP_DELINQUENCY_RESERVE_BAL_CAP
    elif (currentPeriod < 1):
        pp_Amt_EoP_DELINQUENCY_RESERVE_BAL_CAP = firstPeriod_Amt_EoP_DELINQUENCY_RESERVE_BAL_CAP
        cp_Amt_BoP_DELINQUENCY_RESERVE_BAL_CAP = pp_Amt_EoP_DELINQUENCY_RESERVE_BAL_CAP
    cp_Amt_SPACE_LEFT_TO_FUND_DELINQUENCY_RESERVE = (cp_Amt_BoP_DELINQUENCY_RESERVE_BAL_CAP - cp_Amt_BoP_DELINQUENCY_RESERVE_BAL)
    temp = min(cp_Amt_CASH_AVAIL_AFTER_PAYING_CONDUIT_PRINCIPAL, cp_Amt_SPACE_LEFT_TO_FUND_DELINQUENCY_RESERVE)
    cp_Amt_CASH_USED_FOR_FUNDING_DELINQUENCY_RESERVE = max(temp, 0)
    cp_Amt_DRAWN_FROM_DELINQUENCY_RESERVE_TO_PAY_SELLER = max((cp_Amt_BoP_DELINQUENCY_RESERVE_BAL - cp_Amt_BoP_DELINQUENCY_RESERVE_BAL_CAP), 0)
    cp_Amt_CASH_PAID_TO_SELLER = (cp_Amt_CASH_AVAIL_AFTER_PAYING_CONDUIT_PRINCIPAL - cp_Amt_CASH_USED_FOR_FUNDING_DELINQUENCY_RESERVE)
    cp_Amt_EoP_DELINQUENCY_RESERVE_BAL = (cp_Amt_BoP_DELINQUENCY_RESERVE_BAL -
                                          cp_Amt_INTEREST_EXPENSE_COVERED_BY_DELINQUENCY_RESERVE +
                                          cp_Amt_CASH_USED_FOR_FUNDING_DELINQUENCY_RESERVE -
                                          cp_Amt_DRAWN_FROM_DELINQUENCY_RESERVE_TO_PAY_SELLER)
    np_Amt_BoP_DELINQUENCY_RESERVE_BAL = cp_Amt_EoP_DELINQUENCY_RESERVE_BAL

    cp_Rate_ADVANCE_RATE = 0.02
    if (cp_Amt_BoP_CONDUIT_PRINCIPAL_BAL > 0.0000):
        cp_Amt_EoP_CONDUIT_PRINCIPAL_BAL = (cp_Amt_BoP_CONDUIT_PRINCIPAL_BAL * cp_Rate_ADVANCE_RATE)
        np_Amt_BoP_CONDUIT_PRINCIPAL_BAL = cp_Amt_EoP_CONDUIT_PRINCIPAL_BAL
    else:
        cp_Amt_EoP_CONDUIT_PRINCIPAL_BAL = 0.0000
        np_Amt_BoP_CONDUIT_PRINCIPAL_BAL = cp_Amt_EoP_CONDUIT_PRINCIPAL_BAL

    cp_EoP_CONDUIT_PRINCIPAL_BAL_AS_PERCENT_OF_firstPeriod_BoP_CONDUIT_PRINCIPAL_BAL = (cp_Amt_EoP_CONDUIT_PRINCIPAL_BAL / firstPeriod_BoP_CONDUIT_PRINCIPAL_BAL)

    try:
        cp_EoP_CONDUIT_PRINCIPAL_BAL_AS_PERCENT_OF_cp_BoP_CONDUIT_PRINCIPAL_BAL = (cp_Amt_EoP_CONDUIT_PRINCIPAL_BAL / cp_Amt_BoP_CONDUIT_PRINCIPAL_BAL)
    except ZeroDivisionError:
        cp_EoP_CONDUIT_PRINCIPAL_BAL_AS_PERCENT_OF_cp_BoP_CONDUIT_PRINCIPAL_BAL = 0.0000

    cp_Amt_EoP_RECORDED_CONDUIT_PRINCIPAL_PAYDOWN = cp_Amt_CONDUIT_PRINCIPAL_PAID
    cp_Amt_EoP_RECORED_CONDUIT_INTEREST_EXPENSE_PAYDOWN = (cp_Amt_INTEREST_EXPENSE_COVERED_BY_AVAIL_CASH + cp_Amt_INTEREST_EXPENSE_COVERED_BY_DELINQUENCY_RESERVE)

    sum_of_next_two_months_coupon_income = 30.00
    if (cp_Amt_EoP_CONDUIT_PRINCIPAL_BAL > 0.0000 or sum_of_next_two_months_coupon_income > 0.0000):
        cp_Amt_EoP_DELINQUENCY_RESERVE_BAL_CAP = sum_of_next_two_months_coupon_income
        np_Amt_BoP_DELINQUENCY_RESERVE_BAL_CAP = cp_Amt_EoP_DELINQUENCY_RESERVE_BAL_CAP
    else:
        cp_Amt_EoP_DELINQUENCY_RESERVE_BAL_CAP = 0.0000
        np_Amt_BoP_DELINQUENCY_RESERVE_BAL_CAP = cp_Amt_EoP_DELINQUENCY_RESERVE_BAL_CAP

    '''This section pertains to the TRIGGER STATUSES'''

    if (there_hasnt_been_a_non_credit_event_throughout_the_period is True):
        cp_EVENT_TRIGGER_STATUS = False
    else:
        cp_EVENT_TRIGGER_STATUS = True


    if (cp_EoP_CONDUIT_PRINCIPAL_BAL_AS_PERCENT_OF_firstPeriod_BoP_CONDUIT_PRINCIPAL_BAL < 0.10 or pp_CLEANUP_TRIGGER_STATUS is True):
        cp_CLEANUP_TRIGGER_STATUS = True
    else:
        cp_CLEANUP_TRIGGER_STATUS = False


    if (cp_Rate_BoP_3_MONTH_ROLLING_AVERAGE_DEFAULT > 0.050):
        cp_DEFAULT_TRIGGER_STATUS = True
    else:
        cp_DEFAULT_TRIGGER_STATUS = False


    if(cp_EVENT_TRIGGER_STATUS is True or cp_CLEANUP_TRIGGER_STATUS is True or cp_DEFAULT_TRIGGER_STATUS is True):
        cp_GLOBAL_TRIGGER_STATUS = True
    else:
        cp_GLOBAL_TRIGGER_STATUS = False

    '''This section pertains to the DEFAULT RATES'''

    if(currentPeriod > 1):
        all_pp_Amt_PRINCIPAL_DEFAULTS = []
        cp_Rate_LIFETIME_DEFAULT_RATE = (sum(all_pp_Amt_PRINCIPAL_DEFAULTS) / firstPeriod_Amt_BoP_CONDUIT_PRINCIPAL_BAL)
    else:
        cp_Rate_LIFETIME_DEFAULT_RATE = 0.0000


    if(currentPeriod > 3):
        if (cp_Amt_BoP_CONDUIT_PRINCIPAL_BAL > 0.0000):
            three_pp_Amt_PRINCIPAL_DEFAULTS = []
            three_pp_Amt_BoP_CONDUIT_PRINCIPAL_BAL = []
            cp_Rate_BoP_3_MONTH_ROLLING_AVERAGE_DEFAULT = (sum(three_pp_Amt_PRINCIPAL_DEFAULTS) / sum(three_pp_Amt_BoP_CONDUIT_PRINCIPAL_BAL))
        else:
            cp_Rate_BoP_3_MONTH_ROLLING_AVERAGE_DEFAULT = 0.0000
    else:
        cp_Rate_BoP_3_MONTH_ROLLING_AVERAGE_DEFAULT = 0.0000

    '''This section pertains to the NET PRESENT VALUE (NPV) Calculations'''

    cp_Rate_CONDUIT_FUNDING_PRESENT_VALUE_FACTOR = (1 / (1 + (cp_Rate_CONDUIT_FUNDING_COUPON / 12)))
    all_pp_Rate_CONDUIT_FUNDING_PRESENT_VALUE_FACTORS.append(cp_Rate_CONDUIT_FUNDING_PRESENT_VALUE_FACTOR)
    cp_Rate_CONDUIT_FUNDING_CUMULATIVE_PRESENT_VALUE_FACTOR = 1.0000
    for x in range(0, len(all_pp_Rate_CONDUIT_FUNDING_PRESENT_VALUE_FACTORS)):
        cp_Rate_CONDUIT_FUNDING_CUMULATIVE_PRESENT_VALUE_FACTOR *= all_pp_Rate_CONDUIT_FUNDING_PRESENT_VALUE_FACTORS[x]
    cp_Amt_TOTAL_CONDUIT_CASHFLOW = (cp_Amt_EoP_RECORED_CONDUIT_INTEREST_EXPENSE_PAYDOWN + cp_Amt_EoP_RECORDED_CONDUIT_PRINCIPAL_PAYDOWN)
    cp_Amt_NPV_OF_SINGLE_CONDUIT_CASHFLOW = (cp_Amt_TOTAL_CONDUIT_CASHFLOW * cp_Rate_CONDUIT_FUNDING_CUMULATIVE_PRESENT_VALUE_FACTOR)

