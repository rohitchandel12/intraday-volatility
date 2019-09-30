import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pyplot
import seaborn as sns
import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error
from scipy.stats import boxcox
import statsmodels.api as sm

plt.style.use('fivethirtyeight')


plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 12


class LoBVolModel:
    def __init__(self, data, freq='1T'):
        self.lob = data
        self.freq = freq
        self.__preprocess()

    def __preprocess(self):
        self.lob['timestamp'] = self.lob['DATE'].astype(str) + ' ' + self.lob['TIME_M']
        self.lob['timestamp'] = pd.to_datetime(self.lob['timestamp'])
        self.lob.index = self.lob['timestamp']
        self.lob['MID_PRICE'] = (self.lob['BID'] + self.lob['ASK']) / 2
        self.lob['TRDSIZ'] = (self.lob['BIDSIZ'] + self.lob['ASKSIZ']) / 2
        self.lob = self.lob[['timestamp', 'BID', 'ASK', 'TRDSIZ', 'MID_PRICE']]
        lob_by_period = self.lob.resample(self.freq).mean()
        # calculate spread
        lob_by_period['SPREAD'] = np.abs(lob_by_period['ASK'] - lob_by_period['BID']) / lob_by_period['MID_PRICE']
        lob_by_period['ret'] = np.log(lob_by_period['MID_PRICE']) - np.log(lob_by_period['MID_PRICE'].shift(1))
        lob_by_period = lob_by_period.dropna()
        ret_lags = self.__create_lagged_features(lob_by_period[['ret']])
        lob_w_lags = pd.concat([lob_by_period, ret_lags], axis=1)
        lob_w_lags = lob_w_lags.fillna(0)
        ret_cols = ['ret_' + str(i) for i in range(12)]
        # take absolute values of returns
        lob_w_lags[ret_cols] = np.abs(lob_w_lags[ret_cols])
        x_cols = np.concatenate((ret_cols, ['TRDSIZ', 'SPREAD']))
        lob_w_lags['VOL'] = lob_w_lags['ret_0'] ** 2
        lob_w_lags = lob_w_lags.replace([np.inf, -np.inf], np.nan).dropna()
        self.X = lob_w_lags[x_cols][:-1]
        self.y = lob_w_lags[['ret_0']].shift(-1)[:-1]
        self.lob_w_lags = lob_w_lags

    def __create_lagged_features(self, X, lag=12):
        """
        This function creates the lagged feature dataframe specifically useful for time series modelling
        """
        lagged_dfs = [X.shift(i).add_suffix('_' + str(i)) for i in range(lag)]
        return pd.concat(lagged_dfs, axis=1)

    def fit(self):
        X = sm.add_constant(self.X)
        model = sm.OLS(self.y, X)
        self.results = model.fit()
        return self.results

    def plot_series(self, feature, plt, title='Plot'):
        X = self.lob_w_lags
        # Add title
        plt.title(title)
        sns.lineplot(x=range(len(X.index)), y=X[feature], linewidth=1)
        plt.xticks(rotation='vertical')

    def mae(self):
        preds = self.results.predict()
        rel = self.y ** 2
        return mean_absolute_error(rel['ret_0'], preds)

    def plot_predictions(self, plt, title='Realized Vol. Vs Predicted Vol.'):
        preds = self.results.predict()
        rel = self.y ** 2
        # Add title
        plt.title(title)
        sns.lineplot(x=range(len(self.X.index)), y=preds, label='predicted(t+1)', linewidth=1)
        sns.lineplot(x=range(len(self.X.index)), y=rel['ret_0'], label='actual(t+1)', linewidth=1)
        plt.xticks(rotation='vertical')