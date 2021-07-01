import argparse
import logging
logging.basicConfig(level=logging.INFO)
from urllib.parse import urlparse
import pandas as pd

logger = logging.getLogger(__name__)


def _read_data(filename):
    logger.info(f'Reading file {filename}')

    return pd.read_csv(filename, encoding='utf-8')


def _get_host(df):
    logger.info('Getting host from urls')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)

    return df


def main(filename):
    logger.info('Starting cleaning process')

    df = _read_data(filename)
    newspaper_uid = filename.split('_')[0]
    logger.info(f'Newspaper uid: {newspaper_uid}')

    df['newspaper'] = newspaper_uid
    df = _get_host(df)

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='Path to data')
    ARGS = parser.parse_args()

    df = main(ARGS.filename)
    print(df)