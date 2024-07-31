from flask import Flask
from datetime import date, timedelta
import yfinance as yf #Alternative package if webreader does not work: pip install yfinance
import joblib
import numpy as np # Fundamental package for scientific computing with Python
import pandas as pd # Additional functions for analysing and manipulating data


app = Flask(__name__)

@app.route("/market-prediction-logreg")
def marketprediction_logreg():
    return getLogRegOrderType()

@app.route("/market-prediction")
def hello_world():
    return getOrderType()

def getLogRegOrderType():
    before = date.today() - timedelta(5)
    tomorrow = date.today() + timedelta(1)

    dataLive = yf.download (tickers = "^SPX", start = before,
                                end = tomorrow, interval = "1d").reset_index()
    vvixLive = yf.download (tickers = "^VVIX", start = before,
                                end = tomorrow, interval = "1d").reset_index()

    vvixLive['feat_vvixOpen'] = vvixLive['Open']
    vvixLive['feat_vvixPrevClose'] = vvixLive['Close'].shift(1)
    vvixLive = vvixLive.drop(['Open','Close', 'High','Low', 'Adj Close', 'Volume'], axis=1)

    # dataLive['feat_Open'] = dataLive['Open']
    dataLive = dataLive.merge(vvixLive, how='left', on='Date')# vVIX

    dataLive['Cluster'] = np.where(dataLive['Close'] > dataLive['Open'], 1, -1)

    dataLive =dataLive.dropna()

    # Seleziona le colonne con il prefisso "feat"
    feat_cols = [col for col in dataLive.columns if 'feat' in col]
    dataLive.dropna(how='any', inplace=True)

    x_live = dataLive[feat_cols]
    x_live.head()

    # Predizione dei dati di test
    clf = joblib.load("./LogRegB-Class.joblib")
    y_live_pred = clf.predict(x_live)
    dataLive['cluster'] = y_live_pred


    df = pd.DataFrame(dataLive)
    df['signal'] = np.where(df['cluster'] == 1, 1, np.where(df['cluster'] == 0, -1, 0)) 

    print('DATA',df['Date'].iloc[-1].date())

    if(df['Date'].iloc[-1].date()==(date.today())):
        orderType = 'BUY' if df['signal'].iloc[-1]==1 else 'SELL'
        print('Direzione Prevista:', orderType)
    else:
        orderType = 'noTrade'
        print('Dati per oggi non ancora disponibili. Ultima data disponibile:', df['Date'].iloc[-1].date())
    return orderType



def getOrderType():
    prevDays = date.today() - timedelta(5)
    tomorrow = date.today() + timedelta(1)

    dataLive = yf.download (tickers = "^GSPC", start = prevDays,
                                end = tomorrow, interval = "1d").reset_index()
    vixLive = yf.download (tickers = "^VIX", start = prevDays,
                                end = tomorrow, interval = "1d").reset_index()

    dataLive[f'feat_vixOpen'] = vixLive['Open']
    dataLive[f'feat_vixPrevClose'] = vixLive['Close'].shift(1)

    dataLive = predictVolatility(dataLive)

    # print('prova',dataLive.tail(20))

    # Seleziona le colonne con il prefisso "feat"
    feat_cols = [col for col in dataLive.columns if 'feat' in col]
    dataLive.dropna(how='any', inplace=True)

    x_live = dataLive[feat_cols]
    x_live.head()

    # Predizione dei dati di test
    clf = joblib.load("./rf-sp-new.joblib")
    y_live_pred = clf.predict(x_live)
    dataLive['cluster'] = y_live_pred


    df = pd.DataFrame(dataLive)
    df['signal'] = np.where(df['cluster'] == 1, 1, np.where(df['cluster'] == 0, -1, 0)) 

    print('DATA',df['Date'].iloc[-1].date())

    if(df['bigBodyRangePred'].iloc[-1] == 1 and df['Date'].iloc[-1].date()==(date.today())):
        orderType = 'BUY' if df['signal'].iloc[-1]==1 else 'SELL'
        print('Direzione Prevista:', orderType)
    else:
        orderType = 'noTrade'
        print('Dati per oggi non ancora disponibili. Ultima data disponibile:', df['Date'].iloc[-1].date())
    return orderType

def predictVolatility(dataLive): 
    # VOLATILIY
    volatilityModel = joblib.load("./VolatilitySeeker.joblib")
    volFeatures = ['feat_vixOpen']

    X_vol_live = dataLive[volFeatures]

    # Prediction Volatility
    y_live_pred = volatilityModel.predict(X_vol_live)
    dataLive['bigBodyRangePred'] = y_live_pred

    return dataLive