import numpy as np
import pandas as pd
import pandas_datareader.data as pdr
import fix_yahoo_finance as yf
import arch
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
yf.pdr_override()

class stock_vol:
    def __init__(self, tk, start, end):
      self.tk = tk
      self.start = start
      self.end = end
      all_data = pdr.get_data_yahoo(self.tk, start=self.start, end=self.end)
      self.stock_data = pd.DataFrame(all_data['Adj Close'], columns=["Adj Close"])
      self.stock_data["log"] = np.log(self.stock_data)-np.log(self.stock_data.shift(1))def garch_sigma(self):
      model = arch.arch_model(self.stock_data["log"].dropna(), mean='Zero', vol='GARCH', p=1, q=1)
      model_fit = model.fit()
      forecast = model_fit.forecast(horizon=1)
      var = forecast.variance.iloc[-1]
      sigma = float(np.sqrt(var))
      return sigma

