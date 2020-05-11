from flask import Flask, render_template, request
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
from datetime import datetime, date, time, timedelta
from collections import Counter
import sys
import os
from textblob import TextBlob
app = Flask(__name__)

@app.route('/')
def student():
  os.system("python -m textblob.download_corpora")
  return render_template('start.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
       consumer_key = os.getenv("consumer_key")
       consumer_secret = os.getenv("consumer_secret")
       access_token = os.getenv("access_token")
       access_token_secret = os.getenv("access_token_secret")

       auth = OAuthHandler(consumer_key, consumer_secret)
       auth.set_access_token(access_token, access_token_secret)
       auth_api = API(auth)

       global_sentiment_undiv = 0

       username = request.form['Username']

       account_list = [username]

       account_name = ""

       if len(account_list) > 0:
           for target in account_list:
               print("Getting data for " + target)
               item = auth_api.get_user(target)
               print("name: " + item.name)
               account_name = item.name
               tweets = item.statuses_count
               tweet_count = 0
               rt_count = 0
               end_date = datetime.utcnow() - timedelta(days=1)
               for status in Cursor(auth_api.user_timeline, id=target).items():
                   tweet_count += 1
                   first_chars = status.text[0:4]
                   if first_chars != "RT @":

                       local_sentiment_undiv = 0

                       sentence_count = 0

                       blob = TextBlob(status.text)

                       for sentence in blob.sentences:
                           local_sentiment_undiv += sentence.sentiment.polarity

                           sentence_count += 1

                       local_sentiment = local_sentiment_undiv / sentence_count

                       global_sentiment_undiv += local_sentiment

                   else:

                       rt_count += 1

                   if status.created_at < end_date:
                       break
               if  (tweet_count - rt_count) > 0:

                   global_sentiment = global_sentiment_undiv / (tweet_count - rt_count)

                   if global_sentiment > 0:
                       result = account_name + " is in a Good Mood"
                       return render_template('result.html', result = result, emoji = ":grinning:")

                   elif global_sentiment == 0:
                       result = account_name + " is in a Neutral Mood"
                       return render_template('result.html', result = result, emoji = ":neutral_face:")
                   elif global_sentiment < 0:
                       result = account_name + " is in a Bad Mood"
                       return render_template('result.html', result = result, emoji = ":rage:")

                   print("All done. Processed " + str(tweet_count - rt_count) + " tweets.")

               else:
                   result = account_name + " hasn't tweeted in the past 24 hours."
                   return render_template('result.html', result = result, emoji = ":no_mouth:")

       ## return render_template("result.html", result=result)

if __name__ == '__main__':
   app.run(debug = True, host ="0.0.0.0")
