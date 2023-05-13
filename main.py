from typing import List, Dict

import asyncio
import feedparser
import openai
import os
from time import time
from collections import defaultdict
import inspect

openai.api_key = os.environ["OPENAI_API_KEY"]


class Stats:
    def __init__(self):
        self.times = defaultdict(list)

    def track(self, f):
        key = f.__name__

        async def _async_f(*args, **kwargs):
            start = time()
            res = await f(*args, **kwargs)
            end = time()
            self.times[key].append(end - start)
            return res

        def _sync_f(*args, **kwargs):
            start = time()
            res = f(*args, **kwargs)
            end = time()
            self.times[key].append(end - start)
            return res

        return _async_f if inspect.iscoroutinefunction(f) else _sync_f

    def report(self):
        for k, v in self.times.items():
            print(f'{k} average: {sum(v) / len(v)}')


stats = Stats()


@stats.track
def parse_feed(feed_url: str):
    feed = feedparser.parse(feed_url)
    articles = []

    """
    rss_last_update = {} # k: url_feed, v: news_id

    if feed_url not in rss_last_update:
        rss_last_update.setdefault(feed_url, record.id)
    """

    for record in reversed(feed.entries[:4]):
        """if record.id == last_used_record_id:
            break"""
        
        article = {
            'title': record.title,
            'link': record.link,
            'published': record.published
        }
        articles.append(article)
        ##last_used_record_id = record.id

    return articles


@stats.track
async def generate_summary(article):
    prompt = f"Summarize this news article: {article['title']} {article['link']}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role': 'user',
             'content': f'{prompt}'
             }
        ],
        max_tokens=2049,
    )

    summary = response['choices'][0]['message']['content']
    return summary


@stats.track
async def aggregate_feeds(feed_urls: List[str]):
    articles = []
    for feed_url in feed_urls:
        feed_articles = parse_feed(feed_url)
        """
        generating_summaries = [generate_summary(article) for article in feed_articles]
        summaries = await asyncio.gather(*generating_summaries)
        for number, article in enumerate(feed_articles):
            article['summary'] = summaries[number]
            articles.append(article)
        """
    ##articles = sorted(articles, key=lambda x: x['published'], reverse=True)
    return feed_articles


async def main():
    feed_urls = []
    with open('source.txt') as f:
        for line in f.readlines():
            feed_urls.append(line.strip())

    articles = await aggregate_feeds(feed_urls)
    for article in articles:
        print(article['title'])
        print(article['link'])
        print(article['published'])
        ## print(article['summary'])
        print()

    print(stats.report())


if __name__ == "__main__":
    asyncio.run(main())
