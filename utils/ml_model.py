from curl_cffi.requests import models
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def prepare_features(df):
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

    features = ['RSI', 'MA20', 'MA50', 'BB_Middle', 'MACD', 'MACD_Signal']

    X = df[features]
    y = df['Target']

    X = X.dropna()
    y = y[X.index]
    
    return X,y

def train_model(X,y):
    X_train , X_test, y_train, y_test = train_test_split(
        X,y,
        random_state = 42,
        test_size = 0.2
    )

    model = RandomForestClassifier(n_estimators = 100, random_state= 42)
    model.fit(X_train,y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    return model,accuracy

def predict_tomorrow(model,df):
    features = ['RSI', 'MA20', 'MA50', 'BB_Middle', 'MACD', 'MACD_Signal']       
    latest = df[features].dropna().iloc[-1:]
    prob = model.predict_proba(latest)[0]
    return {
        "down": round(prob[0] * 100, 1),
        "up": round(prob[1] * 100, 1)
    }

