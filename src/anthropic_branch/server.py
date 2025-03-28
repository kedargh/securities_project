from transformers import AutoModelForSequenceClassification, AutoTokenizer
from rich.console import Console
from pydantic import BaseModel
from typing import List, Dict
from gnews import GNews
import yfinance as yf
import torch
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP


model_path = "yiyanghkust/finbert-tone"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()


mcp = FastMCP("competitive_analysis")


class news_object_class(BaseModel):
    stock: str = None
    news: List = []
    classification: List = []

class time_series_class(BaseModel):
    stock: str = None
    opening_price_list: List
    daily_high_list: List
    daily_low_list: List
    stock_price_time_series_list: List
    daily_volume_list: List
    daily_dividends_list: List
    daily_stock_splits: List


class stock_information(BaseModel):
    stock: str
    company_information: Dict


def sentiment_classifier_single_news(news: str) -> str:
    """Single news classification"""
    if not news:
        return "Neutral"
    inputs = tokenizer(news, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        num_classes = logits.shape[1]
        if num_classes > 3:
            print("Warning: Model outputs more than 3 classes. Truncating logits.")
            logits = logits[:, :3]  

        predictions = torch.softmax(logits, dim=1)
        label_index = torch.argmax(predictions).item()
    labels = ["Neutral", "Positive", "Negative"]
    if label_index < 0 or label_index >= len(labels):
        print(f"Warning: Invalid label index {label_index}. Defaulting to 'Neutral'.")
        return "Neutral"

    return labels[label_index]

@mcp.tool()
async def news_fetcher(stock_name:str):
    """Only for fetching news for a stock_name"""
    google_news = GNews(
    language='en',
    country='US',
    period='1d',
    start_date=None,
    end_date=None,
    max_results=50,)
    ####GOOGLE NEWS OBJECT#####
    news = google_news.get_news(f"{stock_name}")
    headlines = []
    for single_news in news:
        headlines.append(single_news['title'])

    for headline in headlines:
        headline = headline.split('-')[0].strip()

    return headlines

@mcp.tool()
async def news_classification_procedure(stock:str):
    """Main function tool for news classification"""
    news_object = news_object_class()
    print("Created News Object")
    news_object.stock = stock
    news_object.news = news_fetcher(stock)
    
    classification_results = []
    for news in news_object.news:
        classification_results.append(sentiment_classifier_single_news(news))

    print("Classification results populated !!!!")
    news_object.classification = classification_results

    print("Sentiment classification performed here are the results - ")
    return news_object




@mcp.tool()
async def yfinance_financial_data_tool(ticker:str):
    """
    Fetches comprehensive financial market data for a given stock ticker.

    This asynchronous function retrieves an extensive range of financial indicators 
    and market data for the specified stock ticker using the Yahoo Finance API (`yfinance` library). 
    The data includes fundamental analysis metrics, earnings reports, balance sheets, 
    insider transactions, price targets, and more.

    Args:
        ticker (str): The stock ticker symbol (without the ".NS" extension).

    Returns:
        dict: A dictionary containing various financial indicators and market data.

    The returned dictionary contains the following key financial attributes:
        - actions: Corporate actions such as stock splits and dividends.
        - analyst_price_targets: Analyst price target predictions.
        - balance_sheet: Company balance sheet data.
        - capital_gains: Capital gains information.
        - cashflow: Cash flow statement data.
        - dividends: Dividend payment history.
        - earnings: Earnings reports and financial performance.
        - earnings_history: Historical earnings data.
        - eps_revisions: Earnings per share (EPS) revision history.
        - eps_trend: Trends in earnings per share (EPS).
        - fast_info: Quick financial summary, including price and volume data.
        - financials: Company financial statements.
        - funds_data: Mutual funds and institutional holdings data.
        - growth_estimates: Projected growth estimates for the company.
        - history_metadata: Metadata related to historical stock price data.
        - income_stmt: Income statement data.
        - insider_purchases: Insider purchase transactions.
        - insider_roster_holders: Insider holders and executives.
        - insider_transactions: Insider buying/selling transactions.
        - institutional_holders: Institutional investors holding company shares.
        - isin: International Securities Identification Number.
        - major_holders: Summary of major shareholders.
        - mutualfund_holders: Mutual fund holdings of the stock.
        - news: Latest news articles related to the company.
        - options: Available options contracts for the stock.
        - quarterly_balance_sheet: Quarterly balance sheet data.
        - quarterly_cash_flow: Quarterly cash flow statement.
        - quarterly_earnings: Quarterly earnings reports.
        - quarterly_financials: Quarterly financial statement data.
        - quarterly_income_stmt: Quarterly income statement.
        - recommendations: Analyst recommendations for the stock.
        - recommendations_summary: Summary of analyst recommendations.
        - revenue_estimate: Revenue estimates for future periods.
        - sec_filings: SEC filings and regulatory reports.
        - shares: Shareholding structure and float data.
        - splits: Stock split history.
        - sustainability: ESG (Environmental, Social, Governance) data.
        - ttm_cash_flow: Trailing twelve-month cash flow statement.
        - ttm_financials: Trailing twelve-month financial statements.
        - ttm_income_stmt: Trailing twelve-month income statement.
        - upgrades_downgrades: Analyst rating upgrades and downgrades.

    Example:
        >>> import asyncio
        >>> result = asyncio.run(yfinance_market_data_tool("INFY"))
        >>> print(result["INFY.NS INFORMATION"]["financials"])

    Note:
        - The function automatically appends ".NS" to the given stock ticker, assuming it belongs to NSE.
        - Ensure a stable internet connection for fetching live data.
        - This function is asynchronous and should be used with `asyncio.run()` or within an async environment.
    """
    ticker=str(ticker)+".NS"
    data = yf.Ticker(ticker)
    actions = {"actions":data.actions}
    analyst_pricing = {"analyst_price_targets":data.analyst_price_targets}
    balance_sheet = {"balance_sheet":data.balancesheet}
    capital_gains = {"capital_gains":data.capital_gains}
    cashflow={"cashflow":data.cashflow}
    dividends={"dividends":data.dividends}
    earnings={"earnings":data.earnings}
    earnings_history={"earnings_history":data.earnings_history}
    eps_revisions={"eps_revisions":data.eps_revisions}
    eps_trend={"eps_trends":data.eps_trend}

    fast_info = {"fast_info": data.fast_info}
    financials = {"financials": data.financials}
    funds_data = {"funds_data": data.funds_data}
    growth_estimates = {"growth_estimates": data.growth_estimates}
    history_metadata = {"history_metadata": data.history_metadata}
    income_stmt = {"income_stmt": data.income_stmt}
    incomestmt = {"incomestmt": data.incomestmt}
    info = {"info": data.info}
    insider_purchases = {"insider_purchases": data.insider_purchases}
    insider_roster_holders = {"insider_roster_holders": data.insider_roster_holders}
    insider_transactions = {"insider_transactions": data.insider_transactions}
    institutional_holders = {"institutional_holders": data.institutional_holders}
    isin = {"isin": data.isin}
    major_holders = {"major_holders": data.major_holders}
    mutualfund_holders = {"mutualfund_holders": data.mutualfund_holders}
    news = {"news": data.news}
    options = {"options": data.options}
    quarterly_balance_sheet = {"quarterly_balance_sheet": data.quarterly_balancesheet}
    quarterly_cash_flow = {"quarterly_cash_flow": data.quarterly_cashflow}
    quarterly_earnings = {"quarterly_earnings": data.quarterly_earnings}
    quarterly_financials = {"quarterly_financials": data.quarterly_financials}
    quarterly_income_stmt = {"quarterly_income_stmt": data.quarterly_incomestmt}
    recommendations = {"recommendations": data.recommendations}
    recommendations_summary = {"recommendations_summary": data.recommendations_summary}
    revenue_estimate = {"revenue_estimate": data.revenue_estimate}
    sec_filings = {"sec_filings": data.sec_filings}
    shares = {"shares": data.shares}
    splits = {"splits": data.splits}
    sustainability = {"sustainability": data.sustainability}
    ttm_cash_flow = {"ttm_cash_flow": data.ttm_cashflow}
    ttm_financials = {"ttm_financials": data.ttm_financials}
    ttm_income_stmt = {"ttm_income_stmt": data.ttm_incomestmt}
    upgrades_downgrades = {"upgrades_downgrades": data.upgrades_downgrades}

    
    output_dictionary = {
    f"{ticker} INFORMATION": [
        actions, analyst_pricing, balance_sheet, capital_gains, cashflow, dividends, earnings,
        earnings_history, eps_revisions, eps_trend, fast_info, financials, funds_data,
        growth_estimates, history_metadata, income_stmt, incomestmt, info, insider_purchases,
        insider_roster_holders, insider_transactions, institutional_holders, isin, major_holders,
        mutualfund_holders, news, options, quarterly_balance_sheet, quarterly_cash_flow,
        quarterly_earnings, quarterly_financials, quarterly_income_stmt, recommendations,
        recommendations_summary, revenue_estimate, sec_filings, shares, splits, sustainability,
        ttm_cash_flow, ttm_financials, ttm_income_stmt, upgrades_downgrades
    ]
}
    return output_dictionary



@mcp.tool()
def stock_info_tool(stock_ticker: str):
    """
    Fetches detailed stock information for a given ticker symbol.

    This tool retrieves real-time and historical stock data from Yahoo Finance 
    using the yfinance library. It provides key company details, including 
    financial metrics, market performance, executive information, dividend 
    history, and valuation ratios.

    Args:
        stock_ticker (str): The stock ticker symbol (without the exchange suffix).

    Returns:
        dict: A dictionary containing stock details such as company overview, 
              financials, market data, executive team, and valuation metrics.

    Example:
        >>> stock_info_tool("AAPL")
        {'address1': 'One Apple Park Way', 'city': 'Cupertino', ..., 'symbol': 'AAPL'}
    """
    stock_ticker=str(stock_ticker)+".NS"
    data=yf.Ticker(stock_ticker)
    stock_information_object=stock_information()
    stock_information_object.stock=stock_ticker
    stock_information_object.company_information=data


    return stock_information_object




@mcp.tool()
def time_series_indicators(stock_ticker: str):
    """
    Fetches historical stock data for a given stock ticker and stores it in a time series object.

    This function retrieves the historical stock data (Open, High, Low, Close, Volume, Dividends, 
    and Stock Splits) for the specified stock ticker using the Yahoo Finance API (`yfinance` library). 
    The data is then stored in a `time_series_class` object for further analysis.

    Args:
        stock_ticker (str): The stock ticker symbol (without the ".NS" extension).

    Returns:
        time_series_class: An object containing the stock's historical time series data.

    Attributes of the returned object:
        - stock (str): The full stock ticker (appended with ".NS").
        - opening_price_list (list): List of daily opening prices.
        - daily_high_list (list): List of daily highest prices.
        - daily_low_list (list): List of daily lowest prices.
        - stock_price_time_series_list (list): List of daily closing prices.
        - daily_volume_list (list): List of daily trading volumes.
        - daily_dividends_list (list): List of daily dividend payouts.
        - daily_stock_splits (list): List of stock split events.

    Example:
        >>> obj = time_series_indicators("INFY")
        >>> print(obj.stock)  # Output: INFY.NS
        >>> print(obj.stock_price_time_series_list[:5])  # First 5 closing prices

    Note:
        - This function assumes that the stock ticker belongs to the National Stock Exchange (NSE) 
          and automatically appends ".NS" to the given ticker.
        - Ensure that the `time_series_class` is properly defined before calling this function.
    """
    
    stock_ticker = str(stock_ticker) + ".NS"
    data = yf.Ticker(stock_ticker)
    historical_data = data.history(period="max").reset_index()

    open_list = historical_data["Open"].tolist()
    high_list = historical_data["High"].tolist()
    low_list = historical_data["Low"].tolist()
    close_list = historical_data["Close"].tolist()
    volume_list = historical_data["Volume"].tolist()
    dividends_list = historical_data["Dividends"].tolist()
    splits_list = historical_data["Stock Splits"].tolist()

    time_series_indicators_object = time_series_class()
    time_series_indicators_object.stock = stock_ticker
    time_series_indicators_object.opening_price_list = open_list
    time_series_indicators_object.daily_high_list = high_list
    time_series_indicators_object.daily_low_list = low_list
    time_series_indicators_object.stock_price_time_series_list = close_list
    time_series_indicators_object.daily_volume_list = volume_list
    time_series_indicators_object.daily_dividends_list = dividends_list
    time_series_indicators_object.daily_stock_splits = splits_list

    return time_series_indicators_object

    


if __name__ == "__main__":
    # Initialize and run the server
    print("SERVER STARTED")
    mcp.run(transport='stdio')
    
