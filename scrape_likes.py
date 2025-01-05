from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, json, os
from helper import TweetScrapper
from dotenv import load_dotenv

load_dotenv()
option = Options()
option.add_experimental_option("debuggerAddress","localhost:9222")

driver = webdriver.Chrome(options=option)
scraper = TweetScrapper(driver)
twitter_username = os.environ.get('TWITTER_USERNAME')

# scraping likes 
driver.get(f'https://x.com/{twitter_username}/likes')
all_liked_tweets = []
last_height = driver.execute_script('return document.body.scrollHeight')
max_tweets = 2000

while True:
    tweets = scraper.scrape_tweets()
    all_liked_tweets.extend(tweets)

    if len(all_liked_tweets) >= max_tweets:
        break

    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(2)
    new_height = driver.execute_script('return document.body.scrollHeight')
    if new_height == last_height:
        break
    last_height = new_height

# save in json file
with open('liked_tweets.json', 'w', encoding='utf-8') as f:
    json.dump(all_liked_tweets, f, ensure_ascii=False, indent=4)

print(f'{len(all_liked_tweets)} liked tweets save to liked_tweets.json')
driver.quit()