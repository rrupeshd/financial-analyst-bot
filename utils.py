import streamlit as st
import yfinance as yf
from duckduckgo_search import DDGS
import google.generativeai as genai
import pandas as pd
from datetime import datetime, timedelta

# --- Configuration ---
# Configure the Gemini API key
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.warning("Gemini API key not found. Please add it to your Streamlit secrets.", icon="⚠️")

# --- Yahoo Finance Functions ---
@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_stock_data(symbol):
    """Fetches current stock data from Yahoo Finance."""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))
        if current_price:
            return {'current_price': current_price}
        else:
            # Fallback for symbols that might not have 'currentPrice'
            hist = stock.history(period="1d")
            if not hist.empty:
                return {'current_price': hist['Close'].iloc[-1]}
            return None
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

# --- News Fetching Functions ---
@st.cache_data(ttl=1800) # Cache for 30 minutes
def get_stock_news(symbol):
    """Fetches news for a given stock symbol using DuckDuckGo Search."""
    try:
        query = f"latest financial news for {symbol} stock"
        with DDGS() as ddgs:
            results = [r for r in ddgs.news(query, region='wt-wt', safesearch='off', timelimit='w', max_results=5)]
        
        # Simulate a more structured news API response
        formatted_results = []
        for res in results:
            formatted_results.append({
                'title': res.get('title'),
                'url': res.get('url'),
                'source': {'name': res.get('source')},
                'publishedAt': res.get('date') 
            })
        return formatted_results
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        return []

def get_all_news(symbols):
    """Fetches news for a list of stock symbols and compiles them."""
    news_list = []
    for symbol in symbols:
        news = get_stock_news(symbol)
        if news:
            news_list.append(f"\n--- News for {symbol} ---\n")
            for item in news:
                news_list.append(f"- {item['title']}")
    return "\n".join(news_list) if news_list else "No news found for the stocks in the portfolio."


# --- Gemini AI Functions ---
def get_gemini_response(prompt):
    """
    Gets a response from the Gemini model based on the provided prompt.
    """
    if not st.secrets.get("GEMINI_API_KEY"):
        return "Gemini API key is not configured. Please add it to your Streamlit secrets."
        
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        return f"An error occurred while generating the AI response: {e}"
