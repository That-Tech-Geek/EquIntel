import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from PyPDF2 import PdfReader

# Function to load uploaded share price data
def load_share_prices(file):
    return pd.read_csv(file, index_col=0, parse_dates=True)

# Function to extract text from PDF using PyPDF2
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
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
    st.write(f"Could not find {key} in the extracted text.")
    return None


# Function to get financial data from PDF text
def get_financial_data_from_pdf(pdf_text, keys):
    data = {}
    for key in keys:
        data[key] = find_financial_data_in_text(pdf_text, key)
    return pd.Series(data)

# Function to calculate moat indicators
def calculate_moat_indicators(financials):
    net_income = financials.get('Net Income')
    total_assets = financials.get('Total Assets')
    current_liabilities = financials.get('Current Liabilities')
    
    if net_income is not None and total_assets is not None and current_liabilities is not None:
        roic = net_income / (total_assets - current_liabilities)
        return roic
    return None

# Function to analyze investments in times of strength or distress
def analyze_investments(financials):
    net_income = financials.get('Net Income')
    capital_expenditures = financials.get('Capital Expenditures')
    
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
def assess_growth(financials):
    total_revenue = financials.get('Total Revenue')
    
    if total_revenue is not None:
        cagr = (total_revenue.iloc[-1] / total_revenue.iloc[0])**(1/len(total_revenue)) - 1
        return cagr
    return None

# Function to define valuation
def define_valuation(financials):
    market_cap = financials.get('Market Cap')
    book_value = financials.get('Book Value')
    shares_outstanding = financials.get('Shares Outstanding')
    
    if market_cap is not None and book_value is not None and shares_outstanding is not None:
        intrinsic_value = book_value * shares_outstanding
        return market_cap, intrinsic_value
    return None, None

# Function to conduct stress test
def conduct_stress_test(financials):
    total_revenue = financials.get('Total Revenue')
    
    if total_revenue is not None:
        stress_scenarios = total_revenue * 0.9, total_revenue * 0.8
        return stress_scenarios
    return None

# Function to find operating leverage
def find_operating_leverage(financials):
    operating_expenses = financials.get('Operating Expenses')
    cost_of_revenue = financials.get('Cost of Revenue')
    
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

uploaded_share_prices = st.file_uploader("Upload Share Prices CSV", type="csv")
uploaded_statements_pdf = st.file_uploader("Upload Financial Statements PDF", type="pdf")

if uploaded_share_prices and uploaded_statements_pdf:
    share_prices = load_share_prices(uploaded_share_prices)
    pdf_text = extract_text_from_pdf(uploaded_statements_pdf)
    
    financial_keys = ['Net Income', 'Total Assets', 'Current Liabilities', 'Capital Expenditures', 'Total Revenue', 'Market Cap', 'Book Value', 'Shares Outstanding', 'Operating Expenses', 'Cost of Revenue']
    financials = get_financial_data_from_pdf(pdf_text, financial_keys)
    
    roic = calculate_moat_indicators(financials)
    investments_in_high, investments_in_low = analyze_investments(financials)
    stock_returns, industry_average = assess_returns(share_prices)
    cagr = assess_growth(financials)
    market_cap, intrinsic_value = define_valuation(financials)
    stress_scenarios = conduct_stress_test(financials)
    operating_leverage = find_operating_leverage(financials)
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
