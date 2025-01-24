from gnews import GNews
import csv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
import openai
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from news_fetcher import fetch_news_for_ticker


# def create_training_csv_file(headlines):
#     file_name = "training_dataset.csv"
#     with open(file_name, mode="w", newline="") as file:
#         writer = csv.writer(file)
#         writer.writerow(["sentences"])
#         for headline in headlines:
#             writer.writerow([headline])


async def headlines_fetcher(stock : str)->list:         #####TOOL 1####
    """Fetch the list of news for the given stock ticker"""
    google_news = GNews(
    language='en',
    country='US',
    period='1d',
    start_date=None,
    end_date=None,
    max_results=10,)
    ####GOOGLE NEWS OBJECT#####
    news = google_news.get_news(f"{stock}")
    headlines = []
    for single_news in news:
        headlines.append(single_news['title'])

    for headline in headlines:
        headline = headline.split('-')[0].strip()
    
    return(headlines)


async def sentiment_classifier(text: str) -> str:   #####TOOL 2#####
    """Derive sentiment for the given text."""
    model_path = "./finbert-finetuned"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.softmax(outputs.logits, dim=1)
        label_index = torch.argmax(predictions).item()

    labels = ["Neutral", "Negative", "Positive"]
    sentiment = labels[label_index]
    print(sentiment)
    return sentiment



model_client = OpenAIChatCompletionClient(
    model="gpt-4o-mini",
    api_key="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",
)

agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[headlines_fetcher , sentiment_classifier],
    system_message="You are a helpful assistant. Use tools when needed.",
)

async def run_agent():
    user_message = "Perform sentiment analysis for Infosys. The (headlines_fetcher) function returns the list of all the headlines of the company ticker (INFY). For each element of the list perform sentiment analysis using the (sentiment_classifier) function."
    response = await agent.on_messages(
        messages=[TextMessage(content=user_message, source="user")],
        cancellation_token=CancellationToken()
    )
    print(f"Assistant response: {response}")

import asyncio
asyncio.run(run_agent())  