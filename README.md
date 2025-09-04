# **AI Financial Analyst & Portfolio Manager**

This is a Streamlit web application that acts as a personal AI-powered financial analyst. It allows users to upload their stock portfolio, view detailed analysis, get the latest news, and chat with an AI assistant powered by Google's Gemini model.

## **Features**

* **Portfolio Upload**: Easily upload your stock portfolio from an Excel file.  
* **Detailed Analysis**: Get a comprehensive overview of your portfolio, including current value, profit/loss, and allocation.  
* **Live Data**: Fetches real-time stock prices using the yfinance library.  
* **Latest News**: Aggregates the latest news for each stock in your portfolio.  
* **Interactive Visualizations**: Understand your portfolio with interactive charts and graphs powered by Plotly.  
* **AI Financial Analyst**: Chat with a Gemini-powered AI to get insights, analysis, and answers to your financial questions.

## **Setup and Installation**

### **1\. Clone the Repository**

git clone \<your-repo-url\>  
cd \<your-repo-name\>

### **2\. Create a Virtual Environment (Recommended)**

python \-m venv venv  
source venv/bin/activate  \# On Windows, use \`venv\\Scripts\\activate\`

### **3\. Install Dependencies**

Install all the required Python packages using the requirements.txt file.

pip install \-r requirements.txt

### **4\. Set Up API Keys (Streamlit Secrets)**

This application requires a Google Gemini API key. You need to store this key in Streamlit's secrets management.

1. **Get your Gemini API Key**: Visit the [Google AI Studio](https://aistudio.google.com/app/apikey) to get your API key.  
2. **Create a secrets file**: In your project directory, create a folder named .streamlit and inside it, a file named secrets.toml.  
3. **Add your API key**: Add the following line to your secrets.toml file:  
   GEMINI\_API\_KEY \= "YOUR\_API\_KEY\_HERE"

   Replace "YOUR\_API\_KEY\_HERE" with your actual Gemini API key.

## **How to Run the Application**

Once the setup is complete, you can run the Streamlit application with the following command:

streamlit run main\_app.py

The application will open in your web browser.

## **Portfolio Excel File Format**

For the application to correctly parse your portfolio, the uploaded Excel file (.xlsx) must contain the following columns:

* Stock Symbol: The official ticker symbol of the stock (e.g., RELIANCE.NS, TCS.NS).  
* Quantity: The number of shares you own.  
* Average Price: The average price at which you purchased the shares.

Here is an example of the expected format:

| Stock Symbol | Quantity | Average Price |
| :---- | :---- | :---- |
| RELIANCE.NS | 10 | 2500.50 |
| HDFCBANK.NS | 25 | 1500.75 |
| INFY.NS | 50 | 1450.00 |

## **Deployment**

You can easily deploy this application on [Streamlit Community Cloud](https://streamlit.io/cloud).

1. Push your project code to a GitHub repository.  
2. Sign up or log in to Streamlit Community Cloud.  
3. Click "New app" and connect your GitHub account.  
4. Select the repository and branch.  
5. **Important**: Before deploying, add your Gemini API key to the "Advanced settings" \> "Secrets" section on the deployment page.  
6. Click "Deploy\!".

Enjoy your AI Financial Analyst\!