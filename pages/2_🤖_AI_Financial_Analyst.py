import streamlit as st
from utils import get_gemini_response, get_all_news
import pandas as pd

st.set_page_config(page_title="AI Financial Analyst", page_icon="🤖", layout="wide")

st.title("🤖 AI Financial Analyst")
st.markdown("Ask me anything about your portfolio!")

# Check for portfolio and analysis data
if 'portfolio_df' not in st.session_state or 'analysis_df' not in st.session_state:
    st.warning("Please upload and analyze your portfolio on the main and analysis pages first.")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What would you like to know about your portfolio?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("The AI analyst is thinking..."):
        try:
            portfolio_df = st.session_state['portfolio_df']
            analysis_df = st.session_state['analysis_df']
            
            # Fetch latest news for all stocks in the portfolio
            stock_symbols = portfolio_df['stock_symbol'].tolist()
            news_context = get_all_news(stock_symbols)
            
            # Convert dataframes to string/markdown for the prompt
            portfolio_summary = analysis_df.to_markdown()

            # Construct a detailed prompt for the Gemini model
            full_prompt = f"""
            As an expert financial analyst for the Indian stock market, your task is to provide an insightful and data-driven response to the user's query based on their portfolio and the latest financial news.

            **User's Portfolio Summary:**
            {portfolio_summary}

            **Latest News Headlines for the stocks in the portfolio:**
            {news_context}

            **User's Question:**
            {prompt}

            **Instructions:**
            1.  Analyze the user's query in the context of their provided portfolio and the latest news.
            2.  Provide a clear, concise, and professional answer.
            3.  If the query is about a specific stock, focus your analysis on that stock's data and news.
            4.  If the query is general, provide a holistic view of the portfolio.
            5.  Use the provided data to support your claims (e.g., mention P/L, current values, etc.).
            6.  Do not give direct financial advice to buy or sell. Instead, provide analysis and insights.
            7.  Format your response in well-structured markdown for readability.
            """

            response = get_gemini_response(full_prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"An error occurred while communicating with the AI: {e}")
