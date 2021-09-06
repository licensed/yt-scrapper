# Forked from: https://github.com/NihalSharama/Youtube-Scrapper
from selenium import webdriver
import argparse
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from time import time, sleep

# creating argument parser
parser = argparse.ArgumentParser(description='It will scrap using folowing inputs')
parser.add_argument('-s', '--searchterm', metavar='search_term', required=True,
                    help='Search term')
parser.add_argument('-f', '--filename', metavar='file_name', required=False, type=str,
                    help='Filename')

args = parser.parse_args()


class Scraper:
    def __init__(self, driver, timeout=5):
        self.driver = driver
        self.timeout = timeout

    def init_args(self, search_term, file_name='Scraped_data'):
        self.search_term = search_term
        self.file_name = file_name

    def persist_data(self, data):
        with open(f'{self.file_name}.csv', 'w', newline='', encoding='utf-8') as f:
            header = ['Name', 'Id', 'Description', 'Url', 'Img', 'Subscribers', 'links']
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)

    def get_channel_details(self, channelUrl):
        self.driver.get(channelUrl + "/about")
        css_selector_url = """#link-list-container.style-scope.ytd-channel-about-metadata-renderer
                            a.yt-simple-endpoint.style-scope.ytd-channel-about-metadata-renderer"""

        wait = WebDriverWait(self.driver, self.timeout)
        try:
            name = wait.until(EC.presence_of_element_located((By.ID, 'channel-name'))).text
            img = 0
            #img = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='inner-header-container']//yt-formatted-string[@class='style-scope ytd-channel-name']")))
            #img = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/ytd-app/div/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer")))
            #img = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "banner-visible-area style-scope ytd-c4-tabbed-header-renderer")))
            # class="banner-visible-area style-scope ytd-c4-tabbed-header-renderer"
            # element --yt-channel-banner: url
            channel = wait.until(EC.presence_of_element_located((By.XPATH, "//meta[@itemprop='channelId']")))
            channelId = channel.get_attribute("content")
            try:
                description = wait.until(
                    EC.presence_of_element_located((By.ID, 'description'))).text
            except Exception:
                description = 'Sorry but this channel dont add description'

            subscriberCount = wait.until(
                EC.presence_of_element_located((By.ID, 'subscriber-count'))).text
            try:
                links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector_url)))
                sleep(2)
            except TimeoutException:
                links = []
            img = wait.until(EC.presence_of_element_located((By.XPATH, "//img/@src")))
        except TimeoutException:
            print(f'Timeout. {self.timeout} second')

        channel_links = []
        if len(links) != 0:
            for channel_link in links:
                channel_links.append(channel_link.get_attribute('href'))

        channel_data = (name, channelId, description, channelUrl, img, subscriberCount, channel_links)

        return channel_data

    def main(self):
        #sp parameter is channel search only
        #2DO: Load more than 20 datas
        self.driver.get(f'https://www.youtube.com/results?search_query={self.search_term}&sp=EgIQAg%253D%253D')
        sleep(3)
        channelsElement = self.driver.find_elements_by_xpath('//*[@id="main-link"]')
        ChannelsUrl = set()

        for url in channelsElement:
            url = url.get_attribute('href')
            ChannelsUrl.add(url)

        channels_Data = []
        for channelUrl in ChannelsUrl:
            channel_data = self.get_channel_details(channelUrl)
            channels_Data.append(channel_data)

        self.driver.close()
        self.persist_data(channels_Data)


option = webdriver.FirefoxOptions()
option.add_argument("--incognito")

driver = webdriver.Firefox()
# driver.maximize_window()

start_time = time()
scraper = Scraper(driver, timeout=3)
scraper.init_args(args.searchterm, args.filename)
scraper.main()

print(f"Total time taken by scraping is {time()-start_time}")
