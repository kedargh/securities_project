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

    output_dictionary = {f"{ticker} INFORMATION " : [actions , analyst_pricing , balance_sheet , capital_gains , cashflow , dividends , earnings , earnings_history , eps_revisions , eps_trend]}

    return output_dictionary



if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')