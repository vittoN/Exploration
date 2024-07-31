import calendar
import time
import pandas as pd
import numpy as np # Fundamental package for scientific computing with Python
import yfinance as yf #Alternative package if webreader does not work: pip install yfinance
from datetime import date, timedelta
from sklearn import preprocessing

def exportExcelWithTimeStamp(df, prefix, postfix):
    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)
    df.to_excel(prefix+str(time_stamp) + postfix)

def computeEquity(dataframe, commissioni, feats, pred_prob):
    threshold = 0.5
    
    df = pd.DataFrame(dataframe)
   
    df['pct_change'] = (df['Close']-df['Open'])
    # df['signal'] = np.where(df['cluster'] == 1, 1, np.where(df['cluster'] == -1, -1, 0))
    df['commissione'] = abs(df['cluster'])*commissioni*df['Open']
    # df['gain'] = (df['cluster']*df['pct_change'])-df['commissione']

    # df['equity'] = np.cumsum(df['gain'])


    df2 = pd.DataFrame(pred_prob)
    df2.index = df.index
    df = df.merge(df2, left_index=True, right_index=True)
    #print(df)
    # df['signal'] = np.where(df[0] >= threshold, -1, np.where(df[1] >= threshold, 1, 0))
    df['signal'] = np.where((df[0] >= threshold) , -1, 0) #Considero solo SHORT
    df['gain'] = (df['signal']*df['pct_change'])-df['commissione']*abs(df['signal'])
    df['longGain'] = np.where(df['signal'] == 1,df['signal']*df['pct_change'], 0)
    df['shortGain'] = np.where(df['signal'] == -1, df['signal']*df['pct_change'], 0)  
    df['equity'] = np.cumsum(df['gain'])

    df['HighValue'] = df['equity'].cummax()
    df['Drawdown'] = df['equity'] - df['HighValue']

    df['maxDD'] = df["Drawdown"].min()
    equity = df["equity"].iloc[-1]
    print('Equity:', equity)

    df['anni'] = df["equity"].size/240
    df['cagr'] = df["equity"].iloc[-1]/df["anni"].iloc[-1]

    df['numOp'] = df[df["gain"] != 0].count()['gain']
    # print('Numero di Eseguiti', numOp)

    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)
    df.to_excel("Equity/"+str(time_stamp) + ''.join(feats) +"ComputedEquity.xlsx")

    return df

def getData(bigbodyRangeValue):
    tomorrow = date.today() - timedelta(30)
    start = "1990-09-04"
    # tomorrow = "2023-09-04"

    data = yf.download (tickers = "^SPX", start = start,
                                end = tomorrow, interval = "1d").reset_index()
    vix = yf.download (tickers = "^VIX", start = start,
                                end = tomorrow, interval = "1d").reset_index()
    vvix = yf.download (tickers = "^VVIX", start = start,
                                end = tomorrow, interval = "1d").reset_index()
    # print(data.head())
    # print(vix.head())
    # print(vvix.head())
    scaler = preprocessing.MinMaxScaler()
    data['feat_Open'] = scaler.fit_transform(data['Open'].values.reshape(-1, 1))


    data['feat_Open-PrevClose'] = np.where(data['Open']-data['Close'].shift(1)>0,1,0)
    vix['feat_vixOpen'] = vix['Open']
    vix['feat_vixPrevClose'] = vix['Close'].shift(1)
    vvix['feat_vvixOpen'] = vvix['Open']
    vvix['feat_vvixPrevClose'] = vvix['Close'].shift(1)
    vvix['feat_vvixPrevOpen'] = vvix['Open'].shift(1)
    vvix['feat_vvixPrevHigh'] = vvix['High'].shift(1)
    vvix['feat_vvixPrevLow'] = vvix['Low'].shift(1)
    vvix['feat_vvixPrevHigh-Low'] = (vvix['High'].shift(1)-vvix['Low'].shift(1))/vvix['Open'].shift(1)
    # data['feat_VolChange'] = (data['Volume'].shift(1) - data['Volume'].shift(2)) / data['Volume'].shift(2)
    # data['feat_prevClose'] = data['Close'].shift(1)
    # data['bigBodyRange'] = np.where(abs(data['Close'] - data['Open'])/data['Open'] > 0.004, 1, 0)
    # vix['feat_Prova'] = 1000*(vix['High'].shift(1)-vix['Low'].shift(1))/vix['Open']
    vvix['feat_Acc'] = np.where(vvix['Close'].shift(1) > vvix['Close'].shift(2), 1, 0)
    vix = vix.drop(['Open','Close', 'High','Low', 'Adj Close', 'Volume'], axis=1)
    vvix = vvix.drop(['Open','Close', 'High','Low', 'Adj Close', 'Volume'], axis=1)
    data = data.merge(vix, how='left', on='Date')# VIX
    data = data.merge(vvix, how='left', on='Date')# vVIX
    data['Cluster'] = np.where((data['Close'] < data['Open']) & (abs(data['Close'] - data['Open'])/data['Open'] > bigbodyRangeValue), -1, 1)

    # data['Cluster'] = np.where(data['Close'] > data['Open']+data['Open']*0.001, 1, np.where(data['Close'] < data['Open']-data['Open']*0.001, -1,0))
    data['feat_PrevCluster'] = data['Cluster'].astype('Int64').shift(1)
    data['feat_prevBigBodyRange'] = np.where(abs(data['Close'].shift(1) - data['Open'].shift(1))/data['Open'].shift(1) > bigbodyRangeValue, 1, 0)
    # data['feat_bigBodyRange'] = np.where(abs(data['Close'] - data['Open'])/data['Open'] > 0.01, 1, 0)

    # data['feat_PrevBody'] = 100000*(data['Close'].shift(1)-data['Open'].shift(10))/data['Open'].shift(10)

    data =data.dropna()
    data.to_excel('data1.xlsx')
    return data