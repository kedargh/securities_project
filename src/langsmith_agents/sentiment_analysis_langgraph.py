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

###############################################################
def take_input(initial_state):
    print("Called start node")
    prompt = str(input("Enter the operation you want to perform : "))
    initial_state["prompt"] = prompt


    if "market research" in initial_state["prompt"].lower() or "market study" in initial_state["prompt"].lower():
        tokens = prompt.split()
        try:
            index = tokens.index("for")
            if index + 1 < len(tokens):
                initial_state["ticker"]=tokens[index+1]
        except ValueError:
            pass

    elif "sentiment analysis" in initial_state["prompt"].lower() or "sentiment" in initial_state["prompt"].lower():
        tokens = prompt.split()
        try:
            index = tokens.index("for")
            if index + 1 < len(tokens):
                initial_state["stock"]=tokens[index+1]
        except ValueError:
            pass
    print(initial_state)
    return initial_state


    

def news_fetcher(inital_state):
    if initial_state["stock"] is None:
        return initial_state
    else:
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
        print(inital_state)
        return inital_state



def sentiment_classifier(initial_state):
    if initial_state["stock"] is None:
        return initial_state
    else:
        headlines = initial_state["headlines"]
        classified_sentiment_output = []
        for headline in headlines:
            classified_sentiment_output.append(sentiment_classifier_single_news(headlines))

        initial_state["sentiments"] = classified_sentiment_output
        print(initial_state)
        return initial_state

def yf_market_research(initial_state):
    if initial_state["ticker"] is None:
        return initial_state
    else:
        stock_name = initial_state["ticker"]
        data = yf.Ticker(stock_name)
        dict_for_analyst_price_targets = data.analyst_price_targets
        dict_for_ticker_info = data.info
        dict_for_analyst_price_targets.update(dict_for_ticker_info)
        initial_state["company_data"] = dict_for_analyst_price_targets
        print(initial_state)
        return initial_state 


def end_node(initial_state):
    print(f"Your processed input is: {initial_state}")
    return initial_state

workflow = Graph()

workflow.add_node("start" , take_input)
workflow.add_node("news_fetcher",news_fetcher)
workflow.add_node("sentiment_classifier", sentiment_classifier)
workflow.add_node("market_research" , yf_market_research)
workflow.add_node("end" , end_node)


workflow.add_edge("start","news_fetcher")
workflow.add_edge("news_fetcher" , "sentiment_classifier")
workflow.add_edge("sentiment_classifier" , "market_research")
workflow.add_edge("market_research" , "end")

workflow.set_entry_point("start")
compiled_workflow = workflow.compile()
final_state = compiled_workflow.invoke(initial_state)

print("Final State:", final_state)
