from flask import Flask
from datetime import date, timedelta
import yfinance as yf #Alternative package if webreader does not work: pip install yfinance
import joblib
import numpy as np # Fundamental package for scientific computing with Python
import pandas as pd # Additional functions for analysing and manipulating data
from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import Contract
import threading
import time

flaskApp = Flask(__name__)

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = [] #Initialize variable to store candle

    def historicalData(self, reqId, bar):
        print(f'DateTime: {bar.date}  Open: {bar.open}  High: {bar.high} Close: {bar.close}  Low: {bar.low}  Volume: {bar.volume}')
        self.data.append([bar.date, bar.open,bar.high,bar.close,bar.low,bar.volume])

    def cleanData(self):
        print('Cleaning Data')
        self.data.clear()

app = IBapi()

@flaskApp.route("/big-short-prediction")
def bigShortPred():
    
    connect_app(app)
    return bigShortPrediction(app)

def run_loop():
    app.run()

def bigShortPrediction(app):
    result_df = pd.DataFrame()

    # VVIX
    vvix_contract = create_contract('VVIX')
    vvix_data = request_historical_data(app, vvix_contract)
    result_df = process_data(vvix_data, result_df, 'vvix')

    # VIX
    vix_contract = create_contract('VIX')
    vix_data = request_historical_data(app, vix_contract)
    result_df = process_data(vix_data, result_df, 'vix')

    # SPX
    spx_contract = create_contract('SPX')
    spx_data = request_historical_data(app, spx_contract)
    if len(spx_data) == 0:
        print('ERROR - Probabilmente ci sono problemi di connessione alla TWS')
    else:
        spx = pd.DataFrame(spx_data, columns=['Date', 'Open', 'High', 'Close', 'Low', 'Volume'])
        spx['Date'] = spx['Date'].str[:17]
        spx['Date'] = spx['Date'].str[:4] + '-' + spx['Date'].str[4:6] + '-' + spx['Date'].str[6:8] + '' + spx['Date'].str[8:]
        spx['Date'] = pd.to_datetime(spx['Date'], format="%Y-%m-%d")

        result_df['feat_Open-PrevClose'] = np.where(spx['Open'] - spx['Close'].shift(1) > 0, 1, 0)
        result_df['Date'] = pd.to_datetime(spx['Date'])

    print('Dati inseriti nel DF', result_df)
    
    # Run classification
    y_live_pred = run_classification(result_df)
    print(y_live_pred)

    if result_df['Date'].iloc[-1] == pd.Timestamp(date.today()):
        orderType = 'HOLD' if y_live_pred == 1 else 'SELL'
        print('Direzione Prevista:', orderType)
    else:
        orderType = 'noTrade'
        print('Dati per oggi non ancora disponibili. Ultima data disponibile:', result_df['Date'].iloc[-1].date())
    
    print('Direzione prevista per oggi:', orderType)

    disconnect_app(app)
    return orderType

def connect_app(app):
    app.connect('127.0.0.1', 7497, 123)
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    time.sleep(3)

def disconnect_app(app):
    app.disconnect()

def run_classification(result_df, model_path="./BigShort.joblib"):
    result_df = result_df.dropna()
    clf = joblib.load(model_path)
    features = ['feat_Open-PrevClose', 'feat_vixOpen', 'feat_vixPrevClose', 'feat_vvixOpen', 'feat_vvixPrevClose']
    x_live = result_df[features]
    y_live_pred = clf.predict(x_live)
    return y_live_pred

def create_contract(symbol, secType='IND', exchange='CBOE', currency='USD'):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = secType
    contract.exchange = exchange
    contract.currency = currency
    return contract

def request_historical_data(app, contract):
    app.cleanData()
    app.reqHistoricalData(1, contract, '', "2 D", "1 Day", "TRADES", 0, 1, False, [])
    time.sleep(2)
    return app.data

def process_data(data, result_df, prefix):
    if len(data) == 0:
        print('ERROR - Probabilmente ci sono problemi di connessione alla TWS')
        return result_df

    df = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Close', 'Low', 'Volume'])
    df['Date'] = df['Date'].str[:17]
    df['Date'] = df['Date'].str[:4] + '-' + df['Date'].str[4:6] + '-' + df['Date'].str[6:8] + '' + df['Date'].str[8:]
    df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")

    result_df[f'feat_{prefix}Open'] = df['Open']
    result_df[f'feat_{prefix}PrevClose'] = df['Close'].shift(1)

    return result_df