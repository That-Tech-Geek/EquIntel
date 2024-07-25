import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm

# Function to load uploaded financial data
def load_financials(file):
    return pd.read_csv(file, index_col=0)

# Function to load uploaded share price data
def load_share_prices(file):
    return pd.read_csv(file, index_col=0, parse_dates=True)

# Function to check and fetch required financial data
def get_financial_data(financials, key, uploaded_statements):
    if key in financials.index:
        return financials.loc[key]
    else:
        if uploaded_statements and key in uploaded_statements.columns:
            return uploaded_statements[key]
        else:
            st.error(f"{key} not found in the financials or uploaded statements.")
            return None

# Function to calculate moat indicators
def calculate_moat_indicators(financials, uploaded_statements):
    # Calculate key moat indicators such as ROIC, reinvestment rates, etc.
    net_income = get_financial_data(financials, 'Net Income', uploaded_statements)
    total_assets = get_financial_data(financials, 'Total Assets', uploaded_statements)
    current_liabilities = get_financial_data(financials, 'Current Liabilities', uploaded_statements)
    
    if net_income is not None and total_assets is not None and current_liabilities is not None:
        roic = net_income / (total_assets - current_liabilities)
        return roic.mean()
    return None

# Function to analyze investments in times of strength or distress
def analyze_investments(financials, uploaded_statements):
    net_income = get_financial_data(financials, 'Net Income', uploaded_statements)
    capital_expenditures = get_financial_data(financials, 'Capital Expenditures', uploaded_statements)
    
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
def assess_growth(financials, uploaded_statements):
    total_revenue = get_financial_data(financials, 'Total Revenue', uploaded_statements)
    
    if total_revenue is not None:
        cagr = (total_revenue.iloc[-1] / total_revenue.iloc[0])**(1/len(total_revenue)) - 1
        return cagr
    return None

# Function to define valuation
def define_valuation(financials, uploaded_statements):
    market_cap = get_financial_data(financials, 'Market Cap', uploaded_statements)
    book_value = get_financial_data(financials, 'Book Value', uploaded_statements)
    shares_outstanding = get_financial_data(financials, 'Shares Outstanding', uploaded_statements)
    
    if market_cap is not None and book_value is not None and shares_outstanding is not None:
        intrinsic_value = book_value * shares_outstanding
        return market_cap, intrinsic_value
    return None, None

# Function to conduct stress test
def conduct_stress_test(financials, uploaded_statements):
    total_revenue = get_financial_data(financials, 'Total Revenue', uploaded_statements)
    
    if total_revenue is not None:
        stress_scenarios = total_revenue * 0.9, total_revenue * 0.8
        return stress_scenarios
    return None

# Function to find operating leverage
def find_operating_leverage(financials, uploaded_statements):
    operating_expenses = get_financial_data(financials, 'Operating Expenses', uploaded_statements)
    cost_of_revenue = get_financial_data(financials, 'Cost of Revenue', uploaded_statements)
    
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
uploaded_statements = st.file_uploader("Upload Additional Financial Data CSV", type="csv")

if uploaded_financials and uploaded_share_prices:
    financials = load_financials(uploaded_financials)
    share_prices = load_share_prices(uploaded_share_prices)
    statements = load_financials(uploaded_statements) if uploaded_statements else None
    
    roic = calculate_moat_indicators(financials, statements)
    investments_in_high, investments_in_low = analyze_investments(financials, statements)
    stock_returns, industry_average = assess_returns(share_prices)
    cagr = assess_growth(financials, statements)
    market_cap, intrinsic_value = define_valuation(financials, statements)
    stress_scenarios = conduct_stress_test(financials, statements)
    operating_leverage = find_operating_leverage(financials, statements)
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
