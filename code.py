import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
import fitz  # PyMuPDF

# Function to load uploaded financial data
def load_financials(file):
    return pd.read_csv(file, index_col=0)

# Function to load uploaded share price data
def load_share_prices(file):
    return pd.read_csv(file, index_col=0, parse_dates=True)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(pdf_file)
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

# Function to find specific financial data in the extracted text
def find_financial_data_in_text(text, key):
    lines = text.split('\n')
    for line in lines:
        if key in line:
            parts = line.split()
            for part in parts:
                try:
                    return float(part.replace(',', '').replace('$', ''))
                except ValueError:
                    continue
    return None

# Function to check and fetch required financial data
def get_financial_data(financials, key, pdf_text):
    if key in financials.index:
        return financials.loc[key]
    else:
        value = find_financial_data_in_text(pdf_text, key)
        if value is not None:
            return value
        else:
            st.error(f"{key} not found in the financials or PDF statements.")
            return None

# Function to calculate moat indicators
def calculate_moat_indicators(financials, pdf_text):
    net_income = get_financial_data(financials, 'Net Income', pdf_text)
    total_assets = get_financial_data(financials, 'Total Assets', pdf_text)
    current_liabilities = get_financial_data(financials, 'Current Liabilities', pdf_text)
    
    if net_income is not None and total_assets is not None and current_liabilities is not None:
        roic = net_income / (total_assets - current_liabilities)
        return roic.mean()
    return None

# Function to analyze investments in times of strength or distress
def analyze_investments(financials, pdf_text):
    net_income = get_financial_data(financials, 'Net Income', pdf_text)
    capital_expenditures = get_financial_data(financials, 'Capital Expenditures', pdf_text)
    
    if net_income is not None and capital_expenditures is not None:
        performance = net_income.pct_change()
        high_performance = performance > performance.median()
        investments_in_high = capital_expenditures[high_performance].mean()
        investments_in_low = capital_expenditures[~high_performance].mean()
        return investments_in_high, investments_in_low
    return None, None

# Function to assess returns relative to industry standard
def assess_returns(share_prices):
    stock_returns = share_prices['Close'].pct_change().mean()
    # Placeholder for industry average calculation
    industry_average = 0.05
    return stock_returns, industry_average

# Function to assess growth methodologies
def assess_growth(financials, pdf_text):
    total_revenue = get_financial_data(financials, 'Total Revenue', pdf_text)
    
    if total_revenue is not None:
        cagr = (total_revenue.iloc[-1] / total_revenue.iloc[0])**(1/len(total_revenue)) - 1
        return cagr
    return None

# Function to define valuation
def define_valuation(financials, pdf_text):
    market_cap = get_financial_data(financials, 'Market Cap', pdf_text)
    book_value = get_financial_data(financials, 'Book Value', pdf_text)
    shares_outstanding = get_financial_data(financials, 'Shares Outstanding', pdf_text)
    
    if market_cap is not None and book_value is not None and shares_outstanding is not None:
        intrinsic_value = book_value * shares_outstanding
        return market_cap, intrinsic_value
    return None, None

# Function to conduct stress test
def conduct_stress_test(financials, pdf_text):
    total_revenue = get_financial_data(financials, 'Total Revenue', pdf_text)
    
    if total_revenue is not None:
        stress_scenarios = total_revenue * 0.9, total_revenue * 0.8
        return stress_scenarios
    return None

# Function to find operating leverage
def find_operating_leverage(financials, pdf_text):
    operating_expenses = get_financial_data(financials, 'Operating Expenses', pdf_text)
    cost_of_revenue = get_financial_data(financials, 'Cost of Revenue', pdf_text)
    
    if operating_expenses is not None and cost_of_revenue is not None:
        fixed_costs = operating_expenses.mean()
        variable_costs = cost_of_revenue.mean()
        operating_leverage = fixed_costs / (fixed_costs + variable_costs)
        return operating_leverage
    return None

# Function to pronounce a verdict
def pronounce_verdict(roic, stock_returns, industry_average, cagr, market_cap, intrinsic_value, operating_leverage):
    verdict = "Invest" if roic and roic > 0.1 and stock_returns > industry_average and cagr and cagr > 0.05 and market_cap and market_cap < intrinsic_value and operating_leverage and operating_leverage > 0.5 else "Do Not Invest"
    return verdict

# Streamlit UI
st.title("EquiIntel: Comprehensive Equity Analysis AI")

uploaded_financials = st.file_uploader("Upload Financial Statements CSV", type="csv")
uploaded_share_prices = st.file_uploader("Upload Share Prices CSV", type="csv")
uploaded_statements_pdf = st.file_uploader("Upload Additional Financial Data PDF", type="pdf")

if uploaded_financials and uploaded_share_prices:
    financials = load_financials(uploaded_financials)
    share_prices = load_share_prices(uploaded_share_prices)
    pdf_text = extract_text_from_pdf(uploaded_statements_pdf) if uploaded_statements_pdf else ""
    
    roic = calculate_moat_indicators(financials, pdf_text)
    investments_in_high, investments_in_low = analyze_investments(financials, pdf_text)
    stock_returns, industry_average = assess_returns(share_prices)
    cagr = assess_growth(financials, pdf_text)
    market_cap, intrinsic_value = define_valuation(financials, pdf_text)
    stress_scenarios = conduct_stress_test(financials, pdf_text)
    operating_leverage = find_operating_leverage(financials, pdf_text)
    verdict = pronounce_verdict(roic, stock_returns, industry_average, cagr, market_cap, intrinsic_value, operating_leverage)

    st.write(f"ROIC: {roic}")
    st.write(f"Investments in times of high performance: {investments_in_high}")
    st.write(f"Investments in times of low performance: {investments_in_low}")
    st.write(f"Stock returns: {stock_returns}")
    st.write(f"Industry average returns: {industry_average}")
    st.write(f"CAGR: {cagr}")
    st.write(f"Market Cap: {market_cap}")
    st.write(f"Intrinsic Value: {intrinsic_value}")
    st.write(f"Stress Scenarios: {stress_scenarios}")
    st.write(f"Operating Leverage: {operating_leverage}")
    st.write(f"Verdict: {verdict}")
