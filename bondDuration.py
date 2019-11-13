
'''Page 518 of Simon Benninga (4th Edition)'''

bondMaturity = 10 # years
bond_YTM = 0.07
bond_faceValue = 1000

bondPrice_CURRENT = 10
bondCoupon_CURRENT = 10
currentYield = (bondCoupon_CURRENT / bondPrice_CURRENT)

ytm = 0.070
price = 1000.00
principal = 1000.00

years = list(range(1, (10 + 1)))
cashflows = [70] * 10
cashflows[-1] += principal
weightings = [(year * cashflow) / (price * ((1 + ytm) ** year)) for year, cashflow in zip(years, cashflows)]
bondDuration = sum(weightings)
print("The Bond Duration is:", bondDuration)