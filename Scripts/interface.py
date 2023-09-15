import json
import requests

from Scripts.webscraper import YoutubeWebscraper


class WebscraperInterface:
    """
    Provides a command line interface for the YoutubeWebscraper interface
    """
    def __init__(self):
        self.scraper: YoutubeWebscraper = YoutubeWebscraper()

    @staticmethod
    def handle_json_error(exception: json.JSONDecodeError):
        """
        Print information for the user to solve
        :param exception:
        :return:
        """
        print("JSON Error!")
        print(exception.msg)

        # Position where the error occurred
        pos = exception.pos

        delta = 7
        location_lower_index = max(0, pos - delta)
        location_upper_index = min(pos + delta, len(exception.doc))

        error_string = exception.doc[location_lower_index: location_upper_index]
        pointer_string = " " * (min(pos, delta)) + "^"

        print("Error was found around here:")
        print()
        print(error_string)
        print(pointer_string)

    @staticmethod
    def handle_incorrect_type_from_file_error(exception: TypeError):
        """
        Handles a Value error for an incorrect type loaded from the file
        :return:
        """
        print("Incorrect type loaded from file:")
        print(exception.args[0])
        print("Adjust the file to a dict object")

    def display_subscribed(self):
        """
        Displays the YouTubers subscribed to in the YouTubers.txt file
        :return:
        """

        try:
            self.scraper.load_youtuber_names()
        except json.JSONDecodeError as e:
            # Display error info
            self.handle_json_error(e)
            return
        except TypeError as e:
            self.handle_incorrect_type_from_file_error(e)
            return

        print("YouTubers subscribed to:")
        numb = len(self.scraper.youtubers)
        if not numb:
            print("None subscribed yet")
            return

        for youtuber_name, channel_name in self.scraper.youtubers.items():
            print(f"{youtuber_name}", end="")

            if youtuber_name != channel_name:
                print(f" ({channel_name})")
            else:
                print()

        print()

    def add_youtuber(self):
        """
        Displays prompts to add a youtuber to track
        :return:
        """

        while True:
            print("Please enter the channel name for the YouTuber")
            print("It can be found in the URL of the channel page (https://www.youtube.com/@{ChannelName})")
            channel_name = input("> ")

            print("Checking if this channel exists...")

            # Check channel exists
            url = self.scraper.get_youtuber_url(channel_name)
            self.scraper.load_page(url)

            if "404 not found" in self.scraper.driver.title.lower():
                print("Channel doesn't seem to exist")
                print("Hit enter to try again, or type 'quit' then enter")

                inp = input("> ")
                if inp and inp[0].lower() == "q":
                    return
                else:
                    continue
            else:
                print("It does!")

            print(f"Give a nickname to {channel_name} (You can leave this blank)")
            youtuber_name = input("> ")

            if not youtuber_name:
                youtuber_name = channel_name

            self.scraper.add_youtuber(youtuber_name=youtuber_name,
                                      youtuber_channel_name=channel_name)

            print()
            return

    def start(self):
        """
        Starts the interface
        :return:
        """
        print("Welcome to the YouTube Webscaper!")
        print()

        self.scraper.load_driver(debug=False)

        while True:
            self.display_subscribed()
            self.add_youtuber()

