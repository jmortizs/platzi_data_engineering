import argparse
import logging
logging.basicConfig(level=logging.INFO)

import news_page_objects as news

from common import config

logger = logging.getLogger(__name__)

def _news_scraper(news_site_uid):
    host = config()['news_sites'][news_site_uid]['url']
    logging.info(f' Beginnig scraper for {host}')
    homepage = news.HomePage(news_site_uid, host)

    for link in homepage.article_links:
        print(link)

if __name__ == '__main__':

    news_site_choices = list(config()['news_sites'].keys())
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--news_site', type=str, choices=news_site_choices,
        help='News side that you want to scrape')

    ARGS = parser.parse_args()

    _news_scraper(ARGS.news_site)

    pass