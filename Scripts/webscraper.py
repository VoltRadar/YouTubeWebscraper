import datetime
import json
import os
import time

# All selenium imports
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Locations contains the locations for any elements on the YouTube page
from Scripts.YoutubeLocations import Locations


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

        self.youtubers = {}

    def __del__(self):
        """
        Quits the driver when this object is deleted
        :return:
        """
        self.driver.quit()

    def load_driver(self, debug=False):

        # If the webdriver is already loaded, just exit
        if self.driver is not None:
            return

        options = Options()

        if not debug:
            options.add_argument("--headless")
            # options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(options=options)

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
        """
        Load a page for YouTube, then click reject all if needed
        :param url:
        :return:
        """
        self.driver.get(url)
        self.click_reject_all()

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
                if not json_string:
                    # If the file is empty
                    titles_from_file = {}
                else:
                    titles_from_file = json.loads(json_string)
        except json.decoder.JSONDecodeError as e:
            raise json.decoder.JSONDecodeError(msg="Titles.txt corrupted: " + e.msg,
                                               doc=e.doc,
                                               pos=e.pos)
        except OSError:
            # No file called titles.txt, making a new file
            _ = open("titles.txt", "w")

            titles_from_file = {}

        titles_type = type(titles_from_file)
        if not isinstance(titles_type, dict):
            raise TypeError("Expected titles.txt type to be dict, "
                             f"but was type {titles_type.__name__}")

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

    def load_youtuber_names(self):
        """
        Loads the youtubers names from a file
        :return: None
        """

        if self.youtubers:
            # If YouTubers already loaded, then don't load them from the file
            return

        try:
            with open("YouTubers.txt", "r") as txt:
                self.youtubers = json.loads(txt.read())

        except json.decoder.JSONDecodeError as e:
            raise json.decoder.JSONDecodeError(msg="YouTubers.txt corrupted: " + e.msg,
                                               doc=e.doc,
                                               pos=e.pos)

        except OSError:
            # No YouTubers.txt file. Make a new one
            with open("YouTubers.txt", "w") as txt:
                txt.write("{}")

        if not isinstance(self.youtubers, dict):
            raise TypeError("Expected YouTubers.txt type to be dict, "
                             f"but was type {type(self.youtubers).__name__}")

    def save_youtuber_names(self):
        """Saves the self.youtubers dict"""

        youtubers_json_string = json.dumps(self.youtubers)

        # Make the file slightly easier to read
        youtubers_json_string = youtubers_json_string.replace('",', '",\n')

        with open("YouTubers.txt", "w") as txt:
            txt.write(youtubers_json_string)

    def add_youtuber(self, youtuber_name: str, youtuber_channel_name: str):
        """
        Raises TypeError if youtuber_name already exists in self.youtubers

        Adds a youtuber to the self.youtubers dict.
        If a YouTuber already has the same nickname,

        The youtuber_name will be a nickname that the program will use to refer
        to this youtuber e.g. "Tom Scott".

        The youtuber_channel_name is the youtuber channel name, found in the
        URL for their channel page. Tom Scott's URL is the following:
        https://www.youtube.com/@TomScottGo
        So in this case, their channel name should be "TomScottGo"

        :param youtuber_name: Nick name for youtuber
        :param youtuber_channel_name: name after @ symbol in channel URL
        :return:
        """
        if youtuber_name in self.youtubers:
            raise ValueError("YouTuber already exists")

        self.youtubers[youtuber_name] = youtuber_channel_name

    def scrap_titles(self) -> None:
        self.load_youtuber_names()

        self.load_driver()

        for name, channel_name in self.youtubers.items():
            url = self.get_youtuber_url(channel_name)
            self.load_page(url)
            self.click_reject_all()
            self.get_video_titles(name)

        self.save_video_titles()

        self.save_page()
        self.driver.quit()

    def test(self):
        self.load_youtuber_names()
        self.save_youtuber_names()
