import re
import csv
import logging
logging.basicConfig(level=logging.INFO)

import argparse
import datetime
import news_page_objects as news

from common import config
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

logger = logging.getLogger(__name__)
is_welL_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')


def _news_scraper(news_site_uid):
    host = config()['news_sites'][news_site_uid]['url']
    logging.info(f' Beginnig scraper for {host}')
    homepage = news.HomePage(news_site_uid, host)

    articles = []
    for link in homepage.article_links:
        article = _fetch_article(news_site_uid, host, link)

        if article:
            logger.info(' Article fetched.')
            articles.append(article)

    _save_articles(news_site_uid, articles)


def _save_articles(news_site_uid, articles):
    now = datetime.datetime.now().strftime('%Y_%m_%d')
    out_file_name = f'{news_site_uid}_{now}_articles.csv'

    csv_headers = filter(lambda property: not property.startswith('_'), dir(articles[0]))
    csv_headers = list(csv_headers)

    with open(out_file_name, 'w+') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for article in articles:
            row = [str(getattr(article, prop)) for prop in csv_headers]
            writer.writerow(row)


def _fetch_article(news_site_uid, host, link):
    logger.info(f' Start fetching article at {link}')

    article = None
    try:
        article = news.ArticlePage(news_site_uid, _build_link(host, link))
    except (HTTPError, MaxRetryError) as e:
        logger.warning(' Error while fetching article', exc_info=False)

    if article and not article.summary:
        logger.warning(' Invalid article. There is no summary')
        return None

    return article


def _build_link(host, link):

    if is_welL_formed_link.match(link):
        return link

    elif is_root_path.match(link):
        return f'{host}{link}'

    else:
        return f'{host}/{link}'


if __name__ == '__main__':

    news_site_choices = list(config()['news_sites'].keys())
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--news_site', type=str, choices=news_site_choices,
        help='News side that you want to scrape')

    ARGS = parser.parse_args()

    _news_scraper(ARGS.news_site)
