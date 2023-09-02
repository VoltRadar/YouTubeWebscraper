import datetime
import json
import traceback

# All selenium imports
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Locations contains the locations for any elements on the YouTube page
from YoutubeLocations import Locations

from Youtubers import Youtubers


class YoutubeWebscraper:
    """
    Webscraper for youtube to get some minor information
    """
    def __init__(self):
        self.driver: webdriver = None

        self.youtuber_titles = []
        self.youtuber = ""

    def load_driver(self):
        self.driver = webdriver.Firefox()

    def wait_for(self, location):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(location)
            )
            return element
        except TimeoutError as e:
            print("Time out")
            return None

    def load_page(self, url):
        self.driver.get(url)

    def save_page(self):
        """Wait a bit and save the page. Used in debugging"""
        self.driver.implicitly_wait(2)

        with open("page.txt", "wb") as txt:
            txt.write(self.driver.page_source.encode())

    def click_reject_all(self):
        """Rejects cookies from Youtube"""

        all_buttons = self.driver.find_elements(*Locations.buttons)
        reject_button = [b for b in all_buttons if "REJECT ALL" in b.text][0]
        reject_button.click()

    def get_video_titles(self, youtubername):
        """
        Waits for the videos page for a given youtuber to load, then saves the
        video titles in the self.youtuber_titles list

        :param youtubername: youtuber name
        :return:
        """

        # Wait until a video title is found
        self.wait_for(Locations.titles)

        # Wait 2 more seconds
        self.driver.implicitly_wait(2)

        all_title_elements = self.driver.find_elements(*Locations.titles)

        titles = []

        for ele in all_title_elements:
            try:
                title = ele.text
            except StaleElementReferenceException:
                # If title element doesn't exist anymore, then
                continue

            if title:
                titles.append(title)

        self.youtuber_titles = titles
        self.youtuber = youtubername

    def save_video_titles(self):
        """
        Saves the video titles from the youtuber titles list, along with a
        timestamp and youtuber name in the titles.txt file
        """

        # Loads the last youtuber titles. If the json fails, or file doesn't
        # exist, print to console and exit
        try:
            with open("titles.txt", "r") as txt:
                json_string = txt.read()
                json_string = json_string.replace("\n", "")
                titles = json.loads(json_string)
        except json.decoder.JSONDecodeError as e:
            print("JSON corrupted!")
            return
        except OSError as e:
            print("\"titles.txt\" failed to load!")
            return

        if self.youtuber in titles:
            their_titles = titles[self.youtuber]
        else:
            their_titles = {}
            titles[self.youtuber] = their_titles

        # Get the current timestamp
        current_time = datetime.datetime.now().replace(microsecond=0)
        time_stamp = current_time.isoformat()

        their_titles[time_stamp] = self.youtuber_titles

        with open("titles.txt", "w") as txt:
            json_string = json.dumps(titles)
            json_string = json_string.replace("{", "{\n").replace("}", "\n}\n")
            txt.write(json_string)

    def scrap_titles(self, youtuber):
        url = "https://www.youtube.com/@" + youtuber[1] + "/videos"
        self.load_driver()
        self.load_page(url)

        self.click_reject_all()
        self.get_video_titles(youtuber[0])
        self.save_video_titles()

        self.save_page()
        self.driver.quit()


YoutubeWebscraper().scrap_titles(Youtubers.tomscott)
