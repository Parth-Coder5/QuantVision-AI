import pandas as pd


def gen_signal_row(row):
    """Score one day's row (for backtest loop)."""
    cols = ["MA20", "MA50", "RSI", "MACD", "MACD_Signal", "BB_Middle"]
    if row[cols].isnull().any():
        return "HOLD", 0

    score = 0

    if row["MA20"] > row["MA50"]:
        score += 1

    if row["RSI"] > 50:
        score += 1

    if row["MACD"] > row["MACD_Signal"]:
        score += 1

    if row["Close"] > row["BB_Middle"]:
        score += 1

    if score >= 3:
        return "BUY", score

    if score <= 1:
        return "SELL", score

    return "HOLD", score


def gen_signal(df):
    """Live signal for latest bar only (Streamlit)."""
    return gen_signal_row(df.iloc[-1])
