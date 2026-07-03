import pandas as pd
import numpy as np
import os

def feature_engineering():
    filename = "stock_new.csv"
    if not os.path.exists(filename):
        raise FileNotFoundError(f"'{filename}' not found. Please run download_data.py first.")
        
    print(f"Reading raw data from '{filename}' for feature engineering...")
    
    # Read the CSV, naming indices and levels
    raw_df = pd.read_csv(filename, header=[0, 1], index_col=0, parse_dates=True)
    raw_df.index.name = "Date"
    raw_df.columns.names = ["Ticker", "Metric"]
    
    # yfinance output column structure mapping for Metric level:
    # yfinance might download fields named "Open", "High", "Low", "Close", "Adj Close", "Volume"
    # Let's map "Adj Close" to "Adjusted" to match the original notebooks exactly
    raw_df = raw_df.rename(columns={"Adj Close": "Adjusted"}, level="Metric")
    
    tickers = sorted({col[0] for col in raw_df.columns})
    print(f"Discovered {len(tickers)} tickers. Extracting features for each...")
    
    # Compute 5 new metrics per ticker
    for stock in tickers:
        # Check if Adjusted is present, if not, copy from Close
        if (stock, "Adjusted") not in raw_df.columns:
            raw_df[(stock, "Adjusted")] = raw_df[(stock, "Close")]
            
        # 1) Daily returns: pct_change() of Close price
        raw_df[(stock, "DailyRet")] = raw_df[(stock, "Close")].pct_change()
        
        # 2) 20-day returns: pct_change(20) of Close price
        raw_df[(stock, "20DayRet")] = raw_df[(stock, "Close")].pct_change(20)
        
        # 3) 20-day rolling volatility: rolling 20-day std of DailyRet
        raw_df[(stock, "20DayVol")] = raw_df[(stock, "DailyRet")].rolling(20).std(ddof=0)
        
        # 4) Rolling 252-day z-scores of 20DayRet and 20DayVol
        ry_ret = raw_df[(stock, "20DayRet")].rolling(252)
        ry_vol = raw_df[(stock, "20DayVol")].rolling(252)
        
        # (mean - value) / std
        raw_df[(stock, "Z20DayRet")] = (
            ry_ret.mean().shift(1) - raw_df[(stock, "20DayRet")]
        ) / ry_ret.std(ddof=0).shift(1)
        
        raw_df[(stock, "Z20DayVol")] = (
            ry_vol.mean().shift(1) - raw_df[(stock, "20DayVol")]
        ) / ry_vol.std(ddof=0).shift(1)
        
    # Sort columns by Ticker and Metric
    raw_df = raw_df.sort_index(axis=1, level=[0, 1])
    
    # Drop rows containing NaNs (first 252+20 days will be NaN due to rolling calculations)
    full_feature_df = raw_df.dropna(axis=0)
    
    # In PCA_LSTM.ipynb cell 25, they filter for specific metrics:
    metrics_to_keep = [
        'Open', 'High', 'Low', 'Close', 'Adjusted', 'Volume',
        'DailyRet', 'Z20DayRet', 'Z20DayVol'
    ]
    idx = pd.IndexSlice
    full_feature_filtered = full_feature_df.loc[:, idx[:, metrics_to_keep]]
    full_feature_filtered.columns = full_feature_filtered.columns.remove_unused_levels()
    
    # Save the full engineered features DataFrame
    output_filename = "full_feature_dataset.csv"
    full_feature_filtered.to_csv(output_filename)
    print(f"Saved engineered features to '{output_filename}' with shape {full_feature_filtered.shape}")

if __name__ == "__main__":
    feature_engineering()
