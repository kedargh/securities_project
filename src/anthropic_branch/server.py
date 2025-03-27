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
async def yfinance_market_data_tool(ticker:str):
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



if __name__ == "__main__":
    # Initialize and run the server
    print("SERVER STARTED")
    mcp.run(transport='stdio')
    
