import utils.cmd_gui as gui
from utils.models import Episode
import utils.imdb as Imdb

def main():
    gui.header("Series Update", margin=20)

    results = Episode.getList([Episode.STATUS_PENDING, Episode.STATUS_UNDATED])
    i = 1
    for e in results:
        p = (i * 100)/len(results)
        gui.progress("Downloading..", p, "{:.2f}%".format(p))
        episode = Imdb.getEpisode(e.id)
        if (e.status != Episode.STATUS_UNDATED):
            episode.status = e.status
        episode.save()
        i = i + 1
