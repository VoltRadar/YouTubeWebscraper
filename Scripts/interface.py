import json

from Scripts.webscraper import YoutubeWebscraper


class WebscraperInterface:
    """
    Provides a command line interface for the YoutubeWebscraper interface
    """
    def __init__(self):
        self.scraper = YoutubeWebscraper()

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

    def start(self):
        """
        Starts the interface
        :return:
        """
        print("Welcome to the YouTube Webscaper!")
        self.display_subscribed()
