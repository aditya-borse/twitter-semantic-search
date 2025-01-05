from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, json
from helper import TweetScrapper

option = Options()
option.add_experimental_option("debuggerAddress","localhost:9222")

driver = webdriver.Chrome(options=option)
scraper = TweetScrapper(driver)

# scraping bookmarks 
driver.get('https://x.com/i/bookmarks')
all_bookmarked_tweets = []
last_height = driver.execute_script('return document.body.scrollHeight')

while True:
    tweets = scraper.scrape_tweets()
    all_bookmarked_tweets.extend(tweets)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(2)
    new_height = driver.execute_script('return document.body.scrollHeight')
    if new_height == last_height:
        break
    last_height = new_height

# save in json file
with open('bookmarked_tweets.json', 'w', encoding='utf-8') as f:
    json.dump(all_bookmarked_tweets, f, ensure_ascii=False, indent=4)

print('bookmarked tweets save to bookmarked_tweets.json')
driver.quit()