import requests
import pandas as pd
import time
import numpy as np
from datetime import datetime
import yfinance as yf
from tabulate import tabulate

def calculate_rsi(data, window=14):
    """Calculate RSI for a given price series"""
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def get_nifty50_stocks():
    """Get list of Nifty 50 stocks"""
    # Using NSE India website data
    url = "https://www1.nseindia.com/content/indices/ind_nifty50list.csv"
    
    try:
        df = pd.read_csv(url)
        # Extract the symbol and company name
        symbols = df['Symbol'].tolist()
        return symbols
    except Exception as e:
        print(f"Error fetching Nifty 50 list: {e}")
        # Fallback list of Nifty 50 stocks
        return [
            "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "HINDUNILVR", 
            "INFY", "HDFC", "ITC", "KOTAKBANK", "LT", "AXISBANK", 
            "SBIN", "BAJFINANCE", "BHARTIARTL", "ASIANPAINT", "MARUTI", 
            "HCLTECH", "TITAN", "TATAMOTORS", "SUNPHARMA", "ULTRACEMCO", 
            "BAJAJFINSV", "WIPRO", "NESTLEIND", "NTPC", "POWERGRID", 
            "ONGC", "TECHM", "ADANIPORTS", "GRASIM", "JSWSTEEL", 
            "HINDALCO", "TATASTEEL", "M&M", "INDUSINDBK", "DRREDDY", 
            "BPCL", "CIPLA", "EICHERMOT", "COALINDIA", "BRITANNIA", 
            "ADANIENT", "HDFCLIFE", "SBILIFE", "UPL", "HEROMOTOCO", 
            "DIVISLAB", "APOLLOHOSP", "BAJAJ-AUTO", "TATACONSUM"
        ]

def get_stock_data(symbols):
    """Get stock data for given symbols with Yahoo Finance"""
    stock_data = []
    
    # Add .NS suffix for NSE stocks and fetch data
    for symbol in symbols:
        try:
            # Append .NS to get data from NSE
            ticker = yf.Ticker(f"{symbol}.NS")
            hist = ticker.history(period="1mo")
            
            if not hist.empty:
                # Calculate current market price (last closing price)
                cmp = hist['Close'].iloc[-1]
                
                # Calculate daily percentage change
                prev_close = hist['Close'].iloc[-2]
                daily_change = ((cmp - prev_close) / prev_close) * 100
                
                # Calculate RSI
                rsi = calculate_rsi(hist['Close']).iloc[-1]
                
                stock_data.append({
                    'Symbol': symbol,
                    'CMP': round(cmp, 2),
                    'Daily Change (%)': round(daily_change, 2),
                    'RSI': round(rsi, 2)
                })
                
            # Pause to avoid hitting rate limits
            time.sleep(0.2)
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    
    return stock_data

def main():
    print("Fetching Nifty 50 Stocks data...")
    
    # Get Nifty 50 stock symbols
    symbols = get_nifty50_stocks()
    
    if not symbols:
        print("Failed to fetch Nifty 50 stocks list.")
        return
    
    # Get stock data including CMP, daily change and RSI
    stocks_data = get_stock_data(symbols)
    
    # Convert to DataFrame and sort by RSI
    df = pd.DataFrame(stocks_data)
    
    if not df.empty:
        # Sort by RSI level (ascending)
        df_sorted_by_rsi = df.sort_values(by='RSI')
        
        # Print stocks data with tabulate for better formatting
        print("\nNifty 50 Stocks Data:")
        print(tabulate(df_sorted_by_rsi, headers='keys', tablefmt='pretty', showindex=False))
        
        # Highlight overbought (RSI > 70) and oversold (RSI < 30) stocks
        print("\nOverbought Stocks (RSI > 70):")
        overbought = df[df['RSI'] > 70]
        if not overbought.empty:
            print(tabulate(overbought, headers='keys', tablefmt='pretty', showindex=False))
        else:
            print("No stocks are currently overbought.")
            
        print("\nOversold Stocks (RSI < 30):")
        oversold = df[df['RSI'] < 30]
        if not oversold.empty:
            print(tabulate(oversold, headers='keys', tablefmt='pretty', showindex=False))
        else:
            print("No stocks are currently oversold.")
    else:
        print("Failed to fetch stock data.")

if __name__ == "__main__":
    main()
