import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_guide_pdf():
    pdf_filename = "Stock_Forecasting_Portfolio_Optimization_Guide.pdf"
    print(f"Generating PDF: {pdf_filename}...")
    
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
    
    # Custom styles to look premium
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=18,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2D3748'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=10
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=6
    )
    
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1A202C'),
        backColor=colors.HexColor('#EDF2F7'),
        borderPadding=8,
        spaceBefore=8,
        spaceAfter=8
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2C5282')
    )

    story = []
    
    # ------------------ COVER PAGE / HEADER ------------------
    story.append(Paragraph("Stock Forecasting and Portfolio Optimization", title_style))
    story.append(Paragraph("A Complete Guide for Beginners and Interview Preparation", subtitle_style))
    
    # Divider line
    divider = Table([[""]], colWidths=[7 * inch])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 2, colors.HexColor('#2B6CB0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0)
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))
    
    # Callout Box: Elevator Pitch
    pitch_text = (
        "<b>Elevator Pitch:</b> This project builds an end-to-end quantitative trading and asset allocation "
        "pipeline. It downloads 19 years of daily stock prices for 61 S&P 500 equities, creates stationary technical "
        "features, reduces features via Principal Component Analysis (PCA), and trains a deep learning LSTM model to "
        "predict prices 22 days out. Finally, these predictions are optimized using a sparse L1-regularized mean-variance "
        "allocator, achieving superior risk-adjusted returns (Sharpe ratio) over Moving Average and Linear Regression baselines."
    )
    callout_table = Table([[Paragraph(pitch_text, callout_style)]], colWidths=[6.8 * inch])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF8FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BEE3F8')),
        ('PADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 15))
    
    # ------------------ SECTION 1 ------------------
    story.append(Paragraph("1. Core Financial Concepts (The Foundation)", h1_style))
    story.append(Paragraph(
        "Before diving into machine learning, it is critical to understand the financial data layer. Stock prices "
        "themselves are notoriously hard to predict directly because they are non-stationary (their mean and variance "
        "change over time). To train stable models, we must engineer features that represent relative changes.",
        body_style
    ))
    
    story.append(Paragraph("<b>Key Features Computed:</b>", h2_style))
    story.append(Paragraph("&bull; <b>Daily Returns</b>: The percentage change in Close price from day t-1 to t. It represents the daily growth rate of the asset.", bullet_style))
    story.append(Paragraph("&bull; <b>20-Day Returns</b>: The percentage change in Close price over the last month (20 trading days). This captures medium-term stock momentum.", bullet_style))
    story.append(Paragraph("&bull; <b>20-Day Volatility</b>: The rolling standard deviation of daily returns over the last 20 days. This measures the asset's risk/uncertainty.", bullet_style))
    story.append(Paragraph("&bull; <b>Rolling Z-Scores</b>: Normalized values computed by subtracting the 252-day (1 trading year) rolling mean and dividing by the rolling standard deviation.", bullet_style))
    
    # Callout: Non-stationarity
    stationarity_text = (
        "<b>Interview Concept - Non-Stationarity:</b> Financial time series models must be stationary to ensure that the "
        "statistical properties (mean, variance) are constant over time. Z-scoring daily returns and volatilities over "
        "a rolling window removes trends, ensuring the LSTM learns structural relationships rather than arbitrary nominal changes."
    )
    st_table = Table([[Paragraph(stationarity_text, callout_style)]], colWidths=[6.8 * inch])
    st_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(st_table)
    story.append(Spacer(1, 15))
    
    # ------------------ SECTION 2 ------------------
    story.append(Paragraph("2. Dimensionality Reduction & PCA", h1_style))
    story.append(Paragraph(
        "With 61 stocks and 11 features per stock, our model receives 671 inputs every day. Feeding this many "
        "highly correlated features into a neural network causes overfitting and slow training. We resolve this "
        "using Principal Component Analysis (PCA).",
        body_style
    ))
    
    story.append(Paragraph("<b>Why PCA is crucial in Finance:</b>", h2_style))
    story.append(Paragraph("&bull; <b>Multicollinearity Removal</b>: Equity markets are highly co-dependent (e.g., tech stocks move together). PCA decorrelates the features by projecting them onto orthogonal principal axes.", bullet_style))
    story.append(Paragraph("&bull; <b>Noise Reduction</b>: Most of the 671 features contain redundant information or noise. By selecting the top 61 principal components, we compress the data while retaining ~95% of the information variance.", bullet_style))
    story.append(Paragraph("&bull; <b>Data Leakage Prevention</b>: PCA scalers are fit ONLY on the training dataset. We apply `transform` on the test set using the train-fitted PCA, ensuring future test information never leaks into the training phase.", bullet_style))
    
    story.append(PageBreak())
    
    # ------------------ SECTION 3 ------------------
    story.append(Paragraph("3. Deep Learning Price Forecasting (PCA-LSTM)", h1_style))
    story.append(Paragraph(
        "Long Short-Term Memory (LSTM) networks are a specialized type of Recurrent Neural Network (RNN) designed for "
        "learning sequence relationships without suffering from vanishing gradients.",
        body_style
    ))
    
    story.append(Paragraph("<b>Model Architecture:</b>", h2_style))
    story.append(Paragraph("&bull; <b>Sequence Prep</b>: Input sequences are shaped as `(batch_size, 252, 59)`, representing 252 days of historical daily PCA features across all stocks.", bullet_style))
    story.append(Paragraph("&bull; <b>LSTM Layer 1</b>: 800 units, returns sequences. This extracts low-level chronological patterns.", bullet_style))
    story.append(Paragraph("&bull; <b>LSTM Layer 2</b>: 600 units, collapses sequence. This aggregates temporal information into high-level features.", bullet_style))
    story.append(Paragraph("&bull; <b>Dense Layer 3 & 4</b>: 2 Dense layers of size `1298` (22 days * 59 stocks) with ReLU and Sigmoid activations. The model outputs a flattened array representing the forecasted prices for all 59 stocks over the next 22 days (1 trading month).", bullet_style))
    
    # ------------------ SECTION 4 ------------------
    story.append(Paragraph("4. Sparse L1-Regularized Portfolio Optimization", h1_style))
    story.append(Paragraph(
        "After obtaining predicted returns for the next month, we construct our portfolio using a regularized "
        "mean-variance optimizer to find the optimal stock weights (w).",
        body_style
    ))
    
    story.append(Paragraph("<b>The Objective Function:</b>", h2_style))
    story.append(Paragraph(
        "We solve the following optimization problem at the beginning of each month:<br/>"
        "<b>Minimize:</b>  - [ w^T &mu; - &lambda;_1 (w^T &Sigma; w) + &lambda;_2 ||w||_1 ]<br/>"
        "Where:<br/>"
        "&bull; <b>w</b>: Vector of stock weights.<br/>"
        "&bull; <b>&mu;</b>: Expected predicted stock returns.<br/>"
        "&bull; <b>&Sigma;</b>: Expected covariance matrix.<br/>"
        "&bull; <b>&lambda;_1</b>: Risk-aversion coefficient (0.5).<br/>"
        "&bull; <b>&lambda;_2</b>: L1-regularization coefficient (2.0) enforcing sparsity.",
        body_style
    ))
    
    story.append(Paragraph("<b>Constraints & Real-world Bounds:</b>", h2_style))
    story.append(Paragraph("&bull; <b>Long-only constraint</b>: Bounded weights between 0 and 1 ($0 \\le w_i \\le 1$), preventing short-selling.", bullet_style))
    story.append(Paragraph("&bull; <b>Fully invested constraint</b>: Sum of weights must equal 1 ($\sum w_i = 1$), ensuring all capital is allocated.", bullet_style))
    story.append(Paragraph("&bull; <b>L1-Regularization (Sparsity)</b>: Instead of allocating tiny fractions to all stocks, the L1 penalty forces weights of less-favorable stocks to exactly zero. This selects a concentrated basket of the top 5-10 stocks, lowering transaction fees and complexity.", bullet_style))
    
    story.append(Spacer(1, 10))
    story.append(PageBreak())
    
    # ------------------ SECTION 5 ------------------
    story.append(Paragraph("5. Rolling Backtests and Bug Fixes", h1_style))
    story.append(Paragraph(
        "To test how our strategies perform in real-world conditions, we simulate a monthly rebalanced portfolio "
        "over a 5-year rolling window.",
        body_style
    ))
    
    story.append(Paragraph("<b>The Sharpe Ratio Bug Fix:</b>", h2_style))
    story.append(Paragraph(
        "In the original repository's codebase, the Sharpe ratio was calculated as:<br/>"
        "<code>sharpe_ratio = portfolio_actual_returns / np.std(portfolio_actual_variance)</code><br/>"
        "Since `portfolio_actual_variance` is a scalar float value, its standard deviation is always 0. "
        "This led to a division by zero warning, outputting `inf` or `-inf` Sharpe ratios in their backtest logs.<br/>"
        "<b>Our Correction:</b> We implemented the true Sharpe ratio, dividing the mean daily return by the daily standard deviation (square root of variance):",
        body_style
    ))
    story.append(Paragraph("<code>Corrected Sharpe = portfolio_actual_returns / sqrt(portfolio_actual_variance)</code>", code_style))

    # ------------------ SECTION 6 ------------------
    story.append(Paragraph("6. Key Interview Questions & Answers", h1_style))
    
    story.append(Paragraph("<b>Q1: Why did you use PCA before the LSTM?</b>", h2_style))
    story.append(Paragraph("<i>Answer:</i> Financial features are highly collinear and noisy. Feeding 671 raw features directly into an LSTM causes overfitting and slows down training. PCA decorrelates inputs and reduces the dimensions to 61 components, removing multicollinearity while retaining 95% of the information variance.", body_style))
    
    story.append(Paragraph("<b>Q2: What is the benefit of adding an L1 penalty to portfolio optimization?</b>", h2_style))
    story.append(Paragraph("<i>Answer:</i> A standard Markowitz optimizer creates highly fragmented portfolios with tiny weights across all assets. Adding an L1 penalty (|w|_1) drives the weights of weaker assets to exactly zero, resulting in a sparse portfolio. This reduces transaction costs and concentrates capital in the strongest ideas.", body_style))
    
    story.append(Paragraph("<b>Q3: What was the main technical issue you identified in the original repository?</b>", h2_style))
    story.append(Paragraph("<i>Answer:</i> The original code calculated the Sharpe ratio by dividing returns by the standard deviation of a scalar variance, which resulted in a divide-by-zero warning and infinite values. We corrected this by using the square root of the portfolio variance to calculate the true Sharpe ratio.", body_style))
    
    # Build Document
    doc.build(story)
    print(f"PDF Guide generated successfully as '{pdf_filename}'!")

if __name__ == "__main__":
    create_guide_pdf()
