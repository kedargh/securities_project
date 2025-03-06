from transformers import AutoModelForSequenceClassification, AutoTokenizer
from langgraph.graph import Graph
from rich.console import Console
from pydantic import BaseModel
from typing import List, Dict
from gnews import GNews
import yfinance as yf
import torch

initial_state = {"prompt":None ,"stock": None, "ticker": None , "number_of_news":None,"headlines": None , "sentiments": None , "company_data":None}


##############NOTB A NODE###########################

model_path = "yiyanghkust/finbert-tone"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()
def sentiment_classifier_single_news(news: str) -> str:
        """Single news classification"""
        inputs = tokenizer([news], return_tensors="pt", truncation=True, padding=True)

        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.softmax(outputs.logits, dim=1)
            label_index = torch.argmax(predictions).item()
        labels = ["Neutral", "Positive", "Negative"]
        return labels[label_index]



###############################################################
def take_input(initial_state):
    prompt = str(input("Enter the operation you want to perform : "))
    initial_state["prompt"] = prompt
    return initial_state

def input_prompt_output(initial_state):
    if "market research" in initial_state["prompt"].lower() or "market study" in initial_state["prompt"].lower():
        return "market_research"
    elif "sentiment analysis" in initial_state["prompt"].lower() or "sentiment" in initial_state["prompt"].lower():
        return "sentiment_classifier"
    

def market_research(inital_state):
    google_news = GNews(
    language='en',
    country='US',
    period='1d',
    start_date=None,
    end_date=None,
    max_results=50,)
    ####GOOGLE NEWS OBJECT#####
    stock=initial_state["stock"]
    news = google_news.get_news(f"{stock}")
    headlines = []
    for single_news in news:
        headlines.append(single_news['title'])

    for headline in headlines:
        headline = headline.split('-')[0].strip()

    inital_state["headlines"] = headlines
    return inital_state



def sentiment_classifier(initial_state):
    headlines = initial_state["headlines"]
    classified_sentiment_output = []
    for headline in headlines:
        classified_sentiment_output.append(sentiment_classifier_single_news(headlines))

    initial_state["sentiments"] = classified_sentiment_output
    return initial_state



def end_node(initial_state):
    print(f"Your processed input is: {initial_state}")
    return initial_state

workflow = Graph()

workflow.add_node("start" , take_input)
workflow.add_node("conditional_node", input_prompt_output)
workflow.add_node("market_research", market_research)
workflow.add_node("sentiment_classifier", sentiment_classifier)
workflow.add_node("end" , end_node)

workflow.add_conditional_edges(
    "start", input_prompt_output,
    {"market_research":"market_research" , "sentiment_classifier":"sentiment_classifier"}
)   
workflow.set_entry_point("start")
compiled_workflow = workflow.compile()
final_state = compiled_workflow.invoke(initial_state)

print("Final State:", final_state)
