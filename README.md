# news_scraping_gui
Simple GUI to embed scraped news headlines and tweets.

GUI includes 4 tabs:

**1) Chart Portal**
- work in process
- goal: build dynamic, potentially real-time multifunctional stock chart

**2) Stock Portal**
- work in process
- goal: scrape in fundamental data from Yahoo Finance

**3) News Portal**
- scrapes in headlines from any news source provided as an object of Url type within news_urls.py
- sorted by timestamp
- each headline is a clickable link; links will turn grey after being clicked
- refreshable feed

**4) Tweet Portal**
- note: requires Twitter developer API keys; add keys to twitter_keys.conf
- scrapes tweets for any tickers provided as an object of Search_Term type within twitter_search.py
- search Twitter within tab for any keyword (e.g. $APPL, #fintech, etc.) and filter search by minimum likes and minimum followers; returns maximum number of tweets based on value provided in the count field
- refreshable feed (based on tickers provided within twitter_search.py)
