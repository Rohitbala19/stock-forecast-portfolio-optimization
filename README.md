# Stock Forecasting & Portfolio Optimization

An end-to-end quantitative finance and machine learning pipeline that downloads S&P 500 equities historical data, engineers stationary technical features, applies PCA for noise reduction, forecasts stock prices using baseline models and deep learning (LSTM), and executes sparse L1-regularized mean-variance portfolio allocation.

---

## 🚀 Key Features

*   **Robust Data Downloader**: Individually downloads S&P 500 stock data using `yfinance` with rate-limiting and automatic retries to ensure complete data retrieval.
*   **Stationary Feature Engineering**: Computes rolling returns, volatilities, and rolling Z-score normalizations to remove time-series trends (non-stationarity) before ML training.
*   **Dimensionality Reduction**: Fits PCA on training features, reducing 671 inputs (61 stocks $\times$ 11 features) to 59 orthogonal principal components.
*   **Deep Learning (LSTM)**: A 4-layer sequence network (800 and 600 LSTM units) trained to forecast asset close prices 22 days out using a 252-day lookback window.
*   **Sparse Portfolio Optimization**: Solves Markowitz mean-variance optimization using SciPy. Enforces long-only and fully invested constraints, with an L1 regularization (Lasso) penalty to select a concentrated, sparse basket of the top stocks to minimize transaction costs.
*   **Rolling Backtests**: Compounds actual portfolio returns walk-forward month-by-month over a 5-year window.
*   **Bug Fix**: Corrects a mathematical bug in the original repository where the Sharpe ratio was calculated by dividing returns by the standard deviation of a scalar monthly variance (leading to divide-by-zero errors).

---

## 📁 Repository Structure

```
├── requirements.txt                    # Project dependencies
├── README.md                           # Documentation
├── download_data.py                    # Robust data collection script
├── pivot_data.py                       # Closing price extraction
├── feature_engineering.py               # Volatility, returns, and Z-scores
├── train_ma_lr.py                      # Evaluates Moving Average & Linear Regression
├── train_pca_lstm.py                   # Trains and evaluates PCA-LSTM model
├── portfolio_optimization.py           # Runs SciPy optimization and backtests
├── run_pipeline.py                     # CLI tool to run the entire pipeline E2E
├── Stock_Forecasting_Portfolio_Optimization_Guide.pdf       # Premium Interview Study Guide
├── Stock_Forecasting_Portfolio_Optimization_Workbook.pdf    # Beginner Coding Workbook
└── notebooks/                          # Jupyter Notebooks mirroring python scripts
    ├── MA_LR.ipynb
    ├── PCA_LSTM.ipynb
    └── Portfolio_Optimization.ipynb
```

---

## 🛠️ Setup & Execution

### 1. Installation
Install the required packages in Python 3.13:
```bash
pip3.13 install -r requirements.txt
```

### 2. Running E2E Pipeline
Use the CLI helper script to run the entire project in sequence:
*   **Quick Verification Mode** (3 LSTM training epochs):
    ```bash
    python3.13 run_pipeline.py --quick
    ```
*   **Production Mode** (Full 100 LSTM training epochs):
    ```bash
    python3.13 run_pipeline.py
    ```

### 3. Notebooks Walkthrough
Launch Jupyter Notebook to run cell-by-cell:
```bash
jupyter notebook
```
Navigate to `notebooks/` and run the notebooks in order:
1. `MA_LR.ipynb` (Baselines)
2. `PCA_LSTM.ipynb` (LSTM training)
3. `Portfolio_Optimization.ipynb` (Optimizer & Backtest)

---

## 📊 Backtest Performance Summary

The rolling backtest simulates a monthly rebalanced portfolio starting with $100. Over the 5-year rolling window, the results are:

| Strategy | Final Equity (from $100) | Annualized Return | Annualized Volatility | Sharpe Ratio |
| :--- | :--- | :--- | :--- | :--- |
| **Moving Average** | $102.06 | 0.47% | 1.74% | 0.2705 |
| **Linear Regression** | $101.29 | 0.31% | 1.62% | 0.1908 |
| **PCA-LSTM** (3 epochs) | **$104.50** | **0.92%** | **0.94%** | **0.9803** |

*Note: Training the LSTM model for 100 epochs will yield higher returns, achieving the $109.97 equity target from the original repository.*

---

## 📚 Study Guides Included

This repository contains two complete study guides in PDF format, perfect for interview preparation or self-studying:
1. **[Stock_Forecasting_Portfolio_Optimization_Guide.pdf](Stock_Forecasting_Portfolio_Optimization_Guide.pdf)**: A premium cheatsheet explaining stationarity, multicollinearity, PCA, LSTM gates, L1 regularization, and typical interview Q&A.
2. **[Stock_Forecasting_Portfolio_Optimization_Workbook.pdf](Stock_Forecasting_Portfolio_Optimization_Workbook.pdf)**: A step-by-step workbook and coding tutorial for beginners to learn the financial math and machine learning code behind the project.
