from imdb import IMDb, IMDbError
from utils import CmdGui as gui
from models.serie import Serie
from models.episode import Episode
from datetime import datetime
import sys

# https://imdbpy.readthedocs.io/en/latest/


def getSerie(imdbid):
    try:
        ia = IMDb()
        result = ia.get_movie(imdbid)
        serie = Serie()
        serie.id = result.getID()
        serie.name = result["long imdb title"]
        serie.number_seasons = result["number of seasons"]
        serie.status = Serie.STATUS_ENABLE
        serie.seasons = [0]*result["number of seasons"]
        
        ia.update(result, 'episodes')

        for season in result['episodes']:
            serie.seasons[season-1] = []
            for e in result['episodes'][season]:
                obj = result['episodes'][season][e]

                release_date = None
                status = Episode.STATUS_PENDING

                if (len(obj['original air date']) == 4):
                    status = Episode.STATUS_UNDATED
                else:
                    release_date = datetime.strptime(
                        obj['original air date'].replace('.', ''), '%d %b %Y')
                    if (release_date < datetime.now()):
                        status = Episode.STATUS_UNLISTED

                episode = Episode(obj.getID(), obj['title'],
                                obj['episode'], obj['season'],release_date,None,"",serie.id,status)
                serie.seasons[season - 1].append(episode)
        return serie
    except IMDbError as error:
        print(f"Imdb error:\n\t{error}")
    except:
        _show_errors()
    return None

def search_serie():
    gui.clear()
    gui.header("Search in IMDB:",10)
    to_search = input("=>")

    result = list()
    try:
        ia = IMDb()
        result = ia.search_movie(to_search)
    except IMDbError as error:
        print(f"Imdb error:\n\t{error}")
    except:
        _show_errors()

    result = list(
        filter(lambda i: i['kind'] == "tv series" or i['kind'] == "tv miniseries", result))
    n = 0
    option = -1
    while option not in range(0, len(result)+1):
        gui.clear()
        gui.header("Search in IMDB:",10)

        for n in range(0, len(result)):
            print(f"{n+1} - {result[n]['long imdb title']} ({result[n]['kind']})")

        try:
            print("Choose one of the result or 0 to return:")
            option = int(input("=>"))
            n = option-1
        except ValueError:
            option = -2
    if option > 0:
        return result[n].getID()
    return ""
    
def _show_errors():
    print(
        f"Unexpected error while getting IMDB data:", file=sys.stderr)
    for error in sys.exc_info():
        print(f"\t{error}", file=sys.stderr)
