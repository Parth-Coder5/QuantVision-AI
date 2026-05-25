import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objs import indicator
from sklearn import model_selection
import streamlit as st
from plotly.subplots import make_subplots

from utils.stock_data import get_historical_data, get_stock_data
from utils.indicators import indicators
from utils.signals import gen_signal
from utils.backtest import run_backtest
from utils.ml_model import predict_tomorrow, prepare_features, train_model


st.set_page_config(page_title='QUANTVISION-AI', layout='wide', page_icon='💀')
st.title('QuantVision-AI')

def sidebar():
    ticker = st.sidebar.text_input(label='Type Stock Name', value='AAPL')
    period = st.sidebar.selectbox(label='Select Period',options=['5d','1mo','3mo','6mo','1y','3y'])

    return ticker,period

def render_signal(signal, score):
    st.subheader("Trading Signal")

    if signal == "BUY":
        st.success(f"🟢 {signal} — Score: {score}/4")
    elif signal == "SELL":
        st.error(f"🔴 {signal} — Score: {score}/4")
    else:
        st.warning(f"🟡 {signal} — Score: {score}/4")


def render_metrics(data):
    st.subheader(f"📊 {ticker.upper()} — Live Market Data")
    col1,col2,col3 = st.columns(3)
    col4,col5,col6 = st.columns(3)
    col1.metric('Current Price', data['current_price'])
    col2.metric('Open Price', data['open'])
    col3.metric('Volume', f"{data['volume']:,}" if data['volume'] is not None else "N/A")
    col4.metric('Previous Close', data['close'])
    col5.metric('High', data['high'])
    col6.metric('Low', data['low'])

def render_chart(hist,ticker):
    fig = make_subplots(
        rows=3,
        cols=1,
        row_heights=[0.6,0.2,0.2],
        vertical_spacing=0.1
    )

    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist['Open'],   # opening price
        high=hist['High'],   # highest price
        low=hist['Low'],     # lowest price
        close=hist['Close'],
        showlegend=False
    ),
       row=1,
       col=1
    )

    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist['MA20'],
        mode='lines',
        name='MA20',
        line={
            "color": "blue",
            "width": 1.5,
        },
    ),
    row=1,
    col=1
    )

    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist['MA50'],
        mode='lines',
        name='MA50',
        line={
            "color": "green",
            "width": 1.5,
        },
    ),
    row=1,
    col=1
    )

    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["RSI"],
            mode="lines",
            name="RSI",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["MACD"],
            mode='lines',
            name="MACD Lines"
        ),
        row=3,
        col=1
    )

    fig.add_trace(
    go.Scatter(
        x=hist.index,
        y=hist["MACD_Signal"],
        mode="lines",
        name="Signal Line",
    ),
    row=3,
    col=1
    )

    fig.add_trace(
    go.Bar(
        x=hist.index,
        y=hist["MACD_Hist"],
        name="Histogram",
    ),
    row=3,
    col=1
    )

    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)  # type: ignore[arg-type]
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)  # type: ignore[arg-type]

    fig.update_layout(
    template='plotly_dark',   # dark theme
    title=f"{ticker} Stock Price",
    xaxis_title="Date",
    yaxis_title="Price",
    xaxis_rangeslider_visible=False,
    height=1200
    )

    st.plotly_chart(fig, use_container_width=True)

def render_ml(df):
    st.subheader("🤖 ML Prediction — Tomorrow")
    
    X,y = prepare_features(df)
    model, accuracy = train_model(X,y)
    prediction = predict_tomorrow(model,df)

    col1,col2,col3 = st.columns(3)

    col1.metric("📈 UP Probability", f"{prediction['up']}%")
    col2.metric("📉 DOWN Probability", f"{prediction['down']}%")
    col3.metric("🎯 Model Accuracy", f"{round(accuracy*100, 1)}%")

    if prediction['up'] > 60:
        st.success("✅ ML Verdict: LIKELY UP tomorrow")
    elif prediction['down'] > 60:
        st.error("❌ ML Verdict: LIKELY DOWN tomorrow")
    else:
        st.warning("⚠️ ML Verdict: UNCERTAIN — No clear direction")


def render_backtest(ticker):
    st.subheader('BACKTESTING RESULTS')

    if st.button('Run Backtest!!'):
       result = run_backtest(ticker)
       if result is None:
        return None
       col1, col2, col3, col4, col5 = st.columns(5)
       
       col1.metric('Total Trades', result['total_trades'])
       col2.metric('Wins', result['wins'])
       col3.metric('Loses', result['losses'])
       col4.metric('Avg PNL', result['avg_pnl'])
       col5.metric('Total Profit', result['total_profit'])

       import pandas as pd
       trades_df = pd.DataFrame(result['trades'])
       st.dataframe(trades_df)

       if result['win_rate'] >= 50:
        st.success(f"Win Rate: {result['win_rate']}%")
       else:
        st.error(f"Win Rate: {result['win_rate']}%")
    


ticker, period = sidebar()
data = get_stock_data(ticker)
hist = get_historical_data(ticker, period)

if data is None or hist is None:
    st.error("Invalid ticker or no data found.")
    st.stop()

new_hist = indicators(hist)
signal, score = gen_signal(new_hist)
ml_hist = get_historical_data(ticker, '5y')
ml_hist = indicators(ml_hist)

render_signal(signal, score)
render_metrics(data)
render_chart(new_hist, ticker)
render_ml(ml_hist)
render_backtest(ticker)

    