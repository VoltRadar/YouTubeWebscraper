import os
from Scripts.interface import WebscraperInterface

# Change the CWD to the Data folder


if __name__ == "__main__":
    os.chdir("Data")

    itr = WebscraperInterface()
    itr.start()
