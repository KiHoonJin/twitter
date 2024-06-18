import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
import time

def crawl_tweets(usernames):
    tweets = {}
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=chrome_options)

    driver.get('https://x.com/i/flow/login')
    driver.find_element(By.NAME, 'text').send_keys(os.getenv('TWITTER_USERNAME'))
    driver.find_element(By.NAME, 'text').send_keys(Keys.RETURN)
    time.sleep(2)
    driver.find_element(By.NAME, 'password').send_keys(os.getenv('TWITTER_PASSWORD'))
    driver.find_element(By.NAME, 'password').send_keys(Keys.RETURN)
    time.sleep(5)

    for user in usernames:
        driver.get(f'https://twitter.com/{user}')
        time.sleep(5)
        tweets[user] = []
        for tweet in driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="tweetText"]'):
            tweets[user].append(tweet.text)
    
    driver.quit()
    return tweets

def summarize_and_extract_keywords(tweets):
    summary = {}
    for user, tws in tweets.items():
        text = ' '.join(tws)
        summary[user] = {
            'summary': text[:500] + '...' if len(text) > 500 else text,
            'keywords': extract_keywords(text)
        }
    return summary

def extract_keywords(text):
    from collections import Counter
    words = text.split()
    keywords = Counter(words).most_common(10)
    return [word for word, freq in keywords]

st.title("Twitter Trend Analysis")
st.write("Analyze recent tweets from specified Twitter accounts and extract trends and keywords.")

user_input = st.text_area("Enter Twitter accounts (one per line)", "DegenerateNews\nWatcherGuru\nCoinDesk\nCointelegraph\ncrypto")
usernames = [u.strip() for u in user_input.split('\n') if u.strip()]

if st.button("Analyze"):
    with st.spinner("Crawling tweets..."):
        tweets = crawl_tweets(usernames)
    with st.spinner("Summarizing and extracting keywords..."):
        summary = summarize_and_extract_keywords(tweets)

    st.write("## Summary of Twitter Accounts")
    for user, data in summary.items():
        st.write(f"### {user}")
        st.write(f"**Summary:** {data['summary']}")
        st.write(f"**Keywords:** {', '.join(data['keywords'])}")

    st.write("## Raw Tweets")
    for user, tws in tweets.items():
        st.write(f"### {user}")
        st.write('\n'.join(tws))

if st.button("Download Summary"):
    with open('summary.txt', 'w', encoding='utf-8') as f:
        for user, data in summary.items():
            f.write(f"### {user}\n")
            f.write(f"**Summary:** {data['summary']}\n")
            f.write(f"**Keywords:** {', '.join(data['keywords'])}\n\n")
    st.success('Summary saved as summary.txt')

if st.button("Download Raw Data"):
    with open('raw_tweets.txt', 'w', encoding='utf-8') as f:
        for user, tws in tweets.items():
            f.write(f"### {user}\n")
            f.write('\n'.join(tws))
            f.write('\n\n')
    st.success('Raw data saved as raw_tweets.txt')