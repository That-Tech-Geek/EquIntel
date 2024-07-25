import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm

# Function to fetch financial data
def fetch_data(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials
    return financials

# Function to calculate moat indicators
def calculate_moat_indicators(financials):
    # Calculate key moat indicators such as ROIC, reinvestment rates, etc.
    roic = financials.loc['Net Income'] / (financials.loc['Total Assets'] - financials.loc['Current Liabilities'])
    return roic.mean()

# Function to analyze investments in times of strength or distress
def analyze_investments(financials):
    # Identify periods of high and low performance
    performance = financials.loc['Net Income'].pct_change()
    high_performance = performance > performance.median()
    investments_in_high = financials.loc['Capital Expenditures'][high_performance].mean()
    investments_in_low = financials.loc['Capital Expenditures'][~high_performance].mean()
    return investments_in_high, investments_in_low

# Function to assess returns relative to industry standard
def assess_returns(ticker):
    # Compare company returns with industry average
    stock = yf.Ticker(ticker)
    stock_returns = stock.history(period="5y")['Close'].pct_change().mean()
    # Placeholder for industry average calculation
    industry_average = 0.05
    return stock_returns, industry_average

# Function to assess growth methodologies
def assess_growth(financials):
    # Calculate CAGR, revenue growth, etc.
    cagr = (financials.loc['Total Revenue'].iloc[-1] / financials.loc['Total Revenue'].iloc[0])**(1/len(financials.loc['Total Revenue'])) - 1
    return cagr

# Function to define valuation
def define_valuation(ticker):
    stock = yf.Ticker(ticker)
    market_cap = stock.info['marketCap']
    intrinsic_value = stock.info['bookValue'] * stock.info['sharesOutstanding']
    return market_cap, intrinsic_value

# Function to conduct stress test
def conduct_stress_test(financials):
    # Stress test scenarios (e.g., revenue drop, cost increase)
    stress_scenarios = financials.loc['Total Revenue'] * 0.9, financials.loc['Total Revenue'] * 0.8
    return stress_scenarios

# Function to find operating leverage
def find_operating_leverage(financials):
    fixed_costs = financials.loc['Operating Expenses'].mean()
    variable_costs = financials.loc['Cost of Revenue'].mean()
    operating_leverage = fixed_costs / (fixed_costs + variable_costs)
    return operating_leverage

# Function to pronounce a verdict
def pronounce_verdict(roic, stock_returns, industry_average, cagr, market_cap, intrinsic_value, operating_leverage):
    verdict = "Invest" if roic > 0.1 and stock_returns > industry_average and cagr > 0.05 and market_cap < intrinsic_value and operating_leverage > 0.5 else "Do Not Invest"
    return verdict

# Streamlit UI
st.title("Equity Analysis AI Model")
ticker = st.text_input("Enter the company ticker:", "AAPL")

if ticker:
    financials = fetch_data(ticker)
    roic = calculate_moat_indicators(financials)
    investments_in_high, investments_in_low = analyze_investments(financials)
    stock_returns, industry_average = assess_returns(ticker)
    cagr = assess_growth(financials)
    market_cap, intrinsic_value = define_valuation(ticker)
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
