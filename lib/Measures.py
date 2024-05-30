import pandas as pd # Additional functions for analysing and manipulating data
import numpy as np # Fundamental package for scientific computing with Python


def countMaxConsecutiveLoss(df):
    maxLossCount = 0
    lossCount = 0
    for index, row in df.iterrows():
        if (row['gain'] < 0):
            lossCount += 1
        else:
            if (lossCount > maxLossCount):
                maxLossCount = lossCount
            lossCount = 0
    return maxLossCount


def measureDataframe(df):

    df['longEquity'] = np.cumsum(df['longGain'])
    df['shortEquity'] = np.cumsum(df['shortGain'])
    df['Buy&Hold'] = np.cumsum(df['pct_change'])
    df['HighValue'] = df['equity'].cummax()
    df['Drawdown'] = df['equity'] - df['HighValue']

    measures = {}

    anni = df["equity"].size/240
    print('Misure per', anni, 'anni')
    measures['Anni'] = anni

    # Calculate Equity
    print('Benchmark Equity:', df["Buy&Hold"].iloc[-1])
    print('Equity', df["equity"].iloc[-1])
    measures['Equity'] = df["equity"].iloc[-1]
    
    # Calculate Equity with Vol. Filter
    print('Equity Volatility Filter', df["equityVolatilityFilter"].iloc[-1])
    measures['EquityVolFilter'] = df["equityVolatilityFilter"].iloc[-1]


    # Count Max Consecutive Losses
    maxConsecutiveLosses = countMaxConsecutiveLoss(df)
    print('Maximum number of loss operation:', maxConsecutiveLosses)
    measures['MaxConsecutiveLosses'] = maxConsecutiveLosses

    # Calculate Max Drawdown
    print('Maximum DrawDown:', df["Drawdown"].min())
    measures['MaxDrawDown'] = df["Drawdown"].min()

    # Calculate SGR
    sgr = df["equity"].iloc[-1]/anni
    sgrVolFilter = df["equityVolatilityFilter"].iloc[-1]/anni
    print('SGR:', sgr, 'vs Benchmark:', df["Buy&Hold"].iloc[-1]/anni)
    print('SGR Vol Filter:', sgrVolFilter, 'vs Benchmark:', df["Buy&Hold"].iloc[-1]/anni)
    measures['SGR'] = sgr

    # Calculate Win Rate Equity
    winCount = df[df["gain"] > 0].count()['gain']
    count = df[df["gain"] != 0].count()['gain']
    winRate = 100*winCount/count
    print('Win Rate:', winRate)
    measures['WR'] = winRate

    # Calculate Win Rate Equity with Vol. Filter
    winCount = df[df["gainVolFilter"] > 0].count()['gainVolFilter']
    count = df[df["gainVolFilter"] != 0].count()['gainVolFilter']
    winRate = 100*winCount/count
    print('Win Rate Volatility Filter:', winRate)
    measures['WR_VolFilter'] = winRate

    # Calculate Long & Short Equity
    print('Long Equity', df["longEquity"].iloc[-1])
    measures['LongEquity'] = df["longEquity"].iloc[-1]
    print('Short Equity', df["shortEquity"].iloc[-1])
    measures['ShortEquity'] = df["shortEquity"].iloc[-1]

    return measures

def measureDataframe2(df):

    df['longEquity'] = np.cumsum(df['longGain'])
    df['shortEquity'] = np.cumsum(df['shortGain'])
    df['Buy&Hold'] = np.cumsum(df['pct_change'])
    df['HighValue'] = df['equity'].cummax()
    df['Drawdown'] = df['equity'] - df['HighValue']

    measures = {}

    anni = df["equity"].size/240
    print('Misure per', anni, 'anni')
    measures['Anni'] = anni

    # Calculate Equity
    print('Benchmark Equity:', df["Buy&Hold"].iloc[-1])
    print('Equity', df["equity"].iloc[-1])
    measures['Equity'] = df["equity"].iloc[-1]
    
    # Count Max Consecutive Losses
    maxConsecutiveLosses = countMaxConsecutiveLoss(df)
    print('Maximum number of loss operation:', maxConsecutiveLosses)
    measures['MaxConsecutiveLosses'] = maxConsecutiveLosses

    # Calculate Max Drawdown
    print('Maximum DrawDown:', df["Drawdown"].min())
    measures['MaxDrawDown'] = df["Drawdown"].min()

    # Calculate SGR
    sgr = df["equity"].iloc[-1]/anni

    print('SGR:', sgr, 'vs Benchmark:', df["Buy&Hold"].iloc[-1]/anni)
    measures['SGR'] = sgr

    # Calculate Win Rate Equity
    winCount = df[df["gain"] > 0].count()['gain']
    count = df[df["gain"] != 0].count()['gain']
    winRate = 100*winCount/count
    print('Win Rate:', winRate)
    measures['WR'] = winRate

    # Calculate Long & Short Equity
    print('Long Equity', df["longEquity"].iloc[-1])
    measures['LongEquity'] = df["longEquity"].iloc[-1]
    print('Short Equity', df["shortEquity"].iloc[-1])
    measures['ShortEquity'] = df["shortEquity"].iloc[-1]

    return measures

