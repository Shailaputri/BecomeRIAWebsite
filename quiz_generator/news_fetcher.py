import feedparser
import random
import os
import json
from datetime import datetime

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=SEBI+investment+India&hl=en-IN&gl=IN&ceid=IN:en",
    "https://www.moneycontrol.com/rss/MCtopnews.xml",
    "https://economictimes.indiatimes.com/rss/wealth/rssfeedstopstories.cms",
]

SEEN_TITLES_PATH = "quiz_generator/news_cache/seen_titles.json"

def load_seen_titles():
    if os.path.exists(SEEN_TITLES_PATH):
        with open(SEEN_TITLES_PATH, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_titles(titles):
    os.makedirs(os.path.dirname(SEEN_TITLES_PATH), exist_ok=True)
    with open(SEEN_TITLES_PATH, "w") as f:
        json.dump(list(titles), f, indent=2)

def fetch_latest_sebi_news(max_articles=5):
    all_articles = []
    seen_titles = load_seen_titles()
    new_titles = set()

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title.strip()
            if title.lower().startswith("sponsored") or title in seen_titles:
                continue

            summary = entry.get("summary", "").strip()
            published = entry.get("published", "")
            article_text = f"- {title}\n  {summary}\n  {published}\n"
            all_articles.append(article_text)
            new_titles.add(title)

    random.shuffle(all_articles)
    selected_articles = all_articles[:max_articles]

    # Update seen titles
    seen_titles.update(new_titles)
    save_seen_titles(seen_titles)

    return "\n\n".join(selected_articles)
