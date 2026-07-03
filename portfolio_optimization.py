import pandas as pd
import numpy as np
import math
from datetime import timedelta
from dateutil.parser import parse
from scipy.optimize import minimize, Bounds
from numpy.linalg import norm
import os
import matplotlib.pyplot as plt

def monthdelta(date, delta):
    m, y = (date.month + delta) % 12, date.year + ((date.month) + delta - 1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    new_date = date.replace(day=d, month=m, year=y)
    return parse(new_date.strftime('%Y-%m-%d'))

def windowGenerator(dataframe, lookback, horizon, step, cumulative=False):
    if cumulative:
        c = lookback
        step = horizon

    initial = min(dataframe.index)
    windows = []
    horizons = []

    while initial <= monthdelta(max(dataframe.index), -lookback):
        windowStart = initial
        windowEnd = monthdelta(windowStart, lookback)
        if cumulative:
            windowStart = min(dataframe.index)
            windowEnd = monthdelta(windowStart, c) + timedelta(days=1)
            c += horizon
        horizonStart = windowEnd + timedelta(days=1)
        horizonEnd = monthdelta(horizonStart, horizon)

        lookbackWindow = dataframe[windowStart:windowEnd]
        horizonWindow = dataframe[horizonStart:horizonEnd]

        windows.append(lookbackWindow)
        horizons.append(horizonWindow)

        initial = monthdelta(initial, step)

    return windows, horizons

def actual_return(actual_returns, w):
    mean_return = actual_returns.mean(axis=0)
    actual_covariance = actual_returns.cov()

    portfolio_returns = mean_return.T.dot(w)
    portfolio_variance = w.T.dot(actual_covariance).dot(w)
    return portfolio_returns, portfolio_variance

def scipy_opt(predicted_returns, actual_returns, lam1, lam2):
    mean_return = predicted_returns.mean(axis=0)
    predicted_covariance = predicted_returns.cov()

    # Cost Function matching the original formula:
    # minimize -(expected_return - lam1 * variance + lam2 * L1_norm)
    def f(w):
        return -(mean_return.T.dot(w) - lam1 * (w.T.dot(predicted_covariance).dot(w)) + lam2 * norm(w, ord=1))

    # Long-only constraint: weights between 0 and 1
    opt_bounds = Bounds(0, 1)

    # Fully invested constraint: sum of weights = 1
    cons = ({
        'type': 'eq',
        'fun': lambda w: sum(w) - 1
    })

    # Solver
    num_stocks = mean_return.shape[0]
    sol = minimize(
        f,
        x0=np.ones(num_stocks) / num_stocks,
        constraints=cons,
        bounds=opt_bounds,
        options={'disp': False},
        tol=10e-10
    )

    w = sol.x
    portfolio_predicted_returns = w.dot(mean_return)
    portfolio_STD = w.T.dot(predicted_covariance).dot(w)

    portfolio_actual_returns, portfolio_actual_variance = actual_return(actual_returns, w)
    
    # Original author's bug: dividing by std of a scalar variance (which is 0, giving +/- inf)
    original_std = np.std(portfolio_actual_variance)
    if original_std == 0:
        sharpe_ratio_original = np.inf if portfolio_actual_returns >= 0 else -np.inf
    else:
        sharpe_ratio_original = portfolio_actual_returns / original_std
        
    # Mathematically correct Sharpe ratio: daily return / daily standard deviation
    # daily standard deviation = sqrt(portfolio_variance)
    daily_std = np.sqrt(portfolio_actual_variance) if portfolio_actual_variance > 0 else 1e-8
    sharpe_ratio_corrected = portfolio_actual_returns / daily_std

    ret_dict = {
        'weights': w,
        'predicted_returns': portfolio_predicted_returns,
        'predicted_variance': portfolio_STD,
        'actual_returns': portfolio_actual_returns,
        'actual_variance': portfolio_actual_variance,
        'sharpe_ratio_original': sharpe_ratio_original,
        'sharpe_ratio_corrected': sharpe_ratio_corrected
    }

    return ret_dict

def run_backtest(windows, horizons, name, lam1=0.5, lam2=2.0):
    print(f"Running rolling backtest for {name}...")
    returns = []
    variances = []
    sr_original = []
    sr_corrected = []
    
    # Backtest over the last 5 years (60 months rebalancing)
    start_idx = len(horizons) - 72
    end_idx = len(horizons) - 12
    
    for i in range(start_idx, end_idx):
        opt_results = scipy_opt(windows[i], horizons[i], lam1, lam2)
        returns.append(opt_results['actual_returns'])
        variances.append(opt_results['actual_variance'])
        sr_original.append(opt_results['sharpe_ratio_original'])
        sr_corrected.append(opt_results['sharpe_ratio_corrected'])
        
    timestamps = [horizons[i].index[-1] for i in range(start_idx, end_idx)]
    
    results_df = pd.DataFrame(
        data=np.array([returns, variances, sr_original, sr_corrected]).T,
        columns=['Returns', 'Variance', 'Sharpe Ratio (Original)', 'Sharpe Ratio (Corrected)'],
        index=timestamps
    )
    
    results_df.index.name = 'Date'
    results_df.to_csv(f"{name}_Portfolio_Returns.csv")
    print(f"Saved {name} backtest results to '{name}_Portfolio_Returns.csv'")
    return results_df

def calculate_equity(returns_list):
    equity = [100.0]
    for r in returns_list[1:]:
        equity.append(equity[-1] * math.exp(r))
    return equity

def main():
    required_files = [
        "final_closing_prices_pivot.csv",
        "MovingAverage.csv",
        "LR_Predicted_Prices.csv",
        "LR_Actual_Prices.csv",
        "PCA_Predicted_Prices1.csv",
        "PCA_Actual_Prices1.csv"
    ]
    
    for f in required_files:
        if not os.path.exists(f):
            raise FileNotFoundError(f"Missing required file '{f}'. Please run baseline and LSTM models first.")
            
    print("Loading datasets for portfolio optimization...")
    # Load Closing Prices & compute daily log returns
    df_close = pd.read_csv("final_closing_prices_pivot.csv", index_col=0, parse_dates=True)
    df_returns = df_close.apply(lambda x: np.log(x) - np.log(x.shift(1))).dropna()
    
    # Load LR Predicted & Actual prices & compute log returns
    lr_pred_prices = pd.read_csv("LR_Predicted_Prices.csv", index_col=0, parse_dates=True)
    lr_act_prices = pd.read_csv("LR_Actual_Prices.csv", index_col=0, parse_dates=True)
    lr_pred_returns = lr_pred_prices.apply(lambda x: np.log(x) - np.log(x.shift(1))).dropna()
    lr_act_returns = lr_act_prices.apply(lambda x: np.log(x) - np.log(x.shift(1))).dropna()
    
    # Load LSTM Predicted & Actual prices & compute log returns
    lstm_pred_prices = pd.read_csv("PCA_Predicted_Prices1.csv", index_col=0, parse_dates=True)
    lstm_act_prices = pd.read_csv("PCA_Actual_Prices1.csv", index_col=0, parse_dates=True)
    lstm_pred_returns = lstm_pred_prices.apply(lambda x: np.log(x) - np.log(x.shift(1))).dropna()
    lstm_act_returns = lstm_act_prices.apply(lambda x: np.log(x) - np.log(x.shift(1))).dropna()
    
    # Generate windows
    # lookback 12 months, horizon 1 month, step 1 month
    ma_windows, ma_horizons = windowGenerator(df_returns, 12, 1, 1)
    lr_windows, lr_horizons = windowGenerator(lr_pred_returns, 12, 1, 1)
    lstm_windows, lstm_horizons = windowGenerator(lstm_pred_returns, 12, 1, 1)
    
    # We must align the actual horizon returns to match the index of the predicted returns
    # (since the prediction starts later than the raw series)
    lr_act_horizons = windowGenerator(lr_act_returns, 12, 1, 1)[1]
    lstm_act_horizons = windowGenerator(lstm_act_returns, 12, 1, 1)[1]
    
    # Run backtests
    ma_results = run_backtest(ma_windows, ma_horizons, "MA")
    lr_results = run_backtest(lr_windows, lr_act_horizons, "LR")
    lstm_results = run_backtest(lstm_windows, lstm_act_horizons, "LSTM")
    
    # Compute Equity Growth
    ma_equity = calculate_equity(ma_results['Returns'].tolist())
    lr_equity = calculate_equity(lr_results['Returns'].tolist())
    lstm_equity = calculate_equity(lstm_results['Returns'].tolist())
    
    # Plot and save Equity Curve
    plt.figure(figsize=(12, 7))
    timestamps = ma_results.index
    plt.plot(timestamps, ma_equity, label="Moving Average", color="blue", linewidth=2)
    plt.plot(timestamps, lr_equity, label="Linear Regression", color="orange", linewidth=2)
    plt.plot(timestamps, lstm_equity, label="PCA-LSTM", color="green", linewidth=2)
    plt.title("Equity Growth Curve (Initial $100)", fontsize=14, fontweight="bold")
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Equity Value ($)", fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.6)
    
    plot_filename = "equity_growth_curve.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Equity curve plot saved to '{plot_filename}'")
    
    # Print summary performance metrics
    print("\n" + "="*50)
    print("BACKTEST STRATEGY PERFORMANCE SUMMARY")
    print("="*50)
    for name, equity_series, results_df in [("Moving Average", ma_equity, ma_results), 
                                            ("Linear Regression", lr_equity, lr_results), 
                                            ("PCA-LSTM", lstm_equity, lstm_results)]:
        final_equity = equity_series[-1]
        mean_return = results_df['Returns'].mean()
        # Correct Sharpe ratio is calculated over the full returns series
        ann_return = mean_return * 12 # monthly to annual
        ann_vol = results_df['Returns'].std() * np.sqrt(12)
        portfolio_sr = ann_return / ann_vol if ann_vol > 0 else 0
        
        print(f"Strategy: {name}")
        print(f"  Final Equity Value: ${final_equity:.2f}")
        print(f"  Annualized Return:  {ann_return*100:.2f}%")
        print(f"  Annualized Volatility: {ann_vol*100:.2f}%")
        print(f"  Overall Sharpe Ratio: {portfolio_sr:.4f}")
        print("-"*50)

if __name__ == "__main__":
    main()
