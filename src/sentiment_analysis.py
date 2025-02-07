from gnews import GNews
import csv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.agents import UserProxyAgent
from pydantic import BaseModel
from typing import List, Dict
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
import openai
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from news_fetcher import fetch_news_for_ticker
import asyncio
from rich.console import Console
#################MESSAGE FORMATS FOR AGENTS#############################################
class NewsResponse(BaseModel):
    stock: str
    headlines: List[str]

class SentimentResponse(BaseModel):
    stock: str
    results: List[Dict[str, str]]

############################################################################################################################
model_client = OpenAIChatCompletionClient(
    model="gpt-4o-mini",
    api_key="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",
)
################################################################################################################################
async def headlines_fetcher(stock : str , number_of_news: int)->NewsResponse:         #####TOOL 1####
    """Fetch the list of news for the given stock ticker"""
    google_news = GNews(
    language='en',
    country='US',
    period='1d',
    start_date=None,
    end_date=None,
    max_results=number_of_news,)
    ####GOOGLE NEWS OBJECT#####
    news = google_news.get_news(f"{stock}")
    headlines = []
    for single_news in news:
        headlines.append(single_news['title'])

    for headline in headlines:
        headline = headline.split('-')[0].strip()
    
    #return headlines
    return NewsResponse(stock=stock, headlines=headlines)


model_path = "yiyanghkust/finbert-tone"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()


async def sentiment_classifier_loop(news_response_object : NewsResponse) -> SentimentResponse:
    """Classify sentiment for multiple news articles asynchronously and return structured response."""
    if isinstance(news_response_object, dict):
        news_response_object = NewsResponse(**news_response_object)

    headlines = news_response_object.headlines

    async def sentiment_classifier(news: str) -> Dict[str,str]:
        """Single news classification"""
        inputs = tokenizer([news], return_tensors="pt", truncation=True, padding=True)

        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.softmax(outputs.logits, dim=1)
            label_index = torch.argmax(predictions).item()
        labels = ["Neutral", "Positive", "Negative"]
        return {news: labels[label_index]}

    tasks = [sentiment_classifier(news) for news in headlines]
    results = await asyncio.gather(*tasks)

    return SentimentResponse(stock=news_response_object.stock , results=results)


async def async_input_func(prompt: str, cancel_token=None) -> str:
    return await asyncio.to_thread(input("Enter your question = "), prompt)
#####################AGENTS###################################################################
news_agent = AssistantAgent(
    name="NewsFetcherAgent",
    description="Fetches financial news for a given stock ticker.",
    model_client=model_client,
    tools=[headlines_fetcher],
    system_message="You are a helpful assistant. Use tools when needed.",

)
sentiment_classifier_agent = AssistantAgent(
    name="SentimentClassifierAgent",
    description="Classifies sentiment for a list of news articles.",
    model_client=model_client,
    tools=[sentiment_classifier_loop], #headlines_fetcher , , sentiment_classifier_loop
    system_message="You are a helpful assistant. Use tools when needed.",
)

user_agent = UserProxyAgent(
    name="AskerAgent",
    description="A human user",
    input_func=async_input_func,
    )
################################################################################################################
# async def main():

team = RoundRobinGroupChat([news_agent , sentiment_classifier_agent , user_agent], max_turns=3) #, termination_condition="DONE")
async def run_chat():
    stream = team.run_stream(task="""Perform sentiment analysis using the "news_agent" agent and the "sentiment_classifier_agent" agent for the first 10 market news for Divi's Laboratories. Once done reply with "DONE" .""")

    console = Console()
    async for result in stream:
        console.print(result)

asyncio.run(run_chat())
