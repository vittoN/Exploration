import calendar
import time
import pandas as pd
import numpy as np # Fundamental package for scientific computing with Python
import yfinance as yf #Alternative package if webreader does not work: pip install yfinance
from datetime import date, timedelta


def exportExcelWithTimeStamp(df, prefix, postfix):
    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)
    df.to_excel(prefix+str(time_stamp) + postfix)

def computeEquity(dataframe, commissioni, feats):
    df = pd.DataFrame(dataframe)
    
    df['pct_change'] = (df['Close']-df['Open'])
    df['signal'] = np.where(df['cluster'] == 1, 1, np.where(df['cluster'] == -1, -1, 0))
    df['commissione'] = abs(df['cluster'])*commissioni*df['Open']
    df['gain'] = (df['cluster']*df['pct_change'])-df['commissione']
    df['longGain'] = np.where(df['cluster'] == 1,df['cluster']*df['pct_change'], 0)
    df['shortGain'] = np.where(df['cluster'] == -1, df['cluster']*df['pct_change'], 0)  
    df['equity'] = np.cumsum(df['gain'])

    equity = df["equity"].iloc[-1]
    print('Equity:', equity)

    anni = df["equity"].size/240
    cagr = df["equity"].iloc[-1]/anni

    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)
    df.to_excel("Equity/"+str(time_stamp) + ''.join(feats) +"ComputedEquity.xlsx")

    return equity, cagr

def getData():
    tomorrow = date.today() - timedelta(30)

    data = yf.download (tickers = "^SPX", start = "1990-09-04",
                                end = tomorrow, interval = "1d").reset_index()
    vix = yf.download (tickers = "^VIX", start = "1990-09-04",
                                end = tomorrow, interval = "1d").reset_index()
    vvix = yf.download (tickers = "^VVIX", start = "1990-09-04",
                                end = tomorrow, interval = "1d").reset_index()

    data['feat_Open'] = data['Open']

    vix['feat_vixOpen'] = vix['Open']
    vix['feat_vixPrevClose'] = vix['Close'].shift(1)
    vvix['feat_vvixOpen'] = vvix['Open']
    vvix['feat_vvixPrevClose'] = vvix['Close'].shift(1)
    # data['feat_VolChange'] = (data['Volume'].shift(1) - data['Volume'].shift(2)) / data['Volume'].shift(2)
    # data['feat_prevClose'] = data['Close'].shift(1)
    # data['bigBodyRange'] = np.where(abs(data['Close'] - data['Open'])/data['Open'] > 0.004, 1, 0)
    # vix['feat_Prova'] = 1000*(vix['High'].shift(1)-vix['Low'].shift(1))/vix['Open']
    vvix['feat_Acc'] = np.where(vvix['Close'].shift(1) > vvix['Close'].shift(2), 1, 0)
    vix = vix.drop(['Open','Close', 'High','Low', 'Adj Close', 'Volume'], axis=1)
    vvix = vvix.drop(['Open','Close', 'High','Low', 'Adj Close', 'Volume'], axis=1)
    data = data.merge(vix, how='left', on='Date')# VIX
    data = data.merge(vvix, how='left', on='Date')# vVIX
    data['Cluster'] = np.where(data['Close'] > data['Open'], 1, -1)
    # data['Cluster'] = np.where(data['Close'] > data['Open']+data['Open']*0.001, 1, np.where(data['Close'] < data['Open']-data['Open']*0.001, -1,0))
    data['feat_PrevCluster'] = data['Cluster'].astype('Int64').shift(1)
    data['feat_bigBodyRange'] = np.where(abs(data['Close'] - data['Open'])/data['Open'] > 0.01, 1, 0)

    # data['feat_PrevBody'] = 100000*(data['Close'].shift(1)-data['Open'].shift(10))/data['Open'].shift(10)

    data =data.dropna()
    return data