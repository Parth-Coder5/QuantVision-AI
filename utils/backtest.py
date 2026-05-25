import pandas as pd
from utils.indicators import indicators
from utils.stock_data import get_historical_data
from utils.signals import gen_signal_row
from utils.ml_model import prepare_features, train_model, predict_tomorrow

#CONSTANTS
PERIOD = '1y'
MAX_HOLD_DAYS = 10
TP_PCT = 0.04
SL_PCT = 0.03
MIN_BUY_SCORE = 3
CAPITAL_PER_TRADE = 10000


#PREPARING DATA FOR BACKTESTING
def prepare_data(ticker):
    hist = get_historical_data(ticker,PERIOD)
    if hist is None:
        return None
    df = indicators(hist)

    return df

#SIMULATING THE TRADES
def simulate_trades(df):
    trades = []
    cooldown = 0

    X, y = prepare_features(df)
    model, accuracy = train_model(X, y)

    for i in range(len(df)):
        row = df.iloc[i]
        if cooldown > 0:
            cooldown -= 1
            continue

        signal,score = gen_signal_row(row)

        if signal == 'BUY' and score >= 3:
            entry_price = row['Open']
            qty = (CAPITAL_PER_TRADE // entry_price)
            tp = entry_price*(1+TP_PCT)
            sl = entry_price*(1-SL_PCT)
              
            end = min(i + MAX_HOLD_DAYS + 1, len(df))

            pred = predict_tomorrow(model, df.iloc[:i+1])
            if pred['up'] < 60:
                continue

            for j in range(i+1, end):
                next_row = df.iloc[j]

                if next_row["Low"] <= sl:
                  exit_price = sl
                  exit_reason = "SL"
                  exit_date = df.index[j]
                  days_held = j - i
                  break

                if next_row["High"] >= tp:
                  exit_price = tp
                  exit_reason = "TP"
                  exit_date = df.index[j]
                  days_held = j - i
                  break
            else:

                exit_price = df.iloc[end-1]["Close"]
                exit_reason = "MAX_HOLD"
                exit_date = df.index[end-1]
                days_held = MAX_HOLD_DAYS
    
            trades.append({
              "entry_date": df.index[i],
              "exit_date": exit_date,
              "entry_price": round(entry_price, 2),
              "exit_price": round(exit_price, 2),
              "qty": int(qty),
              "days_held": days_held,
              "reason": exit_reason,
              "profit_rs": round(qty * (exit_price - entry_price), 2),
              "pnl_pct": round((exit_price - entry_price) / entry_price * 100, 2),
             })

            if exit_reason == "SL":
                cooldown = 2
    return trades


def run_backtest(ticker):
    df = prepare_data(ticker)
    if df is None:
        return None
    trades = simulate_trades(df)

    total_trades = len(trades)
    wins = sum(1 for t in trades if t['profit_rs'] > 0)
    lose = total_trades - wins
    win_rate = round(wins/total_trades*100, 2)
    total_profit = round(sum(t["profit_rs"] for t in trades), 2)
    avg_pnl = round(sum(t["pnl_pct"] for t in trades) / total_trades, 2)

    return {
    "ticker": ticker,
    "total_trades": total_trades,
    "wins": wins,
    "losses": lose,
    "win_rate": win_rate,
    "avg_pnl": avg_pnl,
    "total_profit": total_profit,
    "trades": trades
    }




