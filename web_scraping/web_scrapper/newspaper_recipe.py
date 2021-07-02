import argparse
import logging
logging.basicConfig(level=logging.INFO)
from urllib.parse import urlparse
import pandas as pd
import hashlib
import nltk
from nltk.corpus import stopwords

logger = logging.getLogger(__name__)
stop_words = set(stopwords.words('spanish'))

def _read_data(filename):
    logger.info(f'Reading file {filename}')

    return pd.read_csv(filename, encoding='utf-8')


def _get_host(df):
    logger.info('Getting host from urls')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)

    return df


def _fill_missing_titles(df):
    logger.info('Filling missing titles')
    missing_titles_mask = df['title'].isna()

    missing_titles = (df[missing_titles_mask]['url']
                        .str.extract(r'(?P<missing_titles>[^/]+)/?$')
                        .applymap(lambda title: title.replace('-', ' ').capitalize())
                        )
    df.loc[missing_titles_mask, 'title'] = missing_titles.loc[:, 'missing_titles']

    return df


def _generate_rows_uids(df):

    logger.info('Generating uids for rows')
    uids = (df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest()))

    df['uid'] = uids

    return df.set_index('uid')


def _remove_new_lines(df):
    logger.info('Removing new lines from summary')

    stripped_summary = df.apply(lambda row: row['summary'].replace('\n', ''), axis=1)
    print(stripped_summary)
    df['summary'] = stripped_summary

    return df


def _tokenize_column(df, column_name):
    return(df
                .dropna()
                .apply(lambda row: nltk.word_tokenize(row[column_name]), axis = 1)
                .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
                .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
                .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list)))
                .apply(lambda valid_word_list: len(valid_word_list))
          )


def main(filename):
    logger.info('Starting cleaning process')

    df = _read_data(filename)
    newspaper_uid = filename.split('_')[0]
    logger.info(f'Newspaper uid: {newspaper_uid}')

    df['newspaper'] = newspaper_uid
    df = _get_host(df)
    df = _fill_missing_titles(df)
    df = _generate_rows_uids(df)
    df = _remove_new_lines(df)
    df['n_tokens_title'] = _tokenize_column(df, 'title')
    df['n_tokens_summary'] = _tokenize_column(df, 'summary')

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='Path to data')
    ARGS = parser.parse_args()

    df = main(ARGS.filename)
    print(df)