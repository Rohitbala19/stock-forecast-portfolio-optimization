import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import os

def run_moving_average(df_pivot):
    print("Running Moving Average strategy...")
    # Calculate 252-day moving average of close prices
    ma_df = df_pivot.rolling(252).mean()
    ma_df.to_csv("MovingAverage.csv")
    print("Saved Moving Average data to 'MovingAverage.csv'")
    return ma_df

def predict_prices(raw_df_numpy, close_df, time_idx, lookback, forward, stock_num):
    # PCA setup
    pca1 = PCA(n_components=10)
    pca2 = PCA(n_components=10)
    
    # Training data = [time_idx - forward - lookback : time_idx - forward]
    start_train_idx = time_idx - forward - lookback
    end_train_idx = time_idx - forward
    
    X_train = raw_df_numpy[start_train_idx:end_train_idx, :]
    X_train_scaled = MinMaxScaler().fit_transform(X_train)
    X_train_pca = pca1.fit_transform(X_train_scaled)
    
    y_train = close_df.iloc[end_train_idx:time_idx, stock_num]
    
    # Testing data = [time_idx - lookback : time_idx]
    start_test_idx = time_idx - lookback
    end_test_idx = time_idx
    
    X_test = raw_df_numpy[start_test_idx:end_test_idx, :]
    X_test_scaled = MinMaxScaler().fit_transform(X_test)
    X_test_pca = pca2.fit_transform(X_test_scaled)
    
    y_test = close_df.iloc[end_test_idx : end_test_idx + forward, stock_num]
    
    # Fit Linear Regression
    LR = LinearRegression()
    LR.fit(X_train_pca, y_train)
    predicted = LR.predict(X_test_pca)
    
    return predicted, y_test

def run_linear_regression(raw_df_numpy, close_df):
    print("Running Linear Regression strategy (with rolling PCA)...")
    
    predictions = []
    actuals = []
    
    tickers = close_df.columns
    num_stocks = len(tickers)
    
    # Step size of 30, lookback 30, forward 30
    lookback = 30
    forward = 30
    step = 30
    
    # Outer loop over stocks
    for stock_idx in range(num_stocks):
        stock_predictions = []
        stock_actuals = []
        
        # Inner loop over rolling windows
        for time_idx in range(lookback + forward, len(close_df) - forward, step):
            pred, act = predict_prices(raw_df_numpy, close_df, time_idx, lookback, forward, stock_idx)
            stock_predictions.append(pred)
            stock_actuals.append(act)
            
        stock_predictions = np.concatenate(stock_predictions)
        stock_actuals = np.concatenate(stock_actuals)
        
        predictions.append(stock_predictions)
        actuals.append(stock_actuals)
        
    predictions = np.array(predictions).T
    actuals = np.array(actuals).T
    
    # Date alignment
    # Since lookback+forward = 60, predictions start from index 60 of the close prices dataframe
    # Truncate length of predictions and actuals to align them
    num_prediction_days = min(predictions.shape[0], len(close_df) - 60)
    
    # Slice the dates to match the length
    prediction_dates = close_df.index[60 : 60 + num_prediction_days]
    
    final_preds = pd.DataFrame(data=predictions[:num_prediction_days], index=prediction_dates, columns=tickers)
    final_actuals = pd.DataFrame(data=actuals[:num_prediction_days], index=prediction_dates, columns=tickers)
    
    final_preds.to_csv("LR_Predicted_Prices.csv")
    final_actuals.to_csv("LR_Actual_Prices.csv")
    
    print(f"Saved Linear Regression predictions/actuals to CSV with shape {final_preds.shape}")

def main():
    pivot_file = "final_closing_prices_pivot.csv"
    raw_file = "stock_new.csv"
    
    if not os.path.exists(pivot_file) or not os.path.exists(raw_file):
        raise FileNotFoundError("Make sure to run download_data.py and pivot_data.py first.")
        
    # 1. Load pivoted Close prices
    df_close = pd.read_csv(pivot_file, index_col=0, parse_dates=True)
    
    # 2. Run Moving Average
    run_moving_average(df_close)
    
    # 3. Load raw data for Linear Regression (Open, High, Low, Close, Adj Close, Volume for each stock)
    # We will map standard MultiIndex structure and keep Adjust Close as Adjusted
    raw_df = pd.read_csv(raw_file, header=[0, 1], index_col=0, parse_dates=True)
    raw_df = raw_df.rename(columns={"Adj Close": "Adjusted"}, level=1)
    
    # Drop rows containing NaNs
    raw_df = raw_df.dropna(axis=0)
    
    # Pivot Close to match raw_df index
    df_close_aligned = df_close.loc[raw_df.index]
    
    # Convert raw_df to numpy array for fast slicing
    raw_df_numpy = raw_df.to_numpy()
    
    # 4. Run Linear Regression
    run_linear_regression(raw_df_numpy, df_close_aligned)

if __name__ == "__main__":
    main()
