import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_workbook_pdf():
    pdf_filename = "Stock_Forecasting_Portfolio_Optimization_Workbook.pdf"
    print(f"Generating PDF Study Workbook: {pdf_filename}...")
    
    # Page setup
    margin = 0.75 * inch
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=margin,
        leftMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles for workbook
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#7F8C8D'),
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#16A085'),
        spaceBefore=18,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2C3E50'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=10
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#2C3E50'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=5
    )
    
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#2C3E50'),
        backColor=colors.HexColor('#F8F9F9'),
        borderPadding=6,
        spaceBefore=6,
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#16A085')
    )

    story = []
    
    # ------------------ COVER PAGE / HEADER ------------------
    story.append(Paragraph("Stock Forecasting & Portfolio Optimization", title_style))
    story.append(Paragraph("A Step-by-Step Study Guide & Coding Workbook for Beginners", subtitle_style))
    
    # Divider line
    divider = Table([[""]], colWidths=[7 * inch])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 2, colors.HexColor('#16A085')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0)
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))
    
    # Intro Callout
    intro_text = (
        "<b>Welcome Student!</b> This study workbook is designed to take you from a complete beginner in "
        "quantitative finance to someone who understands data collection, feature engineering, neural network "
        "training, and mathematical portfolio optimization. Follow this guide module-by-module to master the "
        "principles of building modern financial algorithms."
    )
    callout_table = Table([[Paragraph(intro_text, callout_style)]], colWidths=[6.8 * inch])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#E8F8F5')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#A3E4D7')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 15))
    
    # ------------------ MODULE 1 ------------------
    story.append(Paragraph("Module 1: Environment & Setup", h1_style))
    story.append(Paragraph(
        "To build financial models, we need a programming environment. We use <b>Python 3</b> and a list of open-source "
        "packages. Let's learn what these packages do:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>pandas</b>: Used to load, clean, slice, and pivot tabular time-series datasets.", bullet_style))
    story.append(Paragraph("&bull; <b>numpy</b>: Handles fast vector and matrix calculations (arrays).", bullet_style))
    story.append(Paragraph("&bull; <b>yfinance</b>: Fetches historical stock data directly from Yahoo Finance API.", bullet_style))
    story.append(Paragraph("&bull; <b>scikit-learn</b>: Handles data scaling, splitting, and PCA dimensionality reduction.", bullet_style))
    story.append(Paragraph("&bull; <b>tensorflow</b>: The deep learning framework used to construct and train the LSTM model.", bullet_style))
    story.append(Paragraph("&bull; <b>scipy</b>: Holds optimization solvers to find the optimal stock portfolio weights.", bullet_style))
    
    story.append(Paragraph("<b>Try it Yourself (Exercise):</b>", h2_style))
    story.append(Paragraph("Install these dependencies using pip in your terminal:", body_style))
    story.append(Paragraph("<code>pip install pandas numpy scikit-learn tensorflow scipy yfinance matplotlib notebook</code>", code_style))
    story.append(Spacer(1, 10))
    
    # ------------------ MODULE 2 ------------------
    story.append(Paragraph("Module 2: Downloading & Cleaning Data", h1_style))
    story.append(Paragraph(
        "A quantitative model is only as good as its data. We query historical daily prices for 61 stocks. "
        "Financial APIs can sometimes drop connections or block requests if called too fast.",
        body_style
    ))
    story.append(Paragraph("<b>What you will learn:</b>", h2_style))
    story.append(Paragraph("&bull; <b>OHLCV</b>: Open, High, Low, Close, Volume. These are the 5 standard daily metrics for any asset.", bullet_style))
    story.append(Paragraph("&bull; <b>Rate Limiting</b>: We add `time.sleep(1.0)` between requests so the Yahoo Finance server does not throttle or block our IP address.", bullet_style))
    story.append(Paragraph("&bull; <b>Pivoting</b>: Extracting the `Close` prices for all stocks and storing them as a single clean grid indexed by `Date`.", bullet_style))
    
    story.append(Paragraph("<b>Coding Challenge:</b>", h2_style))
    story.append(Paragraph(
        "Write a Python function to read `stock_new.csv` and extract only the Close prices of 'AAPL' and 'MSFT'. "
        "Save this pivoted dataframe as a new CSV file.",
        body_style
    ))
    story.append(PageBreak())
    
    # ------------------ MODULE 3 ------------------
    story.append(Paragraph("Module 3: Preprocessing & Technical Features", h1_style))
    story.append(Paragraph(
        "Raw stock prices cannot be fed directly into machine learning models because they are non-stationary. "
        "Instead, we calculate normalized changes (features).",
        body_style
    ))
    story.append(Paragraph("<b>Understanding the Mathematics:</b>", h2_style))
    story.append(Paragraph("&bull; <b>Daily Returns</b>: $R_t = (C_t - C_{t-1}) / C_{t-1}$. Measures daily price movement.", bullet_style))
    story.append(Paragraph("&bull; <b>20-Day Volatility</b>: Rolling standard deviation of daily returns over the last 20 days. Measures risk.", bullet_style))
    story.append(Paragraph("&bull; <b>Z-Scores</b>: Formula: $Z_t = (value_t - mean_{rolling}) / std_{rolling}$. Shifts values to have a mean of 0 and standard deviation of 1. We shift the rolling mean and std by 1 day (`shift(1)`) to avoid data leakage.", bullet_style))
    
    story.append(Paragraph("<b>Try it Yourself (Exercise):</b>", h2_style))
    story.append(Paragraph(
        "Compute a 20-day simple moving average of Close prices in pandas. Hint: use `df['Close'].rolling(20).mean()`.",
        body_style
    ))
    
    # ------------------ MODULE 4 ------------------
    story.append(Paragraph("Module 4: Machine Learning & PCA-LSTM", h1_style))
    story.append(Paragraph(
        "LSTMs (Long Short-Term Memory) are deep learning networks capable of remembering long-term historical context "
        "for forecasting.",
        body_style
    ))
    story.append(Paragraph("<b>Key Machine Learning Concepts:</b>", h2_style))
    story.append(Paragraph("&bull; <b>PCA (Principal Component Analysis)</b>: Compresses the 671 features down to 61 components, removing multicollinearity (correlated inputs) and noise.", bullet_style))
    story.append(Paragraph("&bull; <b>Sequence Generation</b>: We take a 252-day lookback window of features to predict a 22-day horizon of future prices.", bullet_style))
    story.append(Paragraph("&bull; <b>LSTM Layers</b>: Two LSTM layers (800 and 600 units) extract sequential patterns, and Dense layers map them to the 22-day forecasted prices.", bullet_style))
    
    story.append(Paragraph("<b>Coding Challenge:</b>", h2_style))
    story.append(Paragraph(
        "Write a TensorFlow Sequential model with an Input layer of shape `(252, 61)` and a single LSTM layer of 128 units.",
        body_style
    ))
    story.append(Spacer(1, 10))
    story.append(PageBreak())
    
    # ------------------ MODULE 5 ------------------
    story.append(Paragraph("Module 5: Portfolio Optimization & Allocation", h1_style))
    story.append(Paragraph(
        "Once we have the predicted returns for the next month, we need to decide how much money to invest "
        "in each stock. We use mean-variance optimization (Markowitz Portfolio Theory).",
        body_style
    ))
    story.append(Paragraph("<b>Objective & Regularization:</b>", h2_style))
    story.append(Paragraph(
        "We maximize portfolio return and minimize portfolio variance, subject to constraints. We also add an "
        "<b>L1-Regularization (Lasso)</b> penalty to the optimizer. The L1 penalty forces the weights of less "
        "optimal stocks to exactly zero. This creates a <b>sparse portfolio</b> consisting of only the top 5-10 "
        "best stocks, which is highly practical as it lowers transaction costs.",
        body_style
    ))
    story.append(Paragraph("<b>Constraints:</b>", h2_style))
    story.append(Paragraph("&bull; <b>Long-only</b>: Weights must be between 0 and 1 (no short-selling).", bullet_style))
    story.append(Paragraph("&bull; <b>Fully invested</b>: Weights must sum to 1 (all cash is allocated).", bullet_style))
    
    story.append(Paragraph("<b>Try it Yourself (Exercise):</b>", h2_style))
    story.append(Paragraph(
        "Run the SciPy minimize function on a basic quadratic function $f(x) = (x-3)^2$ to find its minimum. "
        "Verify that it converges to $x=3$.",
        body_style
    ))
    
    # ------------------ MODULE 6 ------------------
    story.append(Paragraph("Module 6: Backtesting & Performance Analysis", h1_style))
    story.append(Paragraph(
        "A backtest simulates how the model would have performed historically. We rebalance the portfolio "
        "monthly over a 5-year rolling window.",
        body_style
    ))
    story.append(Paragraph("<b>Analyzing the Output:</b>", h2_style))
    story.append(Paragraph("&bull; <b>Compounded Return</b>: We start with $100 and compound actual monthly returns using $equity_t = equity_{t-1} \\times e^{r_t}$.", bullet_style))
    story.append(Paragraph("&bull; <b>Sharpe Ratio</b>: Measures risk-adjusted return. Formula: $\\text{Sharpe} = R_p / \\sigma_p$ (return divided by standard deviation). A higher Sharpe ratio indicates better return per unit of risk.", bullet_style))
    
    story.append(Paragraph("<b>Study Check (The Sharpe Bug):</b>", h2_style))
    story.append(Paragraph(
        "Explain why dividing the return by the standard deviation of a scalar monthly variance (which is always 0) "
        "leads to an error. How did we resolve this in our codebase?",
        body_style
    ))
    
    # Build Document
    doc.build(story)
    print(f"Workbook PDF generated successfully as '{pdf_filename}'!")

if __name__ == "__main__":
    create_workbook_pdf()
