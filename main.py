#!/usr/bin/python
#!/usr/bin/env python

import os
import operator
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import webbrowser
from datetime import datetime, timedelta, date
from time import strftime
from pytz import timezone
from news_urls import url_list # import news urls from file
from twitter_search import search_list # import search terms from file
import tweepy as tw
import configparser
from pandas import DataFrame
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np
import yfinance as yf

KEYS_LOCATION = 'twitter_keys.conf'
COLOR_BLACK = '#24272D'
COLOR_GREEN = '#85BDAE'
EST = timezone('US/Eastern')
GMT = timezone('GMT')


'''
Helper functions
'''

# configure parser
def read_conf(settings_location):
    """Read the given setting file
    and return the configparser
    """
    settings = configparser.ConfigParser()
    settings.optionxform = str
    settings.read(settings_location)
    return settings

# convert timezone to EST
def convert_tz_EST(date_input):
    date_output = GMT.localize(date_input)
    date_output = date_output.astimezone(EST)
    return date_output


'''
News integration
'''

# default article_list
article_list = []
def news(site):
    news_url = site.url
    parse_xml_url = urlopen(news_url)
    xml_page = parse_xml_url.read()
    parse_xml_url.close()

    soup_page = BeautifulSoup(xml_page, "xml")
    news_list = soup_page.findAll("item")

    for getfeed in news_list:
        article_date = str(getfeed.pubDate.text)[0:22] #strip first 22 chars
        article_date = datetime.strptime(article_date, '%a, %d %b %Y %H:%M')

        # convert time from GMT to EST
        article_date = GMT.localize(article_date)
        article_date = article_date.astimezone(EST)

        # only show articles with publish dates of today
        if (article_date.day == datetime.today().day):
            # isolate hour and minute for sorting list
            article_hour = str(article_date.hour)
            article_minute = str(article_date.minute)
            # append article details to list, show only time
            article_list.append([getfeed.title.text, getfeed.link.text,
                                str(article_date.strftime("%I:%M %p")),
                                int(article_hour), int(article_minute),
                                site.domain, False])

# build article_list (url_list comes from news_urls.py)
for site in url_list:
    news(site)

'''
GUI
'''

class AppGUI():
    def __init__(self, master):
        self.master = master
        # create header
        headline_var = StringVar()
        self.label = Label(master, textvariable=headline_var,
                            highlightbackground='grey', highlightthickness=1,
                            width=1000, bg=COLOR_GREEN, fg=COLOR_BLACK)
        time_format = "%A, %b %d %-I:%M %p"
        now_time = datetime.now(EST)
        headline_var.set(now_time.strftime(time_format))
        self.label.pack()

        # style overlay for tabs
        style = ttk.Style(master)
        style.theme_create('dark_mode', settings={
            ".": {
                "configure": {
                    "background": COLOR_GREEN, # All except tabs
                    "font":COLOR_BLACK,
                    "tabposition": 'nw'
                }
            },
            "TNotebook": {
                "configure": {
                    "background":COLOR_BLACK, # margin color
                    "tabmargins": [2, 5, 0, 0] # margins: left, top, right, separator
                }
            },
            "TButton": {
                "configure": {
                    "background": COLOR_GREEN, # Your margin color
                    "padding": 0,
                    "borderwidth": 0
                }
            },
            "TNotebook.Tab": {
                "configure": {
                    "background": COLOR_GREEN, # tab color when not selected
                    "padding": [10, 2], # [space between text and horizontal tab-button border, space between text and vertical tab_button border]
                    "font":COLOR_BLACK
                },
                "map": {
                    "background": [("selected", COLOR_GREEN)], # Tab color when selected
                    "expand": [("selected", [1, 1, 1, 0])] # text margins
                }
            }
        })
        style.theme_use('dark_mode')

        # tab master
        tab_control_master = ttk.Notebook(master)
        tab_control_master.pack()


        '''
        Chart tab
        '''

        tab_chart = ttk.Frame(tab_control_master)
        tab_control_master.add(tab_chart, text='Chart Portal')

        tab_chart_frame_top = Frame(tab_chart, bd=0, bg=COLOR_GREEN)
        tab_chart_frame_top.pack(side=TOP, fill=BOTH, expand='true')
        tab_chart_frame_bottom = Frame(tab_chart, bd=0, bg=COLOR_GREEN)
        tab_chart_frame_bottom.pack(side=BOTTOM, fill=BOTH, expand='true')
        tab_chart_frame_toolbar = Frame(tab_chart, bd=0, bg=COLOR_GREEN)
        tab_chart_frame_toolbar.pack(side=BOTTOM, fill=BOTH, expand='true')


        default_ticker = 'AAPL'
        chart = Figure(figsize=(4, 12), dpi=100)
        ax = chart.add_subplot(111)
        def stock_chart(ticker):
            
            # chart data
            end = datetime.today() - timedelta(days=1)
            start = end - timedelta(days=365)
            df = yf.download(ticker, start=start, end=end, period='1d')

            # chart UI
            ax.set_facecolor(COLOR_BLACK)
            ax.plot(df['Adj Close']) # plot graph
            ax.set_title(stock_info(ticker).info['shortName'])
            ax.set_xlabel('Date')
            ax.set_ylabel('Price')
            ax.yaxis.label.set_color(COLOR_GREEN)
            ax.xaxis.label.set_color(COLOR_GREEN)
            ax.title.set_color(COLOR_GREEN)
            ax.spines['bottom'].set_color(COLOR_GREEN)
            ax.spines['top'].set_color(COLOR_GREEN)
            ax.spines['right'].set_color(COLOR_GREEN)
            ax.spines['left'].set_color(COLOR_GREEN)
            ax.tick_params(axis='x', colors=COLOR_GREEN)
            ax.tick_params(axis='y', colors=COLOR_GREEN)
            chart.set_facecolor(COLOR_BLACK)

            canvas = FigureCanvasTkAgg(chart, master=tab_chart_frame_bottom)
            canvas.draw()
            canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        def stock_info(ticker):
            symbol = yf.Ticker(ticker)
            return symbol

        def find_chart(ticker):
            ax.clear()
            stock_chart(ticker)

        # stock chart labels, entry
        l_chart_title = tk.Label(tab_chart_frame_top, text='Ticker:',
                                bg=COLOR_GREEN, fg=COLOR_BLACK)
        l_chart_title.pack(side=LEFT, padx=5)
        e_chart_find = tk.Entry(tab_chart_frame_top, width=12, border=0)
        e_chart_find.insert(END, default_ticker)
        e_chart_find.pack(side=LEFT, padx=3)

        b_chart_find = tk.Button(tab_chart_frame_top, text='Find', command=find_chart(str(e_chart_find.get())), border=0, highlightthickness = 0, bg=COLOR_GREEN, highlightcolor=COLOR_BLACK)
        b_chart_find.pack(side=LEFT, padx=3)
        e_chart_find.bind('<Return>', (lambda event: find_chart(str(e_chart_find.get()))))
        e_chart_find.pack(side=LEFT, padx=3)



        '''
        Stock tab
        '''

        tab_stock = ttk.Frame(tab_control_master)
        tab_control_master.add(tab_stock, text='Stock Portal')

        # frame for 'find bar' header and data
        frame_stock_header = Frame(tab_stock, bd=0, bg=COLOR_GREEN)
        frame_stock_bottom = Frame(tab_stock, bd=0, bg=COLOR_BLACK)

        frame_stock_desc = Frame(frame_stock_bottom, bd=0, bg=COLOR_BLACK)
        frame_stock_desc.pack(side=TOP, fill=BOTH, pady=3)

        frame_stock_header.pack(side=TOP, fill=BOTH, pady=3)
        frame_stock_bottom.pack(side=TOP, fill=BOTH)

        # stock tab - header label
        l_stock_title = tk.Label(frame_stock_header, text='Ticker:',
                                bg=COLOR_GREEN, fg=COLOR_BLACK)
        l_stock_title.pack(side=LEFT, padx=5)
        
        e_stock_find = tk.Entry(frame_stock_header, width=12, border=0)
        e_stock_find.insert(END, default_ticker)
        e_stock_find.pack(side=LEFT, padx=3)

        # stock tab - data labels
        l_stock_desc_title = tk.Label(frame_stock_desc, text='Description:',
                                bg=COLOR_BLACK, fg=COLOR_GREEN, anchor=NW)

        l_stock_desc = tk.Label(frame_stock_desc, text=stock_info(str(e_stock_find.get())).info['longBusinessSummary'], justify='left', wraplength=900, bg=COLOR_BLACK, fg=COLOR_GREEN)
        l_stock_desc.bind("<Configure>")
        l_stock_desc_title.pack(side=TOP)
        l_stock_desc.pack(side=TOP, padx=10)

        def find_stock(ticker):
            l_stock_desc.configure(text=stock_info(str(e_stock_find.get())).info['longBusinessSummary'])



        b_stock_find = tk.Button(frame_stock_header, text='Find', command=find_stock(str(e_stock_find.get())), border=0, highlightthickness = 0, bg=COLOR_GREEN, highlightcolor=COLOR_BLACK)
        b_stock_find.pack(side=LEFT, padx=3)
        e_stock_find.bind('<Return>', (lambda event: find_stock(str(e_stock_find.get()))))
        e_stock_find.pack(side=LEFT, padx=3)



        '''
        News tab
        '''
        
        tab_news = ttk.Frame(tab_control_master)

        tab_control_master.add(tab_news, text='News Portal')

        frame_news_top = Frame(tab_news, bd=0, bg=COLOR_GREEN)
        frame_news_bottom = Frame(tab_news, bd=0, bg=COLOR_BLACK)
        frame_news_top.pack(side=TOP, fill='both', expand='true', pady=3)
        frame_news_bottom.pack(side=BOTTOM, fill='both', expand='true')

        scrollbar_news = Scrollbar(frame_news_bottom)
        scrollbar_news.pack(side=RIGHT, fill='y')

        # create News Portal list box
        lb_news_1 = Listbox(frame_news_bottom, height=1400, width=900,
                            yscrollcommand=scrollbar_news.set, selectmode=EXTENDED,
                            highlightbackground=COLOR_BLACK, highlightthickness=8,
                            bg=COLOR_BLACK, fg=COLOR_GREEN, font='Menlo')
        lb_news_1.pack(side=RIGHT, fill='y')

        # populate news listbox with articles and associated links
        def retrieve_articles():

            # sort article's by published date
            article_list.sort(key=lambda k: (k[3], k[4]), reverse=True)

            # build news list box from article_list
            for article in article_list:
                article_display = '[' + str(article[2]) + ']' + ' - ' + article[0] + ' [' + article[5] + ']'
                lb_news_1.insert(END, article_display)
                if(article[6] == True):
                    lb_news_1.itemconfigure(index, fg="grey")

        # refresh default article list
        def refresh_default_feed():
            article_list.clear()
            lb_news_1.delete(0, tk.END)
            # build article_list (url_list comes from news_urls.py)
            for site in url_list:
                news(site)

            retrieve_articles()

        b_news_refresh = tk.Button(frame_news_top, text='Refresh Feed',
                                command=refresh_default_feed, border=0,
                                highlightthickness = 0, bg=COLOR_GREEN,
                                highlightcolor=COLOR_BLACK)
        b_news_refresh.pack(side=RIGHT, padx=5, pady=0)

        # open url function
        def open_url(*args):
            if(lb_news_1.curselection()):
                index = lb_news_1.curselection()[0]
                item = article_list[index][1]
                if 'http' in item:
                    webbrowser.open(item)
                    # label visited urls, maintains list upon refresh
                    lb_news_1.itemconfigure(index, fg="grey")
                    article_list[index][6] = True

        # bind double click and enter to open url function
        lb_news_1.bind('<Double-Button-1>', open_url)
        lb_news_1.bind('<Return>', open_url)

        '''
        Twitter tab
        '''

        # API keys
        keys = read_conf(KEYS_LOCATION)['MAIN']
        auth = tw.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
        auth.set_access_token(keys['access_token'], keys['access_token_secret'])
        api = tw.API(auth, wait_on_rate_limit=True)

        # twitter tab
        tab_twitter = ttk.Frame(tab_control_master)
        tab_control_master.add(tab_twitter, text='Tweet Portal')

        frame_twitter_top = Frame(tab_twitter, bd=0, bg=COLOR_GREEN)
        frame_twitter_bottom = Frame(tab_twitter, bd=0, bg=COLOR_BLACK)
        frame_twitter_top.pack(side=TOP, fill='both', expand='true', pady=3)
        frame_twitter_bottom.pack(side=BOTTOM, fill='both', expand='true')

        scrollbar_twitter = Scrollbar(frame_twitter_bottom)
        scrollbar_twitter.pack(side=RIGHT, fill='y')

        # create Tweet Portal list box
        lb_twitter_1 = Listbox(frame_twitter_bottom, height=1400, width=900,
                                yscrollcommand=scrollbar_twitter.set,
                            selectmode=EXTENDED,
                            highlightbackground=COLOR_BLACK, highlightthickness=8,
                            bg=COLOR_BLACK, fg=COLOR_GREEN, font='Menlo')
        lb_twitter_1.pack(side=TOP, fill='y')

        date_since = "2021-01-01"
        search_count = 10
        like_threshold = 1
        follower_threshold = 1000

        # search label and entry field
        l_twitter_1 = tk.Label(frame_twitter_top, text='Search:',
                                bg=COLOR_GREEN, fg=COLOR_BLACK)
        l_twitter_1.pack(side=LEFT, padx=5)
        e_twitter_search = tk.Entry(frame_twitter_top, width=12, border=0)
        e_twitter_search.pack(side=LEFT, padx=3)

        # count label and entry field
        l_twitter_count = tk.Label(frame_twitter_top, text='Count:',
                                bg=COLOR_GREEN, fg=COLOR_BLACK)
        l_twitter_count.pack(side=LEFT)
        e_twitter_count = tk.Entry(frame_twitter_top, width=4, border=0)
        e_twitter_count.insert(END, search_count)
        e_twitter_count.pack(side=LEFT, padx=3)

        # min(likes) label and entry field
        l_twitter_likes = tk.Label(frame_twitter_top, text='Min Likes:',
                                bg=COLOR_GREEN, fg=COLOR_BLACK)
        l_twitter_likes.pack(side=LEFT)
        e_twitter_likes = tk.Entry(frame_twitter_top, width=4, border=0)
        e_twitter_likes.insert(END, like_threshold)
        e_twitter_likes.pack(side=LEFT, padx=3)

        # min(followers) label and entry field
        l_twitter_followers = tk.Label(frame_twitter_top, text='Min Followers:',
                                bg=COLOR_GREEN, fg=COLOR_BLACK)
        l_twitter_followers.pack(side=LEFT)
        e_twitter_followers = tk.Entry(frame_twitter_top, width=4, border=0)
        e_twitter_followers.insert(END, follower_threshold)
        e_twitter_followers.pack(side=LEFT, padx=3)

        # collect default tweets (will allow user to initialize list)
        tweet_list = []
        def tweet(search_word):
            search_twitter = search_word.tag + '-filter:retweets'
            twitter = tw.Cursor(api.search,
                          q=search_twitter,
                          lang="en",
                          since=date_since).items(int(e_twitter_count.get()))

            for current_tweet in twitter:
                tweet_date = str(current_tweet.created_at)[0:22] #strip first 22 chars
                tweet_date = datetime.strptime(tweet_date, '%Y-%m-%d %H:%M:%S')

                #convert time from GMT to EST
                tweet_date = GMT.localize(tweet_date)
                tweet_date = tweet_date.astimezone(EST)
                tweet_hour = str(tweet_date.hour)
                tweet_minute = str(tweet_date.minute)

                if ((current_tweet.favorite_count >= int(e_twitter_likes.get())) and
                    (current_tweet.user.followers_count >= int(e_twitter_followers.get()))):
                    tweet_list.append([current_tweet.text, current_tweet.user.screen_name,
                                    f"https://twitter.com/{current_tweet.user.screen_name}/status/{current_tweet.id}",
                                    str(current_tweet.favorite_count), str(tweet_date.strftime("%I:%M %p")),
                                    int(tweet_hour), int(tweet_minute)])

        tab_control_master.pack()

        # create twitter_list (filters out retweets)
        for search_word in search_list:
            tweet(search_word)

        # populates twitter listbox with default search terms
        def retrieve_tweets(list):

            # sort tweets's by published date
            list.sort(key=lambda k: (k[5], k[6]), reverse=True)

            count = 1
            for current_tweet in list:
                tweet_display = '[' + current_tweet[4] + '] - '  + '@' + current_tweet[1] + '(🤍 ' + current_tweet[3] + '): ' + current_tweet[0]
                lb_twitter_1.insert(END, tweet_display)
                count += 1

        def search_twitter():
            count = 1
            tweet_list.clear()
            search_entry = e_twitter_search.get()
            search_return = tw.Cursor(api.search,
                          q=search_entry,
                          lang="en",
                          since=date_since).items(int(e_twitter_count.get()))

            for current_tweet in search_return:
                tweet_date = str(current_tweet.created_at)[0:22] #strip first 22 chars
                tweet_date = datetime.strptime(tweet_date, '%Y-%m-%d %H:%M:%S')

                #convert time from GMT to EST
                tweet_date = GMT.localize(tweet_date)
                tweet_date = tweet_date.astimezone(EST)
                tweet_hour = str(tweet_date.hour)
                tweet_minute = str(tweet_date.minute)

                if ((current_tweet.favorite_count >= int(e_twitter_likes.get())) and
                    (current_tweet.user.followers_count >= int(e_twitter_followers.get()))):
                    tweet_list.append([current_tweet.text, current_tweet.user.screen_name,
                                    f"https://twitter.com/{current_tweet.user.screen_name}/status/{current_tweet.id}",
                                    str(current_tweet.favorite_count), str(tweet_date.strftime("%I:%M %p")),
                                    int(tweet_hour), int(tweet_minute)])

            # clear tweet list box, repopulate
            lb_twitter_1.delete(0, tk.END)
            retrieve_tweets(tweet_list)

        b_twitter_search = tk.Button(frame_twitter_top, text='Search',
                                command=search_twitter, border=0, highlightthickness = 0,
                                bg=COLOR_GREEN, highlightcolor=COLOR_BLACK)
        b_twitter_search.pack(side=LEFT, padx=3)
        # using return on any field causes search event
        e_twitter_search.bind('<Return>', (lambda event: search_twitter()))
        e_twitter_count.bind('<Return>', (lambda event: search_twitter()))
        e_twitter_likes.bind('<Return>', (lambda event: search_twitter()))
        e_twitter_followers.bind('<Return>', (lambda event: search_twitter()))

        # open tweet function
        def open_tweet(*args):
            if(lb_twitter_1.curselection()):
                index = lb_twitter_1.curselection()[0]
                item = tweet_list[index][2]
                if 'http' in item:
                    webbrowser.open(item)
                    # label visited urls, maintains list upon refresh
                    lb_twitter_1.itemconfigure(index, fg="grey")

        # binds double click and enter to open url function
        lb_twitter_1.bind('<Double-Button-1>', open_tweet)
        lb_twitter_1.bind('<Return>', open_tweet)

        # refresh default tweet list
        def refresh_default_feed():
            tweet_list.clear()
            # rebuild tweet_list
            for search_word in search_list:
                tweet(search_word)

            lb_twitter_1.delete(0, tk.END)
            retrieve_tweets(tweet_list)

        b_twitter_refresh = tk.Button(frame_twitter_top, text='Refresh Feed',
                                command=refresh_default_feed, border=0,
                                highlightthickness = 0, bg=COLOR_GREEN,
                                highlightcolor=COLOR_BLACK)
        b_twitter_refresh.pack(side=RIGHT, padx=5, pady=0)

        '''
        Initialize default articles and tweets
        '''
        # run retrieve default articles and tweets first time
        stock_chart(default_ticker)
        retrieve_articles()
        retrieve_tweets(tweet_list)


        def _quit():
            root.quit()     # stops mainloop
            root.destroy()  # this is necessary on Windows to prevent
                            # Fatal Python Error: PyEval_RestoreThread: NULL tstate

'''
Main
'''

def main():
    root = tk.Tk()
    root.title('News Scraper')
    root.geometry('1000x1600')
    root.configure(bg=COLOR_BLACK)
    app = AppGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()

app.mainloop()


