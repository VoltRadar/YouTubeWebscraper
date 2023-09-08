import os
from Scripts.webscraper import YoutubeWebscraper

# Change the CWD to the Data folder


if __name__ == "__main__":
    os.chdir("Data")

    y = YoutubeWebscraper()
    y.scrap_titles()
    # GitHub testing
