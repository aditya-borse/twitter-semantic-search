from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class TweetScrapper:
    def __init__(self, driver):
        self.driver = driver

    def _parse_count(self, count_text):
        if not count_text:
            return 0

        multiplier = 1
        if 'K' in count_text:
            multiplier = 1000
            count_text = count_text.replace('K', '')
        elif 'M' in count_text:
            multiplier = 1000000
            count_text = count_text.replace('M', '')

        try:
            return float(count_text) * multiplier
        except (ValueError, TypeError):
            return 0

    def _get_element_text(self, tweet_element, selector, default=''):
        try:
            element = tweet_element.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except NoSuchElementException:
            return default

    def scrape_tweet(self, tweet_element):
        tweet_data = {}

        try:
            user_element = tweet_element.find_element(
                By.CSS_SELECTOR, '[data-testid="User-Name"]')
            tweet_data['username'] = self._get_element_text(
                user_element, 'div:nth-child(1) > div:nth-child(1) > a > div > span').replace("@", "")
            time_element = user_element.find_element(By.CSS_SELECTOR, 'time')
            tweet_data['timestamp'] = time_element.get_attribute('datetime')
        except NoSuchElementException:
            tweet_data['username'] = ''
            tweet_data['handle'] = ''
            tweet_data['timestamp'] = ''
        
        tweet_data['text'] = self._get_element_text(
            tweet_element,
            '[data-testid="tweetText"]'
        )

        metrics = {}
        try:
            replies = self._get_element_text(
                tweet_element,
                '[data-testid="reply"] [data-testid="app-text-transition-container"]'
            )
            metrics['replies'] = self._parse_count(replies)

            reposts = self._get_element_text(
                tweet_element,
                '[data-testid="retweet"] [data-testid="app-text-transition-container"]'
            )
            metrics['reposts'] = self._parse_count(reposts)

            likes = self._get_element_text(
                tweet_element,
                '[data-testid*="like"] [data-testid="app-text-transition-container"]'
            )
            metrics['like'] = self._parse_count(likes)

            views = self._get_element_text(
                tweet_element,
                'a[href*="/analytics"] [data-testid="app-text-transition-container"]'
            )
            metrics['views'] = self._parse_count(views)
        except NoSuchElementException:
            pass

        tweet_data['metrics'] = metrics

        try:
            time_link = tweet_element.find_element(By.CSS_SELECTOR, 'time').find_element(By.XPATH, '..')
            tweet_data['url'] = time_link.get_attribute('href')
        except NoSuchElementException:
            tweet_data['url'] = ''
        
        return tweet_data
    
    def scrape_tweets(self, wait_time=10):
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
            )

            tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
            tweets_data = []
            for tweet_element in tweet_elements:
                tweet_data = self.scrape_tweet(tweet_element)
                tweets_data.append(tweet_data)
            
            return tweets_data
        except TimeoutException:
            print('Timeout waiting for tweets to load')
            return []