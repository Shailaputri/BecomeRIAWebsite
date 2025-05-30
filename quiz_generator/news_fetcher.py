import feedparser

def fetch_latest_sebi_news(max_articles=5):
    url = "https://news.google.com/rss/search?q=SEBI+investment+India&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    
    articles = []
    for entry in feed.entries[:max_articles]:
        title = entry.title
        summary = entry.get("summary", "")
        articles.append(f"- {title}\n  {summary}")
    
    return "\n\n".join(articles)