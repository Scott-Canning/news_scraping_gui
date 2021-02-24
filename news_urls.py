class Url:
    def __init__(self, url, domain):
        self.url = url
        self.domain = domain

# list of URL objects
url_list = []

'''
url objects
'''
# News Wires
gnw_ma = Url("https://www.globenewswire.com/RssFeed/subjectcode/27-Mergers%20And%20Acquisitions/feedTitle/GlobeNewswire%20-%20Mergers%20And%20Acquisitions", "News Wire - M&A")
gnw_earnings = Url("https://www.globenewswire.com/RssFeed/subjectcode/13-Earnings%20Releases%20And%20Operating%20Results/feedTitle/GlobeNewswire%20-%20Earnings%20Releases%20And%20Operating%20Results", "News Wire - Earnings")

# Tech
ycombinator = Url("https://news.ycombinator.com/rss", "ycombinator")
tech_crunch = Url("http://feeds.feedburner.com/TechCrunch/", "Tech Crunch")
arstechnica = Url("http://feeds.arstechnica.com/arstechnica/index","Ars Technica")
wsj_tech = Url("https://feeds.a.dj.com/rss/RSSWSJD.xml", "WSJ Tech News")
nyt_tech = Url("https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "NYT Tech News")
gnw_tech = Url("https://www.globenewswire.com/RssFeed/industry/9000-Technology/feedTitle/GlobeNewswire%20-%20Industry%20News%20on%20Technology", "News Wire - Tech")


# Markets & business
cnbc = Url("https://www.cnbc.com/id/100003114/device/rss/rss.html", "CNBC")
wsj_us_business = Url("https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml", "WSJ US Business News")
wsj_markets = Url("https://feeds.a.dj.com/rss/RSSMarketsMain.xml","WSJ Market News")
nyt_business = Url("https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "NYT Business")

# World news
wsj_world = Url("https://feeds.a.dj.com/rss/RSSWorldNews.xml","WSJ World News")
nyt_world = Url("https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "NYT World News")

# append Url objects to url_list
url_list.append(ycombinator)
url_list.append(arstechnica)
url_list.append(cnbc)
url_list.append(tech_crunch)
url_list.append(wsj_world)
url_list.append(wsj_tech)
url_list.append(wsj_us_business)
url_list.append(wsj_markets)
url_list.append(nyt_tech)
url_list.append(nyt_business)
url_list.append(nyt_world)
url_list.append(gnw_ma)
url_list.append(gnw_earnings)
url_list.append(gnw_tech)