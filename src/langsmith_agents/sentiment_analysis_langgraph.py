from typing import Annotated
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
import yfinance as yf
from gnews import GNews
class StockState(TypedDict): ######Pydantic Equivalent of StockInfo pydantic
    stock: str 
    attributes: dict


class NewsState(TypedDict):
    stock: str
    number_of_news: int
    headlines: list[str]

graph_builder = StateGraph(StockState)


def fetch_company_details(stockstate_obj : StockState)-> StockState:
    stock_name = stockstate_obj.stock
    data = yf.Ticker(stock_name)
    dict_for_analyst_price_targets = data.analyst_price_targets or {}
    dict_for_ticker_info = data.info or {}
    stock_details = {**dict_for_analyst_price_targets, **dict_for_ticker_info}

    return StockState(stock=stock_name,attributes=stock_details)


def headlines_fetcher(newsstate_obj : NewsState)->NewsState:         #####TOOL 1####
    """Fetch the list of news for the given stock ticker"""
   
    stock = newsstate_obj["stock"] 
    number_of_news = newsstate_obj["number_of_news"]

    google_news = GNews(
    language='en',
    country='US',
    period='1d',
    start_date=None,
    end_date=None,
    max_results=number_of_news,)
    ####GOOGLE NEWS OBJECT#####
    stock = newsstate_obj.stock
    news = google_news.get_news(f"{stock}")
    headlines = []
    for single_news in news:
        headlines.append(single_news['title'])

    for headline in headlines:
        headline = headline.split('-')[0].strip()
    
    #return headlines
    return NewsState(stock=stock, headlines=headlines)



if __name__ == "__main__":

    graph_builder.add_node("company_details" , fetch_company_details)
    graph_builder.add_node("stock_news" , headlines_fetcher)
    graph_builder.set_entry_point("stock_news")
    graph_builder.set_finish_point("stock_news")
    graph = graph_builder.compile()

    input_state = {"stock":"INFY" , "number_of_news":6 ,  "headlines":[]}
    print("INPUT STATE ADDED")
    output_state = graph.invoke(input_state)

    print("Stock Details : " , output_state)
