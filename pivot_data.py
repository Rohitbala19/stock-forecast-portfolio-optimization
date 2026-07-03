import pandas as pd
import os

def pivot_data():
    filename = "stock_new.csv"
    if not os.path.exists(filename):
        raise FileNotFoundError(f"'{filename}' not found. Please run download_data.py first.")
        
    print(f"Reading raw data from '{filename}'...")
    
    # Read the CSV with MultiIndex columns (row 0 has ticker names, row 1 has fields)
    df = pd.read_csv(filename, header=[0, 1], index_col=0, parse_dates=True)
    df.index.name = "Date"
    df.columns.names = ["Ticker", "Metric"]
    
    # Extract only the 'Close' prices for all tickers
    # In yfinance, standard fields include 'Close' (or 'Adj Close')
    # Let's slice the Close metric
    df_close = df.xs("Close", axis=1, level="Metric")
    
    # Save the pivoted Close prices
    pivot_filename = "final_closing_prices_pivot.csv"
    df_close.to_csv(pivot_filename)
    print(f"Extracted 'Close' prices and saved to '{pivot_filename}' with shape {df_close.shape}")

if __name__ == "__main__":
    pivot_data()
