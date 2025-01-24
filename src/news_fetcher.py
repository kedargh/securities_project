from gnews import GNews 

google_news = GNews()

def fetch_news_for_ticker(stock):
    news = google_news.get_news(f"{stock}")
    headlines = []
    for single_news in news:
        headlines.append(single_news['title'])

    for headline in headlines:
        headline = headline.split('-')[0].strip()
    
    print(headlines)

if __name__ == "__main__":
    fetch_news_for_ticker("INFY")
