import os
from Scripts.webscraper import YoutubeWebscraper, Youtubers

# Change the CWD to the Data folder


if __name__ == "__main__":
    os.chdir("Data")

    y = YoutubeWebscraper()
    y.scrap_titles([Youtubers.lemmino, Youtubers.tomscott])
    # TODO: Remake Youtubers.py as a text file in data
