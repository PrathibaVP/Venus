# pip install snscrape
# pip install streamlit
# pip install pymongo

import datetime
import snscrape.modules.twitter as sntwitter
import streamlit as st
import pandas as pd
import pymongo
from pymongo import MongoClient
from PIL import Image
from datetime import date
import json

# Mongodb client connection is done
client = MongoClient("mongodb://localhost:27017/")
db = client.twitter_Scrape
record = db.Scrapped_data

# twitter scraping image,titles, and sub-heading
# img = Image.open(r"C:\Users\prath\OneDrive\Desktop\twt.jpg")
# st.image(img)
#st.image(image, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
st.header('Twitter Scraping page')
st.subheader("Scrape Tweets with your wish!")

#Creating the empty list to add the data
twt_list = []

# Menus used in Twitter Scrape web app -- 5 menus are used
choice = st.sidebar.selectbox('Menu',["Home","About","Search","Display","Download"])

#Menu "home"
if choice == "Home":
    st.write('''This app is a Twitter Scraping web app created using Streamlit.
             It scrapes the twitter data for the given hashtag/ keyword for the given period.
             The tweets are uploaded in MongoDB and can be dowloaded as CSV or a JSON file.''')

#Menu 'about'
elif choice=="About":
   # Info about Twitter Scrapper
     st.write('''Twitter Scraper will scrape the data from Public Twitter profiles.
                    It will collect the data about **date, id, url, tweet content, users/tweeters,reply count, 
                    retweet count, language, source, like count, followers, friends** and lot more information 
                    to gather the real facts about the Tweets.''')

#Menu "search"
elif choice=="Search":

    # First we need to clear the previous scraped tweets
    clear = record.delete_many({})

    item = st.selectbox('Through which way you wanted to get search ?',['Hashtag','username'])
    st.write('you have selected', item)
    items = ['Hashtag','username']

    #getting dates from user
    d1 = st.date_input('Enter the start date:',datetime.date(2023, 2, 1))
    st.write('Tweets starts from', d1)

    d2 = st.date_input('Enter the end date:',datetime.date(2023, 3, 1))
    st.write('Tweets ended at', d2)

    #Getting text to search from user and scrap the tweets using snscrap
    if item in items:
        search_text = st.text_input('Enter the text:')
        date_range = ' since:'+d1.strftime("%Y-%m-%d")+' until:'+d2.strftime("%Y-%m-%d")
        query= search_text+date_range
        number = st.number_input('Enter the number of tweets you wanted to scrape',1,1000)
        st.write(query)

       # collecting all the data using the sncrape i.e. sntwitter
        scraper = sntwitter.TwitterSearchScraper(query)
        st.write(scraper)
        for i, tweet in enumerate(scraper.get_items()):
            if i >(number - 1):
                break
            twt_list.append([tweet.date, tweet.id, tweet.content, tweet.user.username, tweet.replyCount, tweet.retweetCount, tweet.lang, tweet.source, tweet.likeCount, tweet.url])

        #Here we converted data into dataframe using pandas
        df1 = pd.DataFrame(twt_list, columns=['Datetime', 'Tweet Id', 'Text', 'Username', 'Reply Count', 'Retweet_Count','Language', 'Source', 'Like_Count', 'URL'])

        #storing dataframe into mongodb with json
        tweet_data = json.loads(df1.to_json(orient='records'))
        record.insert_many(list(tweet_data))
        st.write('Tweets successfully scraped')

#menu 'Display'
elif choice=="Display":
    # Save the documents in a dataframe
    df2 = pd.DataFrame(list(record.find()))
    #Dispaly the document
    st.dataframe(df2)

# Menu 5 is for Downloading the scraped data as CSV or JSON
else:
   col1, col2 = st.columns(2)

   # Download the scraped data as CSV
   with col1:
       st.write("Download the tweet data as CSV File")
       # save the documents in a dataframe
       df = pd.DataFrame(list(record.find()))
       # Convert dataframe to csv
       df.to_csv('twittercsv.csv')


       def convert_df(data):
           # Cache the conversion to prevent computation on every rerun
           return df.to_csv().encode('utf-8')


       csv = convert_df(df)
       st.download_button(
           label="Download data as CSV",
           data=csv,
           file_name='twtittercsv.csv',
           mime='text/csv',
       )
       st.success("Successfully Downloaded data as CSV")

   # Download the scraped data as JSON

   with col2:
       st.write("Download the tweet data as JSON File")
       # Convert dataframe to json string instead as json file
       twtjs = df.to_json(default_handler=str).encode()
       # Create Python object from JSON string data
       obj = json.loads(twtjs)
       js = json.dumps(obj, indent=4)
       st.download_button(
           label="Download data as JSON",
           data=js,
           file_name='twtjs.js',
           mime='text/js',
       )
       st.success("Successfully Downloaded data as JSON")