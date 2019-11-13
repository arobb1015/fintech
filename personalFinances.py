import pandas as pd
import math
import matplotlib.pyplot as plt
import csv

def calcLivingExpenses(csvFile):
    with open(csvFile, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        i = 0
        for row in reader:
            i+=1
        groceriesAnalysis = pd.DataFrame(index=range(i),
                                         columns=['Item', 'StandardOrderQty', 'UnitPrice', 'UnitServings', 'ServingSize',
                                                  'ServingMetric', 'CaloriesPerServing', 'Carbs', 'Sugar', 'Fiber',
                                                  'Fat', 'Protein', 'ServingsConsumedPerDay', 'DaysUntilDepletion',
                                                  '%CoverageWithinMonth', 'EstimatedMonthlyExpense'])
        i = 0
        for row in reader:
            print(row['Item'], row['NumUnits'], row['UnitPrice'], row['UnitServings'], row['ServingSize'])
            groceriesAnalysis.at[i, 'Item'] = row['Item']
            groceriesAnalysis.at[i, 'StandardOrderQty'] = row['NumUnits']
            groceriesAnalysis.at[i, 'UnitPrice'] = row['UnitPrice']
            groceriesAnalysis.at[i, 'UnitServings'] = row['UnitServings']
            groceriesAnalysis.at[i, 'ServingSize'] = row['ServingSize']
            groceriesAnalysis.at[i, 'ServingMetric'] = row['ServingMetric']
            groceriesAnalysis.at[i, 'CaloriesPerServing'] = row['Calories']
            groceriesAnalysis.at[i, 'Carbs'] = row['Carbs']
            groceriesAnalysis.at[i, 'Sugar'] = row['Sugar']
            groceriesAnalysis.at[i, 'Fiber'] = row['Fiber']
            groceriesAnalysis.at[i, 'Fat'] = row['Fat']
            groceriesAnalysis.at[i, 'Protein'] = row['Protein']
            groceriesAnalysis.at[i, 'ServingsConsumedPerDay'] = row['ServingsConsumedPerDay']
            daysUntilDepletion = row['NumUnits'] * round(1/(row['ServingsConsumedPerDay'] / row['UnitServings']), 3)
            groceriesAnalysis.at[i, 'DaysUntilDepletion'] = daysUntilDepletion
            coverageWithinMonth = round((daysUntilDepletion / 30.458), 3)
            groceriesAnalysis.at[i, '%CoverageWithinMonth'] = round(100 * coverageWithinMonth, 3)
            estimatedMonthlyExpense = round(row['UnitPrice'] * row['NumUnits'] * (1 / coverageWithinMonth), 3)
            groceriesAnalysis.at[i, 'EstimatedMonthlyExpense'] = estimatedMonthlyExpense
            i+=1
        return groceriesAnalysis

def defineLoanTerms(borrowedAmount, apr, duration):

    loanAnalysis = pd.DataFrame(index=range(duration*12),
                                columns=['Year','Month','BoP_AccruedInterest', 'BoP_Principal', 'BoP_Balance', 'Payment',
                                         'EoP_AmtAppliedTowardInterest', 'EoP_AmtAppliedTowardPrincipal', 'EoP_Balance',
                                         'APR','Duration'])

    for i in range(0,len(loanAnalysis)):
        loanAnalysis.at[i, 'Month'] = i
        loanAnalysis.at[i, 'APR'] = apr
        loanAnalysis.at[i, 'Duration'] = duration
    #We assume the loan is DISBURSED ON THE 1st DAY OF THE 1st MONTH
    #We assume that starting in the very 1st month, INTEREST ACCRUES DAILY
    #We assume that the very 1st PAYMENT OCCURS ON 1st DAY OF THE 2nd MONTH
    loanAnalysis.at[0,'BoP_AccruedInterest'] = 0
    loanAnalysis.at[0,'BoP_Principal'] = borrowedAmount
    loanAnalysis.at[0,'BoP_Balance'] = borrowedAmount
    loanAnalysis.at[0,'Payment'] = 0
    loanAnalysis.at[0,'EoP_AmtAppliedTowardInterest'] = 0
    loanAnalysis.at[0,'EoP_AmtAppliedTowardPrincipal'] = 0

    dailyInterestRate = ((apr/100)/365)
    accruedInterest = 30 * (dailyInterestRate * loanAnalysis.at[0,'BoP_Balance'])
    loanAnalysis.at[0,'EoP_Balance'] = round(accruedInterest + loanAnalysis.at[0,'BoP_Balance'],2)

    loanAnalysis.at[1,'BoP_AccruedInterest'] = round(accruedInterest,2)
    loanAnalysis.at[1,'BoP_Principal'] = borrowedAmount
    loanAnalysis.at[1,'BoP_Balance'] = loanAnalysis.at[0,'EoP_Balance']

    return loanAnalysis

def processLoanPayment(loanInformation, currentPeriod, payment):

    loanDataFrame = loanInformation
    duration = loanDataFrame.at[0,'Duration']

    currentAccruedInterest = loanDataFrame.at[currentPeriod,'BoP_AccruedInterest']
    currentPrincipalBalance = loanDataFrame.at[currentPeriod,'BoP_Principal']
    currentTotalBalance  = loanDataFrame.at[currentPeriod,'BoP_Balance']

    loanDataFrame.at[currentPeriod,'Payment'] = payment

    if(payment >= currentAccruedInterest): #We need this condition because at the very least, we must pay interest
        loanDataFrame.at[currentPeriod,'EoP_AmtAppliedTowardInterest'] = currentAccruedInterest
        loanDataFrame.at[currentPeriod,'EoP_AmtAppliedTowardPrincipal'] = payment - currentAccruedInterest
        loanDataFrame.at[currentPeriod,'EoP_Balance'] = currentTotalBalance - payment

        #testCondition = loanDataFrame.at[currentPeriod,'EoP_Balance']
        #print(testCondition)
        if(loanDataFrame.at[currentPeriod,'EoP_Balance'] <= 0.00):
            print("The loan has been fully serviced! Any excess payments will be remitted.")
            return (True, loanInformation, currentPeriod)
        else:
            apr = loanDataFrame.at[0, 'APR']
            dailyInterestRate = ((apr/100)/365)
            accruedInterest = 30 * (dailyInterestRate * loanDataFrame.at[currentPeriod,'EoP_Balance'])

            whichPeriodToResume = (currentPeriod + 1)
            loanDataFrame.at[whichPeriodToResume, 'BoP_AccruedInterest'] = round(accruedInterest,2)
            loanDataFrame.at[whichPeriodToResume, 'BoP_Principal'] = round(loanDataFrame.at[currentPeriod,'EoP_Balance'],2)
            loanDataFrame.at[whichPeriodToResume, 'BoP_Balance'] = round(accruedInterest + loanDataFrame.at[whichPeriodToResume, 'BoP_Principal'],2)

    return (False, loanInformation, whichPeriodToResume)

def verifyOutstandingDebt(debtInformation, monthlyDebtPayment, dateOfPayment = 1):

    for i in range(0, 12):
        #print("Month #",i)
        remainingDebt = processLoanPayment(debtInformation, dateOfPayment, monthlyDebtPayment)
        if (remainingDebt[0] is True):
            debtHasBeenServiced = True
            studentLoans = remainingDebt[1]
            dateOfPayment = remainingDebt[2]
            break
        else:
            debtHasBeenServiced = False
            studentLoans = remainingDebt[1]
            dateOfPayment = remainingDebt[2]

    #print(remainingDebt[1])
    return (debtHasBeenServiced, studentLoans, dateOfPayment)

def calcRequiredMonthlyPayment(debtPrincipal, debtIR, debtDuration, desiredDuration, preallocation):
    debtIR = (debtIR/100)
    expectedMonthlyPayment = (debtPrincipal * (debtIR / 12)) / (1 - ((1 + (debtIR / 12)) ** (-12 * debtDuration)))
    expectedMonthlyPayment = round(expectedMonthlyPayment, 2)

    capableTerm = -((math.log((-(((debtPrincipal*debtIR)/preallocation)-12))/12)) / (12 * math.log((12+debtIR)/12)))
    capableTerm = round(capableTerm, 2)
    minTime = capableTerm

    print("\nREQUIRED Monthly payment is: $", expectedMonthlyPayment)
    print("PLANNED Monthly payment is: $", preallocation)

    timeReduction = round(100*((capableTerm - debtDuration)/debtDuration),2)
    temp = ''
    if(timeReduction > 0):
        temp = 'EXTENDED'
    else:
        temp = 'REDUCED'
    timeReduction = math.fabs(timeReduction)
    paymentRatio = round(100*preallocation/expectedMonthlyPayment,2)
    print("With a planned payment of $",preallocation,"(",paymentRatio,"% of required payment), "
          "the time required would be",temp,"by", timeReduction,"%")

    neededPaymentToMeetTimeGoal = (debtPrincipal * (debtIR / 12)) / (1 - ((1 + (debtIR / 12)) ** (-12 * desiredDuration)))
    neededPaymentToMeetTimeGoal = round(neededPaymentToMeetTimeGoal,2)
    neededTimeReductionFromStatedTerm = round(math.fabs(100*(1-(1/(debtDuration/desiredDuration)))), 2)

    print("In order to service the debt within a desired time constraint of",desiredDuration,"years, the MINIMUM "
           "required monthly payment\nwould have to be $",neededPaymentToMeetTimeGoal,". This would yield a",
          neededTimeReductionFromStatedTerm, "% time reduction from the stated",debtDuration,"year term of the debt.\n")

    x = []
    y = []
    preallocation = expectedMonthlyPayment
    for q in range(0,900):
        paymentRatio = round(100*preallocation/expectedMonthlyPayment,2)
        capableTerm = -((math.log((-(((debtPrincipal * debtIR) / preallocation) - 12)) / 12)) / (
                    12 * math.log((12 + debtIR) / 12)))
        capableTerm = round(capableTerm, 2)
        timeReduction = math.fabs( round(100 * ((capableTerm - debtDuration) / debtDuration), 2) )

        x.append(paymentRatio)
        y.append(timeReduction)
        preallocation += 10.0

    fig = plt.figure()
    fig.suptitle('Nonlinear Effect of Repayment Magnitude on Service Duration', fontsize=14)
    ax1 = fig.add_subplot(111)
    ax1.grid(True)
    ax1.scatter(x,y)
    ax1.set_ylim(0,108)
    ax1.set_title('DebtTerm = '+str(debtDuration)+" years @ "+str(debtIR*100)+"% IR")
    ax1.set_ylabel('% Time Reduction in Payoff')
    ax1.set_xlabel('Payment Ratio = (PlannedPMT / RequiredPMT)')
    # for i,j in zip(x,y):
    #     ax1.annotate(str(j), xy=(i,j))

    #plt.show()
    return expectedMonthlyPayment, neededPaymentToMeetTimeGoal, minTime

def calcAsFractionOfMonthlyIncome(disposableIncome, monthlyAllocationFigure):
    biweeklyPay = round(disposableIncome / 26, 2)
    neededProportionOfMonthlyIncome = round(100*(monthlyAllocationFigure / (2 * biweeklyPay)),2)

    print("A monthly payment of $", monthlyAllocationFigure, "would entail a",
           neededProportionOfMonthlyIncome, "% allocation of the BASELINE year's monthly income.\n")
    return neededProportionOfMonthlyIncome

def simulatePostGradLife(startingIncome, annualRaiseRate, scope, debtBurden, presetIncomeAllocations, incrementalIncomeFreedom,
                         proportionalRepayment):
    earnedIncome = startingIncome
    allocationForCHECKING = presetIncomeAllocations[0]
    allocationForLOANS = presetIncomeAllocations[1]
    allocationForINVESTMENTS = presetIncomeAllocations[2]
    splitTowardCHECKING = incrementalIncomeFreedom[0]
    splitTowardINVESTING = incrementalIncomeFreedom[1]

    if(proportionalRepayment is True):
        schoolLoansAreRepaidAsFixedProportionOfIncome = True
    elif(proportionalRepayment is False):
        schoolLoansAreRepaidAsFixedProportionOfIncome = False
    taxRate = 25.0  # percent tax incidence
    startingBoP = 2020
    studentLoans = debtBurden
    debtHasBeenServiced = False

    simulationOutput = pd.DataFrame(index=range(scope),
                                    columns=['Year', 'DisposableIncome', 'BiweeklyPay',
                                             '%Contrib_CHECKING',
                                             '$Contrib_CHECKING',  # MONTHLY ALLOWANCE FOR CHECKING
                                             '%Contrib_SCHOOL_LOANS',
                                             '$Contrib_SCHOOL_LOANS',  # MONTHLY LOAN PAYMENT
                                             '%Contrib_CARPAY',
                                             '$Contrib_CARPAY',
                                             '%Contrib_INVEST',
                                             '$Contrib_INVEST',
                                             'SavedThusFar',
                                             'HoldingsAfterROI',
                                             'sumToOneCHECK'])

    #schoolLoansAreRepaidAsFixedProportionOfIncome = False
    for x in range(0, scope):
        print("BEGINNING Year #", x)
        simulationOutput.at[x, 'Year'] = (startingBoP + x)
        if (x is 0):
            simulationOutput.at[x, 'DisposableIncome'] = round(earnedIncome * (1 - (taxRate / 100)), 2)
            simulationOutput.at[x, 'BiweeklyPay'] = round(simulationOutput.at[x, 'DisposableIncome'] / 26, 2)

            simulationOutput.at[x, '%Contrib_SCHOOL_LOANS'] = allocationForLOANS

            monthlyLoanPayment = allocationForLOANS * simulationOutput.at[x, 'BiweeklyPay'] * 2
            simulationOutput.at[x, '$Contrib_SCHOOL_LOANS'] = monthlyLoanPayment

            studentLoans = verifyOutstandingDebt(studentLoans, monthlyLoanPayment, dateOfPayment=1)

            if(studentLoans[0] is True):
                #If this condition is triggered, then we know that the debt has been FULLY SERVICED
                simulationOutput.at[x, '%Contrib_SCHOOL_LOANS'] = 0.0
                simulationOutput.at[x, '$Contrib_SCHOOL_LOANS'] = 0.0

            else:
                wherePaymentsLeftOff = studentLoans[2]

            simulationOutput.at[x, '%Contrib_CHECKING'] = round(allocationForCHECKING,3)
            simulationOutput.at[x, '$Contrib_CHECKING'] = round(allocationForCHECKING * simulationOutput.at[x, 'BiweeklyPay'] * 2,2)
            simulationOutput.at[x, '%Contrib_INVEST'] = round(allocationForINVESTMENTS,3)
            simulationOutput.at[x, '$Contrib_INVEST'] = round(allocationForINVESTMENTS * simulationOutput.at[x, 'BiweeklyPay'] * 2,2)
            savedThusFar = (12 * simulationOutput.at[x, '$Contrib_INVEST'])
            simulationOutput.at[x, 'SavedThusFar'] = savedThusFar
            simulationOutput.at[x, 'HoldingsAfterROI'] = savedThusFar*(1.035)

            allocationForCARPAYMENTS = (1 - allocationForCHECKING - allocationForLOANS - allocationForINVESTMENTS)
            simulationOutput.at[x, '%Contrib_CARPAY'] = round(allocationForCARPAYMENTS,3)
            simulationOutput.at[x, '$Contrib_CARPAY'] = round(allocationForCARPAYMENTS * simulationOutput.at[x, 'BiweeklyPay'] * 2,2)

        if (x > 0):
            earnedIncome = round(earnedIncome * (1 + annualRaiseRate / 100), 2)
            simulationOutput.at[x, 'DisposableIncome'] = round(earnedIncome * (1 - (taxRate / 100)), 2)
            simulationOutput.at[x, 'BiweeklyPay'] = round(simulationOutput.at[x, 'DisposableIncome'] / 26, 2)

            if(schoolLoansAreRepaidAsFixedProportionOfIncome is True):
                allocationForLOANS = simulationOutput.at[0, '%Contrib_SCHOOL_LOANS']
                simulationOutput.at[x, '%Contrib_SCHOOL_LOANS'] = allocationForLOANS
                monthlyLoanPayment = round(allocationForLOANS * (2 * simulationOutput.at[x, 'BiweeklyPay']), 2)
                simulationOutput.at[x, '$Contrib_SCHOOL_LOANS'] = monthlyLoanPayment

                if(studentLoans[0] is True):
                    # If this condition is triggered, then we know that the debt has been FULLY SERVICED
                    incrementFreed = simulationOutput.at[x-1, '%Contrib_SCHOOL_LOANS']
                    simulationOutput.at[x, '%Contrib_SCHOOL_LOANS'] = 0.00
                else:
                    wherePaymentsLeftOff = studentLoans[2]
                    studentLoans = verifyOutstandingDebt(studentLoans[1], monthlyLoanPayment, dateOfPayment=wherePaymentsLeftOff)
                    incrementFreed = 0.00

            elif(schoolLoansAreRepaidAsFixedProportionOfIncome is False):
                monthlyLoanPayment = simulationOutput.at[0, '$Contrib_SCHOOL_LOANS']
                simulationOutput.at[x, '$Contrib_SCHOOL_LOANS'] = monthlyLoanPayment
                allocationForLOANS = monthlyLoanPayment / (2 * simulationOutput.at[x, 'BiweeklyPay'])
                simulationOutput.at[x, '%Contrib_SCHOOL_LOANS'] = round(allocationForLOANS,3)

                if(studentLoans[0] is True):
                    #If this condition is triggered, then we know that the debt has been FULLY SERVICED
                    simulationOutput.at[x, '%Contrib_SCHOOL_LOANS'] = 0.00
                    simulationOutput.at[x, '$Contrib_SCHOOL_LOANS'] = 0.00
                else:
                    wherePaymentsLeftOff = studentLoans[2]
                    studentLoans = verifyOutstandingDebt(studentLoans[1], monthlyLoanPayment, dateOfPayment = wherePaymentsLeftOff)
                    incrementFreed = simulationOutput.at[x - 1, '%Contrib_SCHOOL_LOANS'] \
                                     - simulationOutput.at[x, '%Contrib_SCHOOL_LOANS']

            #df = studentLoans[1]
            #print(df['Payments'])

            allocationForINVESTMENTS = (incrementFreed * splitTowardINVESTING) + simulationOutput.at[x - 1, '%Contrib_INVEST']
            allocationForCHECKING = (incrementFreed * splitTowardCHECKING) + simulationOutput.at[x - 1, '%Contrib_CHECKING']

            simulationOutput.at[x, '%Contrib_INVEST'] = round(allocationForINVESTMENTS,3)
            simulationOutput.at[x, '$Contrib_INVEST'] = round(allocationForINVESTMENTS * (2 * simulationOutput.at[x, 'BiweeklyPay']),2)
            savedThusFar = (12 * simulationOutput.at[x, '$Contrib_INVEST']) + simulationOutput.at[x - 1, 'SavedThusFar']
            simulationOutput.at[x, 'SavedThusFar'] = savedThusFar

            simulationOutput.at[x, 'HoldingsAfterROI'] = savedThusFar*1.035

            simulationOutput.at[x, '%Contrib_CHECKING'] = round(allocationForCHECKING,3)
            simulationOutput.at[x, '$Contrib_CHECKING'] = round(allocationForCHECKING * (2 * simulationOutput.at[x, 'BiweeklyPay']),2)

            allocationForCARPAYMENTS = (1 - allocationForCHECKING - allocationForLOANS - allocationForINVESTMENTS)
            simulationOutput.at[x, '%Contrib_CARPAY'] = round(allocationForCARPAYMENTS,3)
            simulationOutput.at[x, '$Contrib_CARPAY'] = round(allocationForCARPAYMENTS * simulationOutput.at[x, 'BiweeklyPay'] * 2,2)

        simulationOutput.at[x, 'sumToOneCHECK'] = simulationOutput.at[x, '%Contrib_CHECKING'] + \
                                                  simulationOutput.at[x, '%Contrib_INVEST'] + \
                                                  simulationOutput.at[x, '%Contrib_SCHOOL_LOANS'] + \
                                                  simulationOutput.at[x, '%Contrib_CARPAY']


    #print(simulationOutput['$Contrib_INVEST'])
    print(simulationOutput['SavedThusFar'])

    # print(simulationOutput['%Contrib_CHECKING'],'\n',simulationOutput['%Contrib_SCHOOL_LOANS'],'\n',
    #       simulationOutput['%Contrib_INVEST'],'\n',simulationOutput['%Contrib_CARPAY'],'\n')
    return simulationOutput, studentLoans[1]


expenses = calcLivingExpenses('listOfGoods.csv')
#print(expenses)


'''
If disposable income rises each year, and loan repayments are held constant, then the proportion of income that's
directed toward repayment will gradually become smaller as time goes on. The year-over-year difference in this fraction
of income is called the INCREMENT-FREED. It represents the proportion of income that has become available for other uses
Each year the INCREMENT-FREED is used to direct more income to both INVESTING & CHECKING. The split is defined by the
FREED-INCOME SPLIT rules.
'''

#Simulation Settings
scope = 12#years
earnedIncome = 65000#dollars
annualRaiseRate = 3.5#percent
termsOfDebt = (100000, 9.1, 15)
collegeDebt = defineLoanTerms(termsOfDebt[0], termsOfDebt[1], termsOfDebt[2])
idealServicingDuration = 6#years
splitTowardCHECKING = 0.35
splitTowardINVESTING = 0.65
incrementalIncomeFreedom = (splitTowardCHECKING, splitTowardINVESTING)
allocationForCHECKING = 0.50
allocationForDEBT_PMT = 0.4495 #0.3706
allocationForINVESTING = 0.0505
initialAllocations = (allocationForCHECKING, allocationForDEBT_PMT, allocationForINVESTING)

debtDuration = termsOfDebt[2]
maxPaymentTowardDebt = (0.899 * allocationForCHECKING * (1-0.25) * (65000/26) * 2)
reqPMT, idealPMT, capableTerm = calcRequiredMonthlyPayment(termsOfDebt[0], termsOfDebt[1], termsOfDebt[2],
                                                           debtDuration, maxPaymentTowardDebt)
print("If the allocation for debt repayment is set to",round(100 * 0.899 * allocationForCHECKING,2),"% then the debt "
      "can be serviced within",round(capableTerm,2),"years.")


fixdREPMTresults, debtServicing1 = simulatePostGradLife(earnedIncome, annualRaiseRate, scope, collegeDebt, initialAllocations,
                                        incrementalIncomeFreedom, False)
propREPMTresults, debtServicing2 = simulatePostGradLife(earnedIncome, annualRaiseRate, scope, collegeDebt, initialAllocations,
                                        incrementalIncomeFreedom, True)

# for x in range(0, len(debtServicing1)):
#     print(debtServicing1.at[x, 'Month'], "  ", debtServicing1.at[x, 'BoP_Principal'], "  ",
#           debtServicing1.at[x, 'BoP_Balance'], "  ", debtServicing1.at[x, 'Payment'], "  ",
#           debtServicing1.at[x, 'EoP_AmtAppliedTowardInterest'], "  ", debtServicing1.at[x, 'EoP_AmtAppliedTowardPrincipal'], "  ",
#           debtServicing1.at[x, 'EoP_Balance'])
# totalPaidInInterest = round(debtServicing1['EoP_AmtAppliedTowardInterest'].sum(),2)
# print("You paid $",totalPaidInInterest," in interest!")

# count = 1
# for q in range(count,9):
#     nameOfPanel = 'ax'+str(count)
#     panelAssignment = nameOfPanel+'fig.add_subplot(42'+str(count)+')'
#     barChartAssignment = "coordinatesForBarChart = "+nameOfPanel+".bar(fixdREPMTresults['Year'], fixdREPMTresults['DisposableIncome'])"
#     eval(nameOfPanel+".set_xlabel('Year')")
#
# eval(nameOfPanel + ".set_title('Biweekly Pay')")
# eval(nameOfPanel + ".set_ylabel('Dollar Income')")

# fig = plt.figure()
# fig.suptitle('Dashboard Controls', fontsize=20)
#
# ax1 = fig.add_subplot(421)
# coordinatesForBarChart = ax1.bar(fixdREPMTresults['Year'], fixdREPMTresults['DisposableIncome'])
# ax1.set_title('Biweekly Pay')
# ax1.set_ylabel('Dollar Income')
# ax1.set_xlabel('Year')
# for i in ax1.patches:
#     # get_x pulls left or right; get_height pushes up or down
#     ax1.text(i.get_x()-.03, i.get_height()+.5, '$'+str(round(  i.get_height(), 2)), fontsize=8, color='black')
#
# ax2 = fig.add_subplot(422)
# coordinatesForBarChart = ax2.bar(fixdREPMTresults['Year'], fixdREPMTresults['BiweeklyPay'])
# ax2.set_title('Biweekly Pay')
# ax2.set_ylabel('Dollar Income')
# ax2.set_xlabel('Year')
# for i in ax2.patches:
#     # get_x pulls left or right; get_height pushes up or down
#     ax2.text(i.get_x()-.03, i.get_height()+.5, '$'+str(round(  i.get_height(), 2)), fontsize=8, color='black')
#
# ax3 = fig.add_subplot(423)
# coordinatesForBarChart = ax3.bar(fixdREPMTresults['Year'], fixdREPMTresults['$Contrib_INVEST'])
# ax3.set_title('Funds for Investing (Fixed RePMT)')
# ax3.set_ylabel('Monthly Allocation')
# ax3.set_xlabel('Year')
# for i in ax3.patches:
#     # get_x pulls left or right; get_height pushes up or down
#     ax3.text(i.get_x()-.03, i.get_height()+.5, '$'+str(round(  i.get_height(), 2)), fontsize=8, color='black')
#
# ax4 = fig.add_subplot(424)
# coordinatesForBarChart = ax4.bar(propREPMTresults['Year'], propREPMTresults['$Contrib_INVEST'])
# ax4.set_title('Funds for Investing (Proportional RePMT)')
# ax4.set_ylabel('Monthly Allocation')
# ax4.set_xlabel('Year')
# for i in ax4.patches:
#     # get_x pulls left or right; get_height pushes up or down
#     ax4.text(i.get_x()-.03, i.get_height()+.5, '$'+str(round(  i.get_height(), 2)), fontsize=8, color='black')
#
# ax5 = fig.add_subplot(425)
# coordinatesForBarChart = ax5.bar(fixdREPMTresults['Year'], fixdREPMTresults['SavedThusFar'])
# ax5.set_title('Cumulative Savings (Fixed RePMT)')
# ax5.set_ylabel('Value of Holdings')
# ax5.set_xlabel('Year')
# for i in ax5.patches:
#     # get_x pulls left or right; get_height pushes up or down
#     ax5.text(i.get_x()-.03, i.get_height()+.5, '$'+str(round(  i.get_height(), 2)), fontsize=8, color='black')
#
# ax6 = fig.add_subplot(426)
# coordinatesForBarChart = ax6.bar(propREPMTresults['Year'], propREPMTresults['SavedThusFar'])
# ax6.set_title('Cumulative Savings (Proportional RePMT)')
# ax6.set_ylabel('Value of Holdings')
# ax6.set_xlabel('Year')
# for i in ax6.patches:
#     # get_x pulls left or right; get_height pushes up or down
#     ax6.text(i.get_x()-.03, i.get_height()+.5, '$'+str(round(  i.get_height(), 2)), fontsize=8, color='black')
#
# ax7 = fig.add_subplot(427)
# coordinatesForBarChart = ax7.bar(fixdREPMTresults['Year'], fixdREPMTresults['$Contrib_CHECKING'])
# ax7.set_title('Funds for Living Expenses (Fixed RePMT)')
# ax7.set_ylabel('Monthly Allocation')
# ax7.set_xlabel('Year')
# for i in ax7.patches:
#     # get_x pulls left or right; get_height pushes up or down
#     ax7.text(i.get_x()-.03, i.get_height()+.5, '$'+str(round(  i.get_height(), 2)), fontsize=8, color='black')
#
# ax8 = fig.add_subplot(428)
# coordinatesForBarChart = ax8.bar(propREPMTresults['Year'], propREPMTresults['$Contrib_CHECKING'])
# ax8.set_title('Funds for Living Expenses (Proportional RePMT)')
# ax8.set_ylabel('Monthly Allocation')
# ax8.set_xlabel('Year')
# for i in ax8.patches:
#     # get_x pulls left or right; get_height pushes up or down
#     ax8.text(i.get_x()-.03, i.get_height()+.5, '$'+str(round(  i.get_height(), 2)), fontsize=12, color='black')
#
# plt.show()




# ax1 = fig.add_subplot(321)
# x = output['Year']
# y = output['$Contrib_INVEST']
# ax1.plot(x,y)
# ax1.set_ylim(output['$Contrib_INVEST'].min(),output['$Contrib_INVEST'].max()*1.05)
# ax1.set_title('Dollar Contribution toward Investments')
# ax1.set_ylabel('Monthly Allocation')
# ax1.set_xlabel('Year')
# for i,j in zip(x,y):
#     ax1.annotate(str(j), xy=(i,j))