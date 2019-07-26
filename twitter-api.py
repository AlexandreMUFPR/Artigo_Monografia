#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys
import jsonpickle
import os
import tweepy
import csv
import json
import logging
logging.basicConfig(level=logging.INFO)

def search(api, sincedate, untildate, csvFile, jsonFile):
    searchQuery = '((cota OR cotas OR universidade OR universidades) AND (racial OR raciais)) OR ((universidade OR universidades) AND (cota OR cotas))'
    maxTweets = 10000000

    tweetsPerQry = 100  # this is the max the API permits

    csvWriter = csv.writer(csvFile)

    # If results from a specific ID onwards are reqd, set since_id to that ID.
    # else default to no lower limit, go as far back as API allows
    sinceId = None

    # If results only below a specific ID are, set max_id to that ID.
    # else default to no upper limit, start from the most recent tweet matching the search query.
    # Python3 has 9223372036854775807 as max number
    max_id = sys.maxsize

    tweetCount = 0
    print("Downloading max {0} tweets".format(maxTweets))
    while tweetCount < maxTweets:
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery,  since = sincedate, until = untildate, count=tweetsPerQry)
                else:
                    new_tweets = api.search(q=searchQuery,  until = untildate, count=tweetsPerQry, since_id=sinceId)
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery,  since = sincedate, until = untildate, count=tweetsPerQry, max_id=str(max_id - 1))
                else:
                    new_tweets = api.search(q=searchQuery,  until = untildate, count=tweetsPerQry, max_id=str(max_id - 1), since_id=sinceId)
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                json.dump(tweet._json, jsonFile)
                jsonFile.write('\n')
                csvWriter.writerow([
                    tweet.created_at,
                    tweet.id,
                    tweet.in_reply_to_status_id,
                    tweet.in_reply_to_user_id,
                    tweet.in_reply_to_screen_name,
                    tweet.user.id, tweet.user.screen_name,
                    tweet.user.followers_count,
                    tweet.is_quote_status,
                    tweet.retweet_count,
                    tweet.favorite_count,
                    tweet.lang,
                    tweet.text.encode('utf-8')])
                tweetCount += len(new_tweets)
                print("Downloaded {0} tweets".format(tweetCount))
                max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            print("some error: " + str(e))
            continue

    print ("Downloaded {0} tweets".format(tweetCount))

if __name__ == "__main__":
    ####input your credentials here
    consumer_key=''
    consumer_secret=''
    access_token=''
    access_token_secret=''
###

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    if( len(sys.argv) != 5):
        print("Usage "+sys.argv[0]+" <since date yyyy-mm-dd> <until date yyyy-mm-dd> <csv File> <json File>")
        sys.exit(1)

    # sincedate =  "2019-05-15"
    sincedate = sys.argv[1]
    # untildate = "2019-05-16"
    untildate = sys.argv[2]

    csvFile = open(sys.argv[3], 'a')
    jsonFile = open(sys.argv[4], 'a')
    search(api, sincedate, untildate, csvFile, jsonFile)
    csvFile.close()
    jsonFile.close()

