import datetime
import json
import os
import time

# All selenium imports
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Locations contains the locations for any elements on the YouTube page
from Scripts.YoutubeLocations import Locations

# Names of youtubers
from Scripts.Youtubers import Youtubers


class YoutubeWebscraper:
    """
    Webscraper for youtube to get some minor information
    """
    def __init__(self):

        self.driver: webdriver = None

        # Dictionary of youtuber titles, keys are youtuber name, and values are a list of titles
        self.titles = {}

        # Have rejected cookies?
        self.clicked_cookies = False

    def load_driver(self):
        self.driver = webdriver.Chrome()
        self.clicked_cookies = False

    def wait_for(self, location):
        """
        Wait for an element in a given location
        :param location:
        :return:
        """
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(location)
            )
            return element
        except TimeoutError:
            print("Time out")
            return None

    def load_page(self, url):
        self.driver.get(url)

    def save_page(self):
        """Wait a bit and save the page. Used in debugging"""
        time.sleep(2)

        with open("page.txt", "wb") as txt:
            txt.write(self.driver.page_source.encode())

    def click_reject_all(self):
        """Rejects cookies from Youtube"""

        if self.clicked_cookies:
            # Already clicked cookies, searching for it causes a crash
            return

        all_buttons = self.driver.find_elements(*Locations.buttons)
        reject_button = [b for b in all_buttons if "REJECT ALL" in b.text][0]
        reject_button.click()

        self.clicked_cookies = True

    def get_video_titles(self, youtuber_name):
        """
        Waits for the videos page for a given youtuber to load, then saves the
        video titles in the self.youtuber_titles list

        :param youtuber_name: youtuber name
        :return:
        """

        # Wait until a video title is found
        self.wait_for(Locations.titles)

        time.sleep(2)

        all_title_elements = self.driver.find_elements(*Locations.titles)

        titles = []

        for ele in all_title_elements:
            try:
                title = ele.text
            except StaleElementReferenceException:
                # If title element doesn't exist anymore, then move on
                continue

            if title:
                titles.append(title)

        self.titles[youtuber_name] = titles

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
                titles_from_file = json.loads(json_string)
        except json.decoder.JSONDecodeError:
            print("JSON corrupted!")
            return
        except OSError:
            print("\"titles.txt\" failed to load!")
            return

        # Get the current timestamp
        current_time = datetime.datetime.now().replace(microsecond=0)
        time_stamp = current_time.isoformat()

        for youtuber, youtuber_titles in self.titles.items():
            if youtuber in titles_from_file:
                # Loads all seen titles seen from a given youtuber before,
                # with timestamps
                their_titles_from_file = titles_from_file[youtuber]
            else:
                their_titles_from_file = {}
                titles_from_file[youtuber] = their_titles_from_file

            # Adds the currently seen titles
            their_titles_from_file[time_stamp] = self.titles[youtuber]
            titles_from_file[youtuber] = their_titles_from_file

        with open("titles.txt", "w") as txt:
            json_string = json.dumps(titles_from_file)
            json_string = json_string.replace("{", "{\n").replace("}", "\n}\n")
            txt.write(json_string)

    @staticmethod
    def get_youtuber_url(youtube_channel_name: str) -> str:
        """
        Returns the videos url of a youtuber
        :param youtube_channel_name: channel name of a youtuber
        :return:
        """
        return "https://www.youtube.com/@" + youtube_channel_name + "/videos"

    def scrap_titles(self, youtubers) -> None:
        self.load_driver()

        for youtuber in youtubers:
            url = self.get_youtuber_url(youtuber[1])
            self.load_page(url)
            self.click_reject_all()
            self.get_video_titles(youtuber[0])

        self.save_video_titles()

        self.save_page()
        self.driver.quit()
