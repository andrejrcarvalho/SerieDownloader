from models import Episode, Serie
from utils import CmdGui as gui
from datetime import datetime
from utils import TorrentAPI, Status
from utils import TPB
from utils import Settings
import re, time, sys, os
from threading import Thread, Lock

total_process = 0


def main():
    threads_list = list()
    uTorrent_mutex = Lock()
    global_vars_mutext = Lock()
    stdout_mutext = Lock()

    uTorrent = TorrentAPI(
        Settings.getInstance().utorrent_gui_url,
        Settings.getInstance().utorrent_gui_user,
        Settings.getInstance().utorrent_gui_password)

    if not uTorrent.is_authenticated():
        gui.pause()
        return

    global total_process
    total_process = 0

    for e in Episode.getList([Episode.STATUS_PENDING, Episode.STATUS_FAIL]):
        if (e.serie.status == Serie.STATUS_ENABLE and e.release_date <= datetime.now()):
            thread = Episode_Downloader(
                e, uTorrent, uTorrent_mutex, global_vars_mutext, stdout_mutext)
            threads_list.append(thread)
            thread.start()
    
    while check_thread_live(threads_list):
        p = total_process / len(threads_list)
        with stdout_mutext:
            gui.progress("Downloading..", p, "{:.2f}%".format(p))

    for thread in threads_list:
        thread.join()

    print("\nALL DOWNLOADS DONE")
    gui.pause()

def check_thread_live(thread_list):
    for t in thread_list:
        if t.isAlive():
            return True
    return False

class Episode_Downloader(Thread):

    def __init__(self, episode, torrentAPI, utorrent_mutex, global_vars_mutext, stdout_mutext):
        Thread.__init__(self)
        self.utorrent_mutex = utorrent_mutex
        self.global_vars_mutext = global_vars_mutext
        self.stdout_mutext = stdout_mutext
        self.episode = episode
        self.torrentAPI = torrentAPI
        self.torrent = None
        self.torrent_hash = ""
        self.torrent_magnet = ""

    def run(self):
        self._update_epidode_start_status()

        if not self._search_torrent():
            return
        if not self._add_download():
            return

        self._wait_for_torrent_to_start()

        self._mointor_torrent()

        self._remove_torrent()

        self._update_epidode_done_status()

    def join(self):
        self.episode.save()
        Thread.join(self)

    def _search_torrent(self):
        global total_process
        tpb = TPB()
        search_string = re.sub(r'[\"()\d]',
                               '', self.episode.serie.name)
        search_string += "S{:02d}".format(self.episode.season_number)
        search_string += "E{:02d}".format(self.episode.number)

        if tpb.search(search_string, 208) <= 0:
            with self.global_vars_mutext:
                total_process += 100
            with self.stdout_mutext:
                print(f"\rNo result founded to '{search_string}' on The Pirate Bay!", file=sys.stderr)
            return False
        
        self.torrent_magnet = tpb.get_torrent_magent_link()
        self.torrent_hash = tpb.get_torrent_hash()
        return True

    def _add_download(self):
        global total_process
        self.utorrent_mutex.acquire()
        if not self.torrentAPI.add_url(self.torrent_magnet):
            self.utorrent_mutex.release()
            with self.global_vars_mutext:
                total_process += 100
            with self.stdout_mutext:
                print("\rCan't add the torrent to the uTorrent download list",
                    file=sys.stderr)
            return False

        torrent_list = self.torrentAPI.get_list()
        self.utorrent_mutex.release()

        for torrent in torrent_list:
            if torrent.hash.upper() == self.torrent_hash.upper():
                self.torrent = torrent
                return True
        print("\rCan't find the torrent in the uTorrent download list", file=sys.stderr)
        return False

    def _wait_for_torrent_to_start(self):
        while self.torrent.size <= 0:
            with self.utorrent_mutex:
                self.torrent.refresh()
            time.sleep(2)

    def _mointor_torrent(self):
        global total_process
        with self.global_vars_mutext:
            total_process += self.torrent.progress

        last_progress_value = self.torrent.progress

        while (self.torrent.progress < 100):

            with self.utorrent_mutex:
                self.torrent.refresh()
            
            with self.global_vars_mutext:
                total_process += (self.torrent.progress - last_progress_value)

            last_progress_value = self.torrent.progress
            time.sleep(1)

    def _remove_torrent(self):
        self.utorrent_mutex.acquire()
        while (not self.torrent.remove()):
            self.utorrent_mutex.release()
            time.sleep(2)
            self.utorrent_mutex.acquire()
        self.utorrent_mutex.release()

    def _update_epidode_done_status(self):
        self.episode.status = Episode.STATUS_DONE
        self.episode.magnet_link = self.torrent_magnet
        self.episode.download_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _update_epidode_start_status(self):
        self.episode.status = Episode.STATUS_FAIL

    def _move_file(self):
        for root, dirs, files in os.walk(self.torrent.availability):
            for file in files:
                if file.endswith(('.mkv', '.avi')):
                    os.rename(os.path.realpath(file),)
        
class Episode_FileManager(Thread):
    def __init__(self,episode,):
        Thread.__init__(self)
