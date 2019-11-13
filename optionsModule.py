from math import *
from scipy.stats import norm

def black_scholes(currentStockPrice, exercisePrice, riskFreeRate, timeToMaturityForOption, stockVolatilty):
    '''pgs425-429 of Simon Benninga 4th'''
    d_ONE = (log(currentStockPrice / exercisePrice) + (
                (riskFreeRate + ((stockVolatilty ** 2) / 2)) * timeToMaturityForOption)) / (
                        stockVolatilty * sqrt(timeToMaturityForOption))
    d_TWO = (d_ONE - (stockVolatilty * sqrt(timeToMaturityForOption)))

    cumulativeProbability_d_ONE = norm.cdf(d_ONE)
    cumulativeProbability_d_TWO = norm.cdf(d_TWO)

    callPrice = currentStockPrice * cumulativeProbability_d_ONE - exercisePrice * exp(
        -1 * riskFreeRate * timeToMaturityForOption) * cumulativeProbability_d_TWO
    callPrice = round(callPrice, 2)
    putPrice = (callPrice - currentStockPrice + (exercisePrice * exp(-1 * riskFreeRate * timeToMaturityForOption)))
    putPrice = round(putPrice, 2)

    print("============================")
    print("d_ONE =", d_ONE, " & d_TWO =", d_TWO)
    print("Stock Price: $", currentStockPrice, "& Exercise Price: $", exercisePrice)
    print("Call Price: $", callPrice, "& Put Price: $", putPrice)
    print("Intrinsic Value:", max(0, currentStockPrice - exercisePrice))
    print("============================")


for x in range(5, 80, 5):
    black_scholes(x, 45.00, 0.04, 0.75, 0.30)

