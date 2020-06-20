import re
import os
import time
from collections import Counter

import settings

import tweepy
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
from google.cloud import translate_v2 as translate


class tweetWords:

    def __init__(self, country, language, twitteritems=1000):
        assert isinstance(country, str), 'Country must be fully spelled out string.'
        assert isinstance(language, str), 'Language must be a string.'
        assert len(language) == 2, 'Language must be two letter abbreviation.'
        self.country = country
        self.language = language.lower()

        self.twitteritems = twitteritems

        self.tweetList = []
        self.wordList = []
        self.wordDF = pd.DataFrame()

    def fetch_tweets(self):
        """
        Connects to twitter API, collects tweets in specified lanuage/country, 
        and appends to internal list tweetList.
        """

        print('Connecting to Twitter API...')

        auth = tweepy.OAuthHandler(
            settings.consumer_key, settings.consumer_secret)
        auth.set_access_token(settings.access_token,
                              settings.access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        places = api.geo_search(query=self.country, granularity="country")
        place_id = places[0].id

        print('Connected. Fetching tweets...')

        attempts = 0
        while attempts < 5:
            attempts += 1
            tweets = tweepy.Cursor(api.search, q="place:%s" % place_id,
                                   lang=self.language).items(self.twitteritems)
            self.tweetList = [tweet.text for tweet in tweets]

            if len(self.tweetList) == self.twitteritems:
                print(str(len(self.tweetList)) + ' tweets fetched.')
                break
            else:
                print('Twitter API rate limited. Only ' + str(len(self.tweetList)) +
                      ' tweets fetched. Resuming in 16 min.')  # API throttling is in 15 min increments
                time.sleep(960)
                continue

    def count_words(self):
        """
        Parses individual words in internal list tweetList, counts each word, 
        and populates internal dataframe wordDF.
        """

        print('Counting words...')
        counts = Counter()
        wordReg = re.compile(r'\w+')

        for sentence in self.tweetList:
            counts.update(wordReg.findall(sentence.lower()))
        self.wordList = [x for x, _ in counts.most_common() if len(x) <= 45]
        self.wordDF = pd.DataFrame(counts.most_common())
        self.wordDF.columns = ['word', 'wordcount']
        self.wordDF.country = self.country

        print(str(len(self.wordDF.index)) + ' words added to dataframe.')

    def translate_words(self):
        """
        Passes words in wordList to Google Translate API and appends translations to dataframe.
        """

        print('Connecting to Google Translate API...')

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.googleJSON
        client = translate.Client()
        translated = []

        print('Translating words...')
        for word in self.wordList:
            translatedWord = client.translate(word, target_language='en')
            translated.append(translatedWord)

        print('Translation complete, appending to main dataframe.')

        transDF = pd.DataFrame(translated)
        transDF.columns = ['language', 'word', 'translation']
        self.wordDF = pd.merge(self.wordDF, transDF, on='word')
        self.wordDF = self.wordDF[self.wordDF.language == self.language]

        print('Appending complete.')

    def exportCSV(self, wordCount=10):
        """
        Generates CSV file with translated words.

        PARAM:
            wordCount (int) - count frequency threshhold that determines what words are exported.
        """
        limDF = self.wordDF[self.wordDF.wordcount >= wordCount]
        limDF = limDF[['word', 'translation']]
        limDF.to_csv(self.country + ' ' + self.language + ' deck.csv',
                     index=False)
        print("Export to .csv complete.")

    def save_words(self):
        """
        Connects to MySQL database using imported **kwargs from gitignored settings file. 
        Inserts each word and triggers a de-dup SPROC.
        """

        cnx = mysql.connector.connect(**settings.DBconfig)
        print('Connected to database, inserting rows...')

        columns = ["word", "wordcount", "country", "language", "translation"]

        insCursor = cnx.cursor()
        add_word = ("INSERT INTO words (" + ", ".join(columns) + ") VALUES (%s, \
                     %s, %s, %s, %s)")
        for i in range(len(self.wordDF)):
            word_data = [self.wordDF.iloc[i, 0], str(self.wordDF.iloc[i, 1]),
                         self.country, self.language, self.wordDF.iloc[i, 3]]
            insCursor.execute(add_word, word_data)
            cnx.commit()

        cnx.commit()
        insCursor.callproc('Consolidate_Words')
        insCursor.close()

        cnx.close()
        print('Insert complete.')


if __name__ == '__main__':

    countryToSearch = 'Spain'
    languageToSearch = 'es'
    twitteritems = 1000

    spanishWords = tweetWords(countryToSearch, languageToSearch, twitteritems)
    spanishWords.fetch_tweets()
    spanishWords.count_words()
    spanishWords.translate_words()
    spanishWords.exportCSV()
    spanishWords.save_words()
