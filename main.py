import os
from Scripts.interface import WebscraperInterface


if __name__ == "__main__":
    # Change the CWD to the Data folder
    os.chdir("Data")

    itr = WebscraperInterface()
    itr.start()
