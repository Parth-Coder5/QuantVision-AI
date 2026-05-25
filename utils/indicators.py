import pandas as pd
import talib


def indicators(df):
    close = df["Close"].values

    df["MA20"] = talib.MA(close, timeperiod=20)
    df["MA50"] = talib.MA(close, timeperiod=50)
    df["RSI"] = talib.RSI(close, timeperiod=14)

    macd, macd_signal, macd_hist = talib.MACD(
        close,
        fastperiod=12,
        slowperiod=26,
        signalperiod=9,
    )
    df["MACD"] = macd
    df["MACD_Signal"] = macd_signal
    df["MACD_Hist"] = macd_hist

    upper, middle, lower = talib.BBANDS(
        close, timeperiod=10, nbdevup=1.5, nbdevdn=1.5, matype=0
    )
    df["BB_Upper"] = upper
    df["BB_Middle"] = middle
    df["BB_Lower"] = lower

    return df
