from apscheduler.schedulers.blocking import BlockingScheduler
from pandas.io.json import json_normalize
import datetime
import requests
import feedparser
import os
import sys

previous_msg = ""

def telegram_bot_sendtext(bot_token, chat_id, bot_message):
   send_text = 'https://api.telegram.org/bot' + bot_token + \
       '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + bot_message
   response = requests.get(send_text)
   return response.json()


def get_feed(theme, language):
    failed = False
    try:
        if language == "pt":
            feed = feedparser.parse(
                "https://news.google.com/rss/search?q="+theme+"&hl=pt-BR&gl=BR&ceid=BR:pt-419")
        elif language == "en":
            feed = feedparser.parse(
                "https://news.google.com/rss/search?q="+theme+"&hl=en-GB&gl=GB&ceid=GB:en")
        else:
            print("Language " + language + "not implemented")
    except:
        print("Error trying to get the items")
        failed = True
    return feed


def get_news(bot_token, chat_id, theme, language):
    global previous_msg
    feed = get_feed(theme, language)

    df_news_feed = json_normalize(feed.entries)
    title = df_news_feed.get("title")[0]
    link = df_news_feed.get("links")[0][0].get("href")
    
    if not title == previous_msg:
        bot_message = "We have some news about *" + theme + \
            "* \n" + "title: " + title + "\n link: " + link
        telegram_bot_sendtext(bot_token, chat_id, bot_message)

    previous_msg = title

def initial_news_send(bot_token, chat_id, theme, language, quantity):
    for i in range(1,quantity):
        feed = get_feed(theme, language)

        df_news_feed = json_normalize(feed.entries)
        title = df_news_feed.get("title")[i]
        link = df_news_feed.get("links")[i][0].get("href")
        
        bot_message = "We have some news about *" + theme + \
        "* \n" + "Title: *" + title + "*\n Link: " + link
        
        telegram_bot_sendtext(bot_token, chat_id, bot_message)

def main(bot_token, chat_id, theme, language, quantity):
    initial_news_send(bot_token, chat_id, theme, language, quantity)

    scheduler = BlockingScheduler()
    scheduler.add_job(get_news, trigger='interval', seconds=5, next_run_time=datetime.datetime.now(
    ), args=(bot_token, chat_id, theme, language))
    scheduler.start()


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print("Usage: python generic_news_bot.py bot_token chat_id theme language initial_quantity")
        exit(0)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]))
