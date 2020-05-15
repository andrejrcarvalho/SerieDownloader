import json
import follow
import download, os.path
from utils import Database
from utils import Settings
from utils import CmdGui as gui

def start_modules():
    gui.header("Series Downloader", margin=20)

    gui.status_msg("Loading settins...")
    Settings(os.path.dirname(os.path.realpath(__file__)))

    gui.status_msg("Loading database...",newLine=True)
    Database(Settings.getInstance().database_file)


def main_menu():
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
            gui.progress("Updating", 1, afterLabel=f" {1}")
        elif option == 3:
            follow.main_menu()

if __name__ == "__main__":
    start_modules()
    main_menu()
