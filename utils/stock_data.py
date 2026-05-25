import pandas as pd
import yfinance as yf


def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        data = {
            "current_price": info.get("currentPrice"),
            "open": info.get("open"),
            "close": info.get("previousClose"),
            "volume": info.get("volume"),
            "high": info.get("dayHigh"),
            "low": info.get("dayLow"),
        }

        return data
    except Exception as e:
        return None


def get_historical_data(ticker, period="1y"):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty:
            return None

        return df
    except Exception as e:
        return None

if __name__ == "__main__":
   result = get_stock_data("NVDA")
   hist = get_historical_data("NVDA", "3mo")

   print(result)
   print(hist)
