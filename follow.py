import utils.cmd_gui as gui
import utils.imdb as Imdb
from utils.models import Serie
import math

def main_menu():
    option = -1
    while option != 0:
        gui.clear()
        option = gui.menu("Follow List", [
            "View list",
            "Add new serie",
            "Remove serie",
            "Activate or Deactivate serie"],
            "Back to Main", 10)
        if option == 1:
            list_series()
        elif option == 2:
            add_new_series()
        elif option == 3:
            delete_serie()
        elif option == 4:
            change_serie_status()

def list_series():
    gui.clear()
    gui.header("Series list", margin=27)
    l = Serie.getList()
    output = ""
    for s in l:
        s.loadSeasons()
        output += s.name
        t = math.floor(len(s.name) / 4)
        for i in range(t, 8):
            output += "\t"
        output += f"{s.status}\n"
    print(output.expandtabs(4))
    gui.pause()
    pass

def add_new_series():
    option = -1
    imdbId = ""
    while(option != 0):
        option = gui.menu("Add new serie", [
            "From IMDB"],
            "Back", 10)
        if (option == 1):
            imdbId = Imdb.search_serie()

        if option > 0 and len(imdbId) > 0:
            __saveSerieToDb(imdbId)

def __saveSerieToDb(imdbId):
    if len(imdbId) == 0:
        raise Exception("Invalid imdbId")
    gui.progress("Fetching info", 1)
    serie = Imdb.getSerie(imdbId)
    gui.progress("Fetching info", 50)
    serie.save()
    gui.progress("Fetching info", 100)
    s_number = 1
    for s in serie.seasons:
        gui.progress("Saving to the database",
                     s_number * (100/(serie.number_seasons)), afterLabel=f"- Season {s_number} of {serie.number_seasons}")
        for e in s:
            e.save()
        s_number += 1

def change_serie_status():
    pass

def delete_serie():
    pass
