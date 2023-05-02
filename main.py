from typing import List

import feedparser
import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]


def parse_feed(feed_url: str):
    feed = feedparser.parse(feed_url)

    articles = []
    for record in feed.entries:
        article = {
            'title': record.title,
            'link': record.link,
            'published': record.published
        }
        articles.append(article)

    return articles


def generate_summary(article):
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


def aggregate_feeds(feed_urls: List[str]):
    articles = []
    for feed_url in feed_urls:
        feed_articles = parse_feed(feed_url)
        for article in feed_articles:
            article['summary'] = generate_summary(article)
            articles.append(article)

    articles = sorted(articles, key=lambda x: x['published'], reverse=True)
    return articles


def main():
    feed_urls = []
    with open('source.txt') as f:
        for line in f.readlines():
            feed_urls.append(line.strip())

    articles = aggregate_feeds(feed_urls)
    for article in articles:
        print(article['title'])
        print(article['link'])
        print(article['published'])
        print(article['summary'])
        print()


if __name__ == "__main__":
    main()
