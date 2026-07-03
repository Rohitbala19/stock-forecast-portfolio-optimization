import pandas as pd
import yfinance as yf
import os
import time

def download_data():
    tickers = [
        "MMM", "AOS", "ABT", "ACN", "ADBE", "AAP", "AMD", "AES", "AFL", "A", 
        "APD", "AKAM", "ALK", "ALB", "ARE", "ALGN", "LNT", "ALL", "GOOGL", "GOOG", 
        "MO", "AMZN", "AEE", "AEP", "AXP", "AIG", "AMT", "AME", "AMGN", "APH", 
        "ADI", "ANSS", "AON", "APA", "AIV", "AAPL", "AMAT", "ADM", "AJG", "AIZ", 
        "T", "ATO", "ADSK", "ADP", "AZO", "AVB", "AVY", "BKR", "BAC", "BAX", 
        "BDX", "BBY", "BIO", "BIIB", "BLK", "BA", "BKNG", "BWA", "BXP", "BSX", 
        "BMY"
    ]
    
    print(f"Downloading historical data for {len(tickers)} tickers individually...")
    
    # Download data from yfinance slightly before June 2005
    start_date = "2005-01-01"
    end_date = "2024-06-30"
    
    dfs = []
    for i, ticker in enumerate(tickers):
        print(f"[{i+1}/{len(tickers)}] Downloading {ticker}...")
        
        # Retry logic with backoff
        for attempt in range(3):
            try:
                # Add a 1.0s delay to avoid throttling
                time.sleep(1.0)
                df_single = yf.download(ticker, start=start_date, end=end_date, progress=False)
                if not df_single.empty:
                    # Flatten MultiIndex if necessary
                    if isinstance(df_single.columns, pd.MultiIndex):
                        df_single.columns = df_single.columns.get_level_values(0)
                        
                    df_single.columns = pd.MultiIndex.from_product([[ticker], df_single.columns])
                    dfs.append(df_single)
                    break
                else:
                    print(f"Warning: No data returned for {ticker} (Attempt {attempt+1}/3)")
            except Exception as e:
                print(f"Error downloading {ticker}: {e} (Attempt {attempt+1}/3)")
                
            # If we reached here, attempt failed, sleep longer before retry
            time.sleep(2.0 * (attempt + 1))
        else:
            print(f"Failed to download {ticker} after 3 attempts.")
            
    if not dfs:
        raise ValueError("No data was downloaded for any of the tickers.")
        
    print("Concatenating dataframes...")
    df = pd.concat(dfs, axis=1)
    
    # Save the MultiIndex DataFrame directly to stock_new.csv
    filename = "stock_new.csv"
    df.to_csv(filename)
    print(f"Saved raw data to '{filename}' with shape {df.shape}")

if __name__ == "__main__":
    download_data()
