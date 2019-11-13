import pandas as pd
import numpy as np
from datetime import date
from math import *
from wallStreetPrep import *

'''********** wall street prep LBO module **********'''

'''INPUTTED ASSUMPTIONS'''
mrp_MarketValueOfCommonStockPricePerShare = 200.00
mre_LTM_EBITDA_Assumption = 880.00
mrp_CashBalance = 1582.00
mre_MINIMUM_CASH_BALANCE_DESIRED = 180.00
mrp_GrossDebt = 1306.00
mre_NetDebt = (mrp_GrossDebt - mrp_CashBalance)
mre_DilutedSharesOutstandingFromTSM = 145.9
mre_DESIRED_EV_TO_LTM_EBITDA_Multiple_UPON_EXIT = 8.0

'''This sections deals with INITIAL VALUATION OF TARGET FIRMS EQUITY VIA INPUTTED ASSUMPTIONS'''
valuationAssumptionDriver = "ExplicitEBITDA"
if(valuationAssumptionDriver == "ExplicitOfferPerShare"):
    # Method #1 - when given an explicit Offer Per Share
    mre_ExplicitOfferPerShareAssumption = 46.25
    mre_ImpliedOfferValue = (mre_ExplicitOfferPerShareAssumption * mre_DilutedSharesOutstandingFromTSM)
    mre_ImpliedEnterpriseValue = (mre_ImpliedOfferValue + mre_NetDebt)
    mre_Implied_EV_TO_LTM_EBITDA_Multiple = (mre_ImpliedEnterpriseValue / mre_LTM_EBITDA_Assumption)
    mre_TargetEquityValue = mre_ImpliedOfferValue
elif(valuationAssumptionDriver == "ExplicitEBITDA"):
    # Method #2 - when given an explicit EV / EBITDA Multiple
    mre_ImpliedEnterpriseValue = (mre_DESIRED_EV_TO_LTM_EBITDA_Multiple_UPON_EXIT * mre_LTM_EBITDA_Assumption)
    mre_ImpliedOfferValue = (mre_ImpliedEnterpriseValue - mre_NetDebt)
    mre_ImpliedOfferValuePerShare = (mre_ImpliedOfferValue / mre_DilutedSharesOutstandingFromTSM)
    mre_TargetEquityValue = mre_ImpliedOfferValue

mre_BuyoutOfEquity = 10.00
mre_GrossDebt = 10.00
mre_Refinancing_of_Pre_LBO_Debt = mre_GrossDebt
mre_MarketPremium_OR_Discount_TO_FairValue = ((mre_ImpliedOfferValuePerShare / mrp_MarketValueOfCommonStockPricePerShare) - 1)

'''This sections deals with SOURCES & USES OF FUNDS'''
usesOfFunding = pd.DataFrame(columns=["Activity/Expense", "Amount"])
usesOfFunding.set_index("Activity/Expense", inplace=True)
sourcesOfFunding = pd.DataFrame(columns=["Source", "EBITDA_Turns", "InvestedAmount"])
sourcesOfFunding.set_index("Source", inplace=True)

# PLANNED USE OF LBO FUNDING
usesOfFunding.at["EquityBuyout", "Amount"] = mre_TargetEquityValue #This is the cost of buying all of the TargetFirm's equity
usesOfFunding.at["Refinancing_Pre-LBO_Debt", "Amount"] = abs(mrp_GrossDebt)
usesOfFunding.at["Fees(Transaction_&_Financing)", "Amount"] = 0.00

# SOURCES OF LBO FUNDING
inputtedFunds = {"ExcessCash":            {"FundingControlSpecification": ("InvestedAmount", max((mrp_CashBalance - mre_MINIMUM_CASH_BALANCE_DESIRED), 0))},

                 "Revolver":              {"FundingControlSpecification": ("EBITDA_Turns", 0.00),
                                           "FinancingFeeProjection":     [("Fee_as_Percent_of_Funded_Amount", 0.01),
                                                                          ("Term", 5)]},

                 "TermLoanA":             {"FundingControlSpecification": ("EBITDA_Turns", 3.64),
                                           "FinancingFeeProjection":     [("Fee_as_Percent_of_Funded_Amount", 0.015),
                                                                          ("Term", 7)]},

                 "TermLoanB":             {"FundingControlSpecification": ("EBITDA_Turns", 1.14),
                                           "FinancingFeeProjection":     [("Fee_as_Percent_of_Funded_Amount", 0.015),
                                                                          ("Term", 7)]},

                 "SeniorNotes":           {"FundingControlSpecification": ("EBITDA_Turns", 1.91),
                                           "FinancingFeeProjection":     [("Fee_as_Percent_of_Funded_Amount", 0.01),
                                                                          ("Term", 8)]},

                 "SubordinatedNotes":     {"FundingControlSpecification": ("EBITDA_Turns", 0.00),
                                           "FinancingFeeProjection":     [("Fee_as_Percent_of_Funded_Amount", 0.00),
                                                                          ("Term", 0)]},

                 "PreferredStock":        {"FundingControlSpecification": ("EBITDA_Turns", 0.00)},

                 "ManagementRollover":    {"FundingControlSpecification": ("EBITDA_Turns", 0.00)}}

# FINANCING & TRANSACTIONAL FEES OF LBO

transactionFee = (0.02 * mre_TargetEquityValue)
financingFees = pd.DataFrame(columns=["Funding_Source", "Fee_as_Percent_of_Funded_Amount", "Fee_Amount",
                                      "Term", "Amortized_Amount_per_Year"])
financingFees.set_index("Funding_Source", inplace=True)

for source in list(inputtedFunds.keys()):
    fundingProjectionMethod = inputtedFunds[source]["FundingControlSpecification"][0]
    value = inputtedFunds[source]["FundingControlSpecification"][1]
    if(fundingProjectionMethod == "EBITDA_Turns"):
        sourcesOfFunding.at[source, "EBITDA_Turns"] = value
        sourcesOfFunding.at[source, "InvestedAmount"] = (value * mre_LTM_EBITDA_Assumption)
    elif(fundingProjectionMethod == "InvestedAmount"):
        sourcesOfFunding.at[source, "InvestedAmount"] = value
        sourcesOfFunding.at[source, "EBITDA_Turns"] = (value / mre_LTM_EBITDA_Assumption)

    if("FinancingFeeProjection" in list(inputtedFunds[source].keys())):
        feeProjectionControlSpecs = inputtedFunds[source]["FinancingFeeProjection"]
        for specification in feeProjectionControlSpecs:
            if (specification[0] == "Fee_as_Percent_of_Funded_Amount"):
                feeRate = specification[1]
                feeAmount = (feeRate * sourcesOfFunding.at[source, "InvestedAmount"])
            elif (specification[0] == "Fee_Amount"):
                feeAmount = specification[1]
                feeRate = (feeAmount / sourcesOfFunding.at[source, "InvestedAmount"])
            financingFees.at[source, "Fee_as_Percent_of_Funded_Amount"] = feeRate
            financingFees.at[source, "Fee_Amount"] = feeAmount
        for specification in feeProjectionControlSpecs:
            term, amortizationPerPeriod = 0, 0
            if (specification[0] == "Term"):
                term = specification[1]
                try:
                    amortizationPerPeriod = (financingFees.at[source, "Fee_Amount"] / term)
                except ZeroDivisionError:
                    amortizationPerPeriod = 0.000
            elif (specification[0] == "Amortized_Amount_per_Year"):
                amortizationPerPeriod = specification[1]
                try:
                    term = (financingFees.at[source, "Fee_Amount"] / amortizationPerPeriod)
                except ZeroDivisionError:
                    term = 0.000
            financingFees.at[source, "Term"] = term
            financingFees.at[source, "Amortized_Amount_per_Year"] = amortizationPerPeriod
    else:
        continue

sourcesOfFunding.at["SponsorEquity", "InvestedAmount"] = (sum(usesOfFunding["Amount"]) - sum(sourcesOfFunding["InvestedAmount"]))
sourcesOfFunding.at["SponsorEquity", "EBITDA_Turns"] = (sourcesOfFunding.at["SponsorEquity", "InvestedAmount"] / mre_LTM_EBITDA_Assumption)

print(usesOfFunding)
print(sourcesOfFunding)
print(financingFees["Fee_Amount"])



#
# def setupAlternatingDriverTable(variables=None, functionalForms=None, coordinated_IO_Flow=None):
#     solvableTerms = list(functionalForms.keys())
#     cols = solvableTerms
#     cols.append("Item")
#     table = pd.DataFrame(columns=cols)
#     table.set_index("Item", inplace=True)
#     for task in coordinated_IO_Flow:
#         key = list(task.keys())
#         input = task[key[1][1]]
#         inputID = task[key[1][0]]
#         table.at[task[key[0]], inputID] = input
#         for termToSolve in solvableTerms:
#             if(termToSolve == inputID):
#                 continue
#             else:
#                 calculatedOutput = solvableTerms[termToSolve]
#                 table.at[task[key[0]], termToSolve] = calculatedOutput
#     return table
#
# mre_LTM_EBITDA_Assumption = 5
# investedAmount = 5
# mre_EBITDA_Turns = 5
#
# elements = [
#                            {"InstanceID": "ExcessCash",
#                            "Input": ("InvestedAmount", max((mrp_CashBalance - mre_MINIMUM_CASH_BALANCE_DESIRED), 0))},
#
#                            {"InstanceID": "Revolver",
#                            "Input": ("EBITDA_Turns", 0.00)},
#
#                            {"InstanceID": "TermLoanA",
#                             "Input": ("EBITDA_Turns", 3.64)},
#
#                            {"InstanceID": "TermLoanB",
#                             "Input": ("EBITDA_Turns", 1.14)},
#
#                            {"InstanceID": "SeniorNotes",
#                             "Input": ("EBITDA_Turns", 1.91)},
#
#                            {"InstanceID": "SubordinatedNotes",
#                             "Input": ("EBITDA_Turns", 1.91)},
#
#                            {"InstanceID": "PreferredStock",
#                             "Input": ("EBITDA_Turns", 0.00)},
#
#                            {"InstanceID": "ManagementRollover",
#                             "Input": ("EBITDA_Turns", 0.00)}]
#
# outputtedTable = setupAlternatingDriverTable(variables=[mre_LTM_EBITDA_Assumption, mre_EBITDA_Turns, investedAmount],
#                                              functionalForms={"EBITDA_Turns": investedAmount / mre_LTM_EBITDA_Assumption,
#                                                               "InvestedAmount": mre_EBITDA_Turns * mre_LTM_EBITDA_Assumption},
#                                              coordinated_IO_Flow=elements)