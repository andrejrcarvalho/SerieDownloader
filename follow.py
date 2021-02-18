import utils.cmd_gui as gui
import utils.imdb as Imdb
from utils.models import Serie, Episode
import math


def main():
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
    option = -1
    while option != 0:
        series_strings = []
        series_list = Serie.getList()
        for i in range(len(series_list)):
            serie = series_list[i]
            series_strings.append(f"{serie.name}\t{serie.status}")
        gui.clear()
        option = gui.menu("Series list", series_strings, "Exit", margin=10)

        if(option != 0):
            option1 = -1
            while option1 != 0:
                option1 = gui.menu("What you to do?", [
                    "Change the series episode status",
                    "Change the series global status"],
                    "Back", 10)
                if(option1 == 1):
                    select_season(series_list[option-1])
                elif (option1 == 2):
                    set_series_status(series_list[option-1])
                if option1 > 0 :   
                    option1 = 0


def set_series_status(serie):
    option = -1
    while option != 0:
        gui.clear()
        option = gui.menu(f"Change status -> {serie.name}", [
            Serie.STATUS_ENABLE if serie.status == Serie.STATUS_DISABLE else Serie.STATUS_DISABLE,
        ],
            "Back", margin=10)

        if option == 1:
            serie.status = Serie.STATUS_ENABLE if serie.status == Serie.STATUS_DISABLE else Serie.STATUS_DISABLE
            serie.save()
            option = 0


def select_season(serie):
    serie.loadSeasons()
    seasons_strings = []
    for i in range(len(serie.seasons)):
        seasons_strings.append(f"Season {i+1}")
    option = -1
    while option != 0:
        gui.clear()
        option = gui.menu(serie.name, seasons_strings, "Exit", margin=10)

        if(option != 0):
            select_episode(serie, option-1)


def select_episode(serie, season):
    episodes = serie.seasons[season]
    episodes_strings = []
    for i in range(len(episodes)):
        episode = episodes[i]
        episodes_strings.append(f"{episode.name}\t{episode.status}")
    option = -1
    while option != 0:
        episodes = serie.seasons[season]
        episodes_strings = []
        for i in range(len(episodes)):
            episode = episodes[i]
            episodes_strings.append(f"{episode.name}\t{episode.status}")
        gui.clear()
        option = gui.menu(f"{serie.name} -> Season {season+1}",
            episodes_strings, "Exit", margin=10)
        if option != 0:
            set_episode_status(episodes[option-1])


def set_episode_status(episode):
    option = -1
    while option != 0:
        gui.clear()
        option = gui.menu(f"Change status -> {episode.name}", [
            Episode.STATUS_UNLISTED,
            Episode.STATUS_PENDING,
            Episode.STATUS_UNDATED,
            Episode.STATUS_FAIL,
            Episode.STATUS_DONE,
        ],
            "Back", margin=10)

        if option == 1:
            episode.status = Episode.STATUS_UNLISTED
        elif option == 2:
            episode.status = Episode.STATUS_PENDING
        elif option == 3:
            episode.status = Episode.STATUS_UNDATED
        elif option == 4:
            episode.status = Episode.STATUS_FAIL
        elif option == 5:
            episode.status = Episode.STATUS_DONE

        if(option > 0):
            episode.save()
            option = 0
            

def delete_serie():
    pass
