import random
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

creditRatingsByRatioRange = {(8.5, 'INF'): 'AAA',
                             (6.5, 8.5): 'AA',
                             (5.5, 6.5): 'A+',
                             (4.25, 5.5): 'A',
                             (3.0, 4.25): 'A-',
                             (2.5, 3.0): 'BBB',
                             (2.25, 2.5): 'BB+',
                             (2.0, 2.25): 'BB',
                             (1.75, 2.0): 'B+',
                             (1.5, 1.75): 'B',
                             (1.25, 1.5): 'B-',
                             (0.8, 1.25): 'CCC',
                             (0.65, 0.8): 'CC',
                             (0.2, 0.65): 'C',
                             ('-INF', 0.2): 'D'}

defaultSpreadsByCreditRating = {'AAA': 1.25,
                                'AA': 1.75,
                                'A+': 2.25,
                                'A': 2.5,
                                'A-': 3.0,
                                'BBB': 3.5,
                                'BB+': 4.25,
                                'BB': 5.0,
                                'B+': 6.0,
                                'B': 7.25,
                                'B-': 8.5,
                                'CCC': 10.0,
                                'CC': 12.0,
                                'C': 15.0,
                                'D': 20.0}

def identifyDefaultSpread(firmsInterestCovRatio, riskFreeRate, creditRatingsByRatioRange, defaultSpreadsByCreditRating):
    #This function is based on Damodaran's Ch.15

    #These two variables will be determined after searching through the Credit Rating Table
    firmsInterestCovRatio = round(firmsInterestCovRatio,3)
    firmsCreditRating = ''
    firmsDefaultSpread = 0
    listOfCreditRatioRanges = [*creditRatingsByRatioRange]
    print("The firm's coverage ratio is", firmsInterestCovRatio),
    for x in range(0, len(listOfCreditRatioRanges)):
        currentRangeBeingTested = listOfCreditRatioRanges[x]
        rangeForSpecificRating = currentRangeBeingTested
        lowerBound = rangeForSpecificRating[0]
        upperBound = rangeForSpecificRating[1]

        print("The current range being tested is",currentRangeBeingTested)
        #If a firm's ratio falls within a prescribed range, lookup the credit rating
        if(firmsInterestCovRatio is 'INF'):
            firmsCreditRating = 'AAA'
            firmsDefaultSpread = defaultSpreadsByCreditRating[firmsCreditRating]
            break
        elif(firmsInterestCovRatio is '-INF'):
            firmsCreditRating = 'D'
            firmsDefaultSpread = defaultSpreadsByCreditRating[firmsCreditRating]
            break
        elif(type(firmsInterestCovRatio) != str and
             (firmsInterestCovRatio > float(lowerBound) and firmsInterestCovRatio < float(upperBound))):

                firmsCreditRating = creditRatingsByRatioRange[currentRangeBeingTested]
                firmsDefaultSpread = defaultSpreadsByCreditRating[firmsCreditRating]
                break

    firmsPreTaxCostOfDebt = (firmsDefaultSpread + riskFreeRate)
    print("Given the firm's rating of",firmsCreditRating,", the spread should be",firmsDefaultSpread,";\n"
          "Thus the new PRE-TAX cost of debt will be updated: (",riskFreeRate," + ",firmsDefaultSpread,")")
    return firmsCreditRating, firmsPreTaxCostOfDebt

def releverBeta(unleveredBeta, marginalTaxRate, debtToEquityRatio):
    releveredBeta = unleveredBeta * (1 + (1-(marginalTaxRate/100)) * (debtToEquityRatio/100))
    return releveredBeta

def approxBetaOfDebt(inputtedCreditRating, marketRiskPremia, marketRiskInfluenceOnDefaultProbability):
    defaultSpread = defaultSpreadsByCreditRating[inputtedCreditRating]/100
    marketRiskPremia = marketRiskPremia/100
    betaOfDebt = (defaultSpread/marketRiskPremia)*(marketRiskInfluenceOnDefaultProbability/100)
    return betaOfDebt



def calcCostOfEquity(leveredBeta, riskFreeRate, inputDescriptor, input):

    riskFreeRate = riskFreeRate/100
    input = input/100

    if(inputDescriptor is 'PresetPremium'):
        presetEquityPremia = input
        costOfEquity = (riskFreeRate + (leveredBeta * presetEquityPremia))
    elif(inputDescriptor is 'MarketReturn'):
        marketReturn = input
        costOfEquity = (riskFreeRate + leveredBeta * (marketReturn-riskFreeRate))
    return costOfEquity

def calcWACC(debtLevel, afterTaxCostOfDebt, costOfEquity):

    wacc = (afterTaxCostOfDebt*(debtLevel/100) + costOfEquity*(1-(debtLevel/100)))
    return wacc

def optimizeCapitalStructure(fixedEBIT, marginalTaxRate, fixedRiskFreeRate, marketValDebt, marketValEquity,
                             unleveredBeta, marketPremium, debtHoldersRiskBurden = None, debtLevelIncrement=1):
    def accountForDebtHolderBurden(debtHoldersRiskBurden, firmsCreditRating, firmsDebtToEquity, leveredBeta,
                                   marketPremium, taxRate):
        if(debtHoldersRiskBurden != None and debtHoldersRiskBurden[0] is True):
            marketRiskInfluenceOnDefaultProbability = debtHoldersRiskBurden[1]
            betaOfDebt = approxBetaOfDebt(firmsCreditRating, marketPremium, marketRiskInfluenceOnDefaultProbability)
            leveredBeta = leveredBeta - (betaOfDebt * (1 - (taxRate / 100)) * firmsDebtToEquity)
            print("COCKCS")
        return leveredBeta

    firmDetails = pd.DataFrame(index=range(0,100,debtLevelIncrement),
                               columns=['DebtLevel', 'DebtToEquity', 'DollarDebt', 'InterestExpense','InterestCoverage',
                                        'CreditRating', 'PreTaxCostOfDebt', 'TaxRate', 'AfterTaxCostOfDebt',
                                        'LeveredBeta', 'CostOfEquity', 'WACC'])

    #Initial Conditions (when the firm is COMPLETELY UNLEVERED)
    marketValOfFirm = (marketValDebt + marketValEquity)
    #firmDetails.set_index('DebtLevel', inplace=True)
    firmDetails.at[0,'DebtLevel'] = 0.00
    firmDetails.at[0,'DebtToEquity'] = 0.00
    firmDetails.at[0,'DollarDebt'] = 0.00
    firmDetails.at[0,'InterestExpense'] = 0.00
    firmDetails.at[0,'InterestCoverage'] = 'INF'
    firmDetails.at[0,'CreditRating'] = 'AAA'
    firmDetails.at[0,'PreTaxCostOfDebt'] = defaultSpreadsByCreditRating[firmDetails.at[0,'CreditRating']]+fixedRiskFreeRate
    firmDetails.at[0,'TaxRate'] = marginalTaxRate
    firmDetails.at[0,'AfterTaxCostOfDebt'] = firmDetails.at[0,'PreTaxCostOfDebt'] * (1 - (marginalTaxRate / 100))
    firmDetails.at[0,'LeveredBeta'] = accountForDebtHolderBurden(debtHoldersRiskBurden,'AAA',0.00,unleveredBeta,marketPremium,marginalTaxRate)
    firmDetails.at[0,'CostOfEquity'] = 100*calcCostOfEquity(unleveredBeta, fixedRiskFreeRate, 'PresetPremium', marketPremium)
    firmDetails.at[0,'WACC'] = calcWACC(firmDetails.at[0,'DebtLevel'],
                                        firmDetails.at[0,'AfterTaxCostOfDebt'],
                                        firmDetails.at[0,'CostOfEquity'])

    prevCoverageRatio = firmDetails.at[0,'InterestCoverage']
    prevCreditRating = firmDetails.at[0,'CreditRating']
    prevPreTaxCostOfDebt = firmDetails.at[0,'PreTaxCostOfDebt']

    for x in range(debtLevelIncrement,100,debtLevelIncrement):
        print("TESTING @ ",x,"% debt level")
        currentDebtLevel = x
        firmDetails.at[x, 'DebtLevel'] = currentDebtLevel

        currentEquityLevel = (1-(x/100))*100
        currentDebtToEquityLevel = currentDebtLevel/currentEquityLevel
        firmDetails.at[x, 'DebtToEquity'] = currentDebtToEquityLevel

        currentDollarDebt = marketValOfFirm*(currentDebtLevel/100)
        firmDetails.at[x, 'DollarDebt'] = currentDollarDebt

        currentInterestExpense = currentDollarDebt*(prevPreTaxCostOfDebt/100)
        firmDetails.at[x, 'InterestExpense'] = currentInterestExpense

        currentCoverageRatio = fixedEBIT/currentInterestExpense
        firmDetails.at[x, 'InterestCoverage'] = round(currentCoverageRatio,3)

        newCreditRating, newPreTaxCostOfDebt = identifyDefaultSpread(currentCoverageRatio, fixedRiskFreeRate,
                                                                     creditRatingsByRatioRange,
                                                                     defaultSpreadsByCreditRating)
        while(newCreditRating != prevCreditRating):
            print("ALERT: The coverage ratio went from",prevCoverageRatio,"to",round(currentCoverageRatio,3),
                  "; this has caused the firm's credit rating to change from",prevCreditRating,"to",newCreditRating)
            prevCreditRating = newCreditRating
            currentInterestExpense = currentDollarDebt*(newPreTaxCostOfDebt/100)
            firmDetails.at[x, 'InterestExpense'] = currentInterestExpense

            currentCoverageRatio = fixedEBIT / currentInterestExpense
            firmDetails.at[x, 'InterestCoverage'] = round(currentCoverageRatio, 3)

            newCreditRating, newPreTaxCostOfDebt = identifyDefaultSpread(currentCoverageRatio, fixedRiskFreeRate,
                                                                         creditRatingsByRatioRange,
                                                                         defaultSpreadsByCreditRating)
        prevCoverageRatio = round(currentCoverageRatio,3)
        firmDetails.at[x, 'CreditRating'] = newCreditRating
        firmDetails.at[x, 'PreTaxCostOfDebt'] = newPreTaxCostOfDebt

        if(firmDetails.at[x, 'InterestExpense'] > fixedEBIT):
            maximumTaxBenefit = fixedEBIT*(marginalTaxRate/100)
            maxTaxBenefitAsProportionOfInterestExpense = (maximumTaxBenefit / firmDetails.at[x, 'InterestExpense'])
            marginalTaxRate = (100*maxTaxBenefitAsProportionOfInterestExpense)

        firmDetails.at[x, 'TaxRate'] = marginalTaxRate
        firmDetails.at[x, 'AfterTaxCostOfDebt'] = newPreTaxCostOfDebt*(1-(marginalTaxRate/100))

        releveredBeta = releverBeta(unleveredBeta, marginalTaxRate, (100*firmDetails.at[x, 'DebtToEquity']))
        firmDetails.at[x, 'LeveredBeta'] = accountForDebtHolderBurden(debtHoldersRiskBurden,
                                                                      firmDetails.at[x, 'CreditRating'],
                                                                      firmDetails.at[x, 'DebtToEquity'],
                                                                      releveredBeta, marketPremium, marginalTaxRate)
        firmDetails.at[x, 'CostOfEquity'] = 100*calcCostOfEquity(firmDetails.at[x, 'LeveredBeta'], fixedRiskFreeRate,
                                                                 'PresetPremium', 6.00)
        firmDetails.at[x, 'WACC'] = calcWACC(firmDetails.at[x,'DebtLevel'], firmDetails.at[x,'AfterTaxCostOfDebt'],
                                             firmDetails.at[x,'CostOfEquity'])
        prevPreTaxCostOfDebt = newPreTaxCostOfDebt
        prevCreditRating = newCreditRating
    print(firmDetails['WACC'])


firmsMostRecentlyAdjustedEBIT = 6829.00
marginalTaxRate = 38.0
riskFreeRate = 3.50
marketPremium = 6.00
firmsUnleveredBeta = 0.7333
debtHoldersBurden = (False, 25.0)
marketValueOfFirmsDebt = 16682
marketValueOfFirmsEquity = 45193.0
optimizeCapitalStructure(firmsMostRecentlyAdjustedEBIT, marginalTaxRate, riskFreeRate,
                         marketValueOfFirmsDebt, marketValueOfFirmsEquity, firmsUnleveredBeta, marketPremium)