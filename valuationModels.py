import random
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta
from matplotlib import colors
from matplotlib.widgets import MultiCursor
from matplotlib.ticker import PercentFormatter
from matplotlib import style
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from matplotlib import cm
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib import interactive
import matplotlib.widgets as mw
import matplotlib.gridspec as gridspec

def calcSTABLE_PE(stableGrowthRate, payoutRatio, costOfEquity):
    return ((payoutRatio*(1+stableGrowthRate))/(costOfEquity-stableGrowthRate))

def calcTwoStage_PE(growthRates, payoutRatios, costsOfEquity, duration):
    '''This function is based on the formulas from Damodaran's Ch18'''
    extraordinaryGrowthRate = (growthRates[0]/100)
    stableGrowthRate = (growthRates[1]/100)
    extraordinaryPayoutRatio = (payoutRatios[0]/100)
    stablePayoutRatio = (payoutRatios[1]/100)
    extraordinaryCostOfEquity = (costsOfEquity[0]/100)
    stableCostOfEquity = (costsOfEquity[1]/100)

    eStage = extraordinaryPayoutRatio*(1+extraordinaryGrowthRate)\
             *(1-(((1+extraordinaryGrowthRate)**duration)/((1+extraordinaryCostOfEquity)**duration)))
    eStage = eStage/(extraordinaryCostOfEquity - extraordinaryGrowthRate)


    sStage = (stablePayoutRatio*((1+extraordinaryGrowthRate)**duration)*(1+stableGrowthRate))\
             /((stableCostOfEquity-stableGrowthRate)*((1+extraordinaryCostOfEquity)**duration))

    return (eStage+sStage)

def calcCostOfEquity(riskFreeRate, beta, inputDescriptor, input):
    if(inputDescriptor is 'PresetPremium'):
        presetEquityPremia = input
        costOfEquity = (riskFreeRate+(beta*presetEquityPremia))
    elif(inputDescriptor is 'MarketReturn'):
        marketReturn = input
        costOfEquity = (riskFreeRate+beta*(marketReturn-riskFreeRate))
    return costOfEquity

def calcUnleveredBeta(leveredBeta, marketValueOfEquity, marketValueOfDebt, marginalTaxRate):
    debtToEquityRatio = (marketValueOfDebt/marketValueOfEquity)
    unleveredBeta = (leveredBeta/(1+debtToEquityRatio)*(1-(marginalTaxRate/100)))
    return unleveredBeta

def calcReleveredBeta(avgUnleveredBeta, targetDebtLevel, avgTaxRate):
    targetEquityLevel = (1 - (targetDebtLevel/100))
    debtToEquityRatio = ((targetDebtLevel/100)/targetEquityLevel)
    releveredBeta = (avgUnleveredBeta*(1+debtToEquityRatio)*(1-(avgTaxRate/100)))
    return releveredBeta

def calcWACC(targetDebtLevel, avgTaxRate, pretaxcostOfDebt, costOfEquity):
    targetEquityLevel = (1 - (targetDebtLevel/100))
    afterTaxCostofDebt = (pretaxcostOfDebt*(1-(avgTaxRate/100)))
    wacc = ((afterTaxCostofDebt*targetDebtLevel)+(costOfEquity*targetEquityLevel))
    return wacc

def calendarizeFigure(actualReportedValue, estimatedFutureValue, monthNumOfFYE):
    # Month Number of Firm's Fiscal Year End = monthNumFYE
    output = ((monthNumOfFYE*actualReportedValue)/12)+(((12-monthNumOfFYE)*estimatedFutureValue)/12)
    return output

def calcPayoutRatio(returnOnEquity, growthRate):
    retentionRatio = (growthRate/returnOnEquity)
    payoutRatio = (1 - retentionRatio)
    return payoutRatio

def valueRandomizer(distribution, inputA, inputB, inputC = None):

    randomNumber = 0
    if(distribution is 'UNIFORM'):
        lowerBound = inputA
        upperBound = inputB
        randomNumber = random.uniform(lowerBound, upperBound)
        randomNumber = round(randomNumber,3)
    elif(distribution is 'NORMAL'):
        specifiedMean = inputA
        specifiedVariance = inputB
        randomNumber = np.random.normal(specifiedMean, specifiedVariance)
    elif(distribution is' TRIANGULAR'):
        lowerBound = inputA
        upperBound = inputB
        mostLikelyValue = inputC
        mode = mostLikelyValue
        mean = (lowerBound+mostLikelyValue+upperBound)/3
        median = 0
        if(mode >= (lowerBound+upperBound)/2):
            median = lowerBound +math.sqrt(((upperBound-lowerBound)*(mode-lowerBound))/2)
        elif(mostLikelyValue <= (lowerBound+upperBound)/2):
            median = upperBound +math.sqrt(((upperBound-lowerBound)*(upperBound-mode))/2)
        print("Mean of Triangular(",lowerBound,mode,upperBound,") = ",mean)
        print("Median of Triangular(",lowerBound,mode,upperBound,") = ",median)

        randomNumber = np.random.triangular(lowerBound, mostLikelyValue, upperBound)
    elif(distribution is 'PERT'):
        lowerBound = inputA
        upperBound = inputB
        mostLikelyValue = inputC
        mode = mostLikelyValue

        alphaParam = (4*mostLikelyValue + upperBound - 5*lowerBound)/(upperBound-lowerBound)
        betaParam = (5*upperBound-lowerBound-4*mostLikelyValue)/(upperBound-lowerBound)

        intA = 0
        intB = 1

        #alphaParam = ((2*(intB + 4*mode - 5*intA))/(3*(intB-intA)))*(1+4(((mode-intA)*(intB-mode))/((intB-intA)**2)))
        #betaParam = ((2*(5*intB - 4*mode - intA))/(3*(intB-intA)))*(1+4(((mode-intA)*(intB-mode))/((intB-intA)**2)))

        mean, var, skew, kurt = beta.stats(alphaParam, betaParam, moments = "mvsk")
        randomNumber = beta.rvs(alphaParam, betaParam, lowerBound, upperBound)
        print("Mean of PERT(",lowerBound,mode,upperBound,") = ",mean)
        print("Variance of PERT(",lowerBound,mode,upperBound,") = ",var)

    return randomNumber

def simulate(numberOfSimulations):

    durationOfExtraordinaryGrowth = 5#years
    costOfEquityHeldConstant = True
    simulationOutput = pd.DataFrame(index=range(numberOfSimulations),
                                    columns=['PE_Ratio', 'DurationOfExtraordinaryGrowth',
                                             'GrowthRateEXTRA',   'GrowthRateSTABLE',
                                             'CostOfEquityEXTRA', 'CostOfEquitySTABLE',
                                             'RiskFreeRateEXTRA', 'RiskFreeRateSTABLE',
                                             'MarketReturnEXTRA', 'MarketReturnSTABLE',
                                             'EquityPremiaEXTRA', 'EquityPremiaSTABLE',
                                             'BetaEXTRA',         'BetaSTABLE',
                                             'PayoutRatioEXTRA',  'PayoutRatioSTABLE'])
    for x in range(0, numberOfSimulations):
        growthRateONE = valueRandomizer("PERT", 0.0, 10.0, 5.0)
        growthRateTWO = valueRandomizer("PERT", 0.0, 10.0, 5.0)
        growthRates = (max(growthRateONE,growthRateTWO), min(growthRateONE,growthRateTWO))
        payoutRatioONE = valueRandomizer("PERT", 0.0, 10.0, 5.0)
        payoutRatioTWO = valueRandomizer("PERT", 0.0, 10.0, 5.0)
        payoutRatios = (max(payoutRatioONE,payoutRatioTWO), min(payoutRatioONE,payoutRatioTWO))
        costsOfEquity=0
        extraordinaryCostOfEquity=0
        stableCostOfEquity=0
        equityPremia = 0

        if(costOfEquityHeldConstant is True):
            beta = valueRandomizer("PERT", -2.0, 2.0, 1.2)
            simulationOutput.at[x, 'BetaEXTRA'] = beta
            simulationOutput.at[x, 'BetaSTABLE'] = beta
            riskFreeRate = valueRandomizer("PERT", 0.0, 8.0, 2.95)
            simulationOutput.at[x, 'RiskFreeRateEXTRA'] = riskFreeRate
            simulationOutput.at[x, 'RiskFreeRateSTABLE'] = riskFreeRate
            marketReturn = valueRandomizer("PERT", -18.0, 18.0, 7.0)
            simulationOutput.at[x, 'MarketReturnEXTRA'] = marketReturn
            simulationOutput.at[x, 'MarketReturnSTABLE'] = marketReturn
            equityPremia = (marketReturn - riskFreeRate)
            stableCostOfEquity = calcCostOfEquity(riskFreeRate, beta, 'MarketReturn', marketReturn)
            extraordinaryCostOfEquity = stableCostOfEquity
            costsOfEquity = (extraordinaryCostOfEquity, stableCostOfEquity)
        elif(costOfEquityHeldConstant is False):
            beta = valueRandomizer("PERT", -2.0, 2.0, 1.2)
            simulationOutput.at[x, 'BetaEXTRA'] = beta
            riskFreeRate = valueRandomizer("PERT", 0.0, 8.0, 2.95)
            simulationOutput.at[x, 'RiskFreeRateEXTRA'] = riskFreeRate
            marketReturn = valueRandomizer("PERT", -18.0, 18.0, 7.0)
            simulationOutput.at[x, 'MarketReturnEXTRA'] = marketReturn
            simulationOutput.at[x, 'EquityPremiaEXTRA'] = (marketReturn - riskFreeRate)
            extraordinaryCostOfEquity = calcCostOfEquity(riskFreeRate, beta, 'MarketReturn', marketReturn)

            beta = valueRandomizer("PERT", -2.0, 2.0, 1.2)
            simulationOutput.at[x, 'BetaSTABLE'] = beta
            riskFreeRate = valueRandomizer("PERT", 0.0, 8.0, 2.95)
            simulationOutput.at[x, 'RiskFreeRateSTABLE'] = riskFreeRate
            marketReturn = valueRandomizer("PERT", -18.0, 18.0, 7.0)
            simulationOutput.at[x, 'MarketReturnSTABLE'] = marketReturn
            simulationOutput.at[x, 'EquityPremiaSTABLE'] = (marketReturn - riskFreeRate)
            stableCostOfEquity = calcCostOfEquity(riskFreeRate, beta, 'MarketReturn', marketReturn)

            costsOfEquity = (extraordinaryCostOfEquity, stableCostOfEquity)


        priceToEarnings = calcTwoStage_PE(growthRates, payoutRatios, costsOfEquity, durationOfExtraordinaryGrowth)
        simulationOutput.at[x, 'PE_Ratio'] = priceToEarnings
        simulationOutput.at[x, 'DurationOfExtraordinaryGrowth'] = durationOfExtraordinaryGrowth
        simulationOutput.at[x, 'GrowthRateEXTRA'] = growthRates[0]
        simulationOutput.at[x, 'GrowthRateSTABLE'] = growthRates[1]
        simulationOutput.at[x, 'PayoutRatioEXTRA'] = payoutRatios[0]
        simulationOutput.at[x, 'PayoutRatioSTABLE'] = payoutRatios[1]
        simulationOutput.at[x, 'CostOfEquityEXTRA'] = costsOfEquity[0]
        simulationOutput.at[x, 'CostOfEquitySTABLE'] = costsOfEquity[1]
    return simulationOutput

numberOfSimulations = 100
simulationOutput = simulate(numberOfSimulations)
#print(simulationOutput['CostOfEquitySTABLE'])
fig = plt.figure()
fig.suptitle('Equity Research Dashboard Control', fontsize=20)

numPanelRows = 3
numPanelColumns = 3
totalNumPanels = (numPanelRows * numPanelColumns)
for x in range(1, totalNumPanels+1):

    text = "ax"+str(x)+" = fig.add_subplot("+str(numPanelRows)+","+str(numPanelColumns)+","+str(x)+")"
    exec(text)


# ax1 = fig.add_subplot(321)
# ax2 = fig.add_subplot(322)
# ax3 = fig.add_subplot(323)
# ax4 = fig.add_subplot(324)
# ax5 = fig.add_subplot(325)
# ax6 = fig.add_subplot(326)

# _x = simulationOutput['CostOfEquitySTABLE']
# _y = simulationOutput['PayoutRatioSTABLE']
# _xx, _yy = np.meshgrid(_x, _y)
# x, y = _xx.ravel(), _yy.ravel()
#
# top = x + y
# bottom = np.zeros_like(top)
# width = depth = 1
#
# ax3.bar3d(x, y, bottom, width, depth, top, shade=True)
# ax3.set_title('Shaded')
# ax3.set_xlabel('X axis')
# ax3.set_ylabel('Y axis')
# ax3.set_zlabel('Z axis')

# X = np.array(simulationOutput['CostOfEquitySTABLE'].values.tolist())
# print(X.shape)
# Y = np.array(simulationOutput['PayoutRatioSTABLE'].values.tolist())
# print(Y.shape)
# Z = np.array(simulationOutput['PE_Ratio'].values.tolist())
# print(Z.shape)
#

parameterOfInterest = 'PayoutRatioSTABLE'
parameterInQuestion = np.array(simulationOutput[parameterOfInterest].values.tolist()) #Converts list to NumPy array
#subplotLeftness_Bottomness = ax1.get_position().get_points().tolist()[0]
#subplotHeight_Width = ax1.get_position().get_points().tolist()[1]


N, bins, patches = ax1.hist(parameterInQuestion, bins='auto') # N is the count in each bin, bins is the lower-limit of the bin
fracs = N / N.max() # This wil color code by height, but you could use any scalar
norm = colors.Normalize(fracs.min(), fracs.max()) # This normalizes the data to 0..1 for the full range of the colormap
for thisfrac, thispatch in zip(fracs, patches): # This will loop thru the objects and set the color of each accordingly
    color = plt.cm.viridis(norm(thisfrac))
    thispatch.set_facecolor(color)
ax2.hist(parameterInQuestion, bins='auto', density=True) # We can also normalize our inputs by the total number of counts
ax2.set_title('Frequency Distribution of '+parameterOfInterest)
ax2.set_xlabel(parameterOfInterest)
ax2.set_ylabel('Proportion')
ax1.axvline(parameterInQuestion.mean(), color='k', linestyle='dashed', linewidth=1)
ax2.axvline(parameterInQuestion.mean(), color='k', linestyle='dashed', linewidth=1)
ax2.yaxis.set_major_formatter(PercentFormatter(xmax=1)) #Formats the y-axis to display percentage
ax1.grid()
ax2.grid()


'''Multi-Cursor Functionality (dragging on one subplots drags simultaneously on another'''
#ax1.get_shared_x_axes().join(ax1, ax2)
#multi = MultiCursor(fig.canvas, (ax1, ax2), color='r', lw=1)



#Initial Assumptions
extraordinaryGrowthRate = 20
stableGrowthRate = 5
extraordinaryPayoutRatio = 10
stablePayoutRatio = 25
extraordinaryCostOfEquity = 7
stableCostOfEquity = 3
growthRates = (extraordinaryGrowthRate, stableGrowthRate)
payoutRatios = (extraordinaryPayoutRatio, stablePayoutRatio)
costsOfEquity = (extraordinaryCostOfEquity, stableCostOfEquity)
durations = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
priceToEarningsRatios = []
for x in range(0,len(durations)):
    peRatio = calcTwoStage_PE(growthRates, payoutRatios, costsOfEquity, durations[x])
    priceToEarningsRatios.append(peRatio)

#[line] = ax5.bar(t, signal(amp_0, freq_0), linewidth=2, color='red')
coordinatesForBarChart = ax5.bar(durations, priceToEarningsRatios)
#print(coordinatesForBarChart.get)
ax5.set_title('Manipulation of the 2-Stage P/E Ratio')
ax5.set_ylabel('P/E Ratio')
ax5.set_xlabel('Duration of Extraordinary Growth')



#print('AXIS LOCATOR:',payoutSlider.ax.get_window_extent().get_points().tolist())
#print('prevSliderLeftness:',prevSliderLeftness)
#print('prevSliderBottomness:',prevSliderBottomness)
#print('prevSliderWidth:',prevSliderWidth)
#print('prevSliderHeight:',prevSliderHeight)

#                       [left, bottom, width, height]

defaultSliderHeight = 0.02
defaultSliderWidth = 0.35
subplotLeftness = ax5.get_position().get_points().tolist()[0][0]
subplotBottomness = ax5.get_position().get_points().tolist()[0][1]


#subplotLeftness_Bottomness = ax5.get_position().get_points().tolist()[0]
subplotHeight = ax5.get_position().get_points().tolist()[1][0]
subplotWidth = ax5.get_position().get_points().tolist()[1][1]

print("Subplot width is:",ax1.get_window_extent().get_points())
#print(inv.transform((335.175,  247.)))
payoutSlider = Slider(plt.axes([subplotLeftness, 0.53, defaultSliderWidth, defaultSliderHeight]), 'Payout', 0.1, 30.0, valinit=5, valstep=5)
prevSliderLeftness = payoutSlider.ax.get_position().get_points().tolist()[0][0]
prevSliderBottomness = payoutSlider.ax.get_position().get_points().tolist()[0][1]
prevSliderWidth = payoutSlider.ax.get_position().get_points().tolist()[1][0]
prevSliderHeight = payoutSlider.ax.get_position().get_points().tolist()[1][1]
betaSlider = Slider(plt.axes([subplotLeftness, prevSliderBottomness-(defaultSliderHeight+0.01), defaultSliderWidth, defaultSliderHeight]), r'$\beta_d$', -2.0, 2.0, valinit=1, valstep=0.001)
prevSliderBottomness = betaSlider.ax.get_position().get_points().tolist()[0][1]
riskFreeSlider = Slider(plt.axes([subplotLeftness, prevSliderBottomness-(defaultSliderHeight+0.01), defaultSliderWidth, defaultSliderHeight]), 'Risk-Free Rate', 0.0, 5.0, valinit=3.00, valstep=0.001)
prevSliderBottomness = riskFreeSlider.ax.get_position().get_points().tolist()[0][1]
marketReturnSlider = Slider(plt.axes([subplotLeftness, prevSliderBottomness-(defaultSliderHeight+0.01), defaultSliderWidth, defaultSliderHeight]), 'Market Return', -18.0, 18.0, valinit=7.00, valstep=0.001)




radio1 = RadioButtons(plt.axes([0.01, 0.653, 0.09, 0.1]), (r'$\beta_d$', r'$\alpha_i$', r'$\Delta_{\theta}$'), active = 0)


def update(val):
    payout_currSliderVal = payoutSlider.val
    beta_currSliderVal = betaSlider.val
    rf_currSliderVal = riskFreeSlider.val
    mr_currSliderVal = marketReturnSlider.val
    costsOfEquity = (calcCostOfEquity(rf_currSliderVal, beta_currSliderVal, 'MarketReturn', mr_currSliderVal),
                     calcCostOfEquity(rf_currSliderVal, beta_currSliderVal, 'MarketReturn', mr_currSliderVal))

    for x in range(0,len(coordinatesForBarChart.patches)):
        coordinatesForBarChart[x].set_height( calcTwoStage_PE(growthRates,(extraordinaryPayoutRatio, payout_currSliderVal), costsOfEquity,durations[x]) )
    fig.canvas.draw_idle()
payoutSlider.on_changed(update)
betaSlider.on_changed(update)
riskFreeSlider.on_changed(update)
marketReturnSlider.on_changed(update)





N = 5
ind = np.arange(N) # the x locations for the groups
width = 0.35       # the width of the bars

menMeans = (150, 160, 146, 172, 155)
menStd = (20, 30, 32, 10, 20)
p1 = ax6.bar(ind, menMeans, width, color='r', bottom=0, yerr=menStd)
womenMeans = (145, 149, 172, 165, 200)
womenStd = (30, 25, 20, 31, 22)
p2 = ax6.bar(ind + width, womenMeans, width, color='y', bottom=0, yerr=womenStd)

ax6.set_title('Scores by group and gender')
ax6.set_xticks(ind + width / 2)
ax6.set_xticklabels(('G1', 'G2', 'G3', 'G4', 'G5'))
ax6.legend((p1[0], p2[0]), ('Men', 'Women'))
ax6.autoscale_view()


columns = [2011,2012,2013,2014]
rows = ['EBIT','Retained Earnings','FCF','WACC']
celltext = [[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]]
table1 = ax4.table(cellText= celltext,rowLabels=rows,colLabels=columns,loc='center')
ax4.axis("off")  # This will leave the table alone in the window
#ax4.xaxis.set_visible(False)
#ax4.yaxis.set_visible(False)


def radioChangeTable(label):
    buttonDictionary = {r'$\beta_d$': 'shit',
                        r'$\alpha_i$': 'nigger',
                        r'$\Delta_{\theta}$': 'ballsak'}
    change = buttonDictionary[label]
    change = r'$\beta_d$'

    print(len(table1.get_celld()))

    #The column for ROW LABELS is index (___ , -1)
    #The row for COLUMN LABLES is index (0 , ___)
    for x in range(0,3):
        table1.get_celld()[(x+1, -1)].get_text().set_text(change)

    #l.set_ydata(ydata)
    plt.draw()
radio1.on_clicked(radioChangeTable)
plt.show()