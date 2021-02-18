import json
import follow
import update, download, os.path
from utils.database import Database
from utils.settings import Settings
import utils.cmd_gui as gui

def start_modules():
    gui.header("Series Downloader", margin=20)

    gui.status_msg("Loading settins...")
    Settings(os.path.dirname(os.path.realpath(__file__)))

    gui.status_msg("Loading database...",newLine=True)
    Database(Settings.getInstance().database_file)


def main():
    option = -1
    while option != 0:

        option = gui.menu("Main Menu", [
            "Download latest episodes",
            "Update series data",
            "Follow list"], "Exit", margin=10)
        gui.clear()

        if option == 1:
            download.main()
        elif option == 2:
            update.main()
        elif option == 3:
            follow.main()

if __name__ == "__main__":
    start_modules()
    main()
