from utils.models import Episode, Serie
import utils.cmd_gui as gui
from datetime import datetime
from utils.torrent import TorrentAPI, Status, TorrentAction
from utils.tpb import TPB
from utils.settings import Settings
import re
import time
import sys
import os
import pathlib
import shutil
from threading import Thread, Lock

total_process = 0


def main():
    threads_list = list()
    global_vars_mutext = Lock()
    stdout_mutext = Lock()

    uTorrent = TorrentAPI(
        Settings.getInstance().utorrent_gui_url,
        Settings.getInstance().utorrent_gui_user,
        Settings.getInstance().utorrent_gui_password)

    if not uTorrent.is_authenticated():
        print("Can't connect to torrent gui")
        gui.pause()
        return

    uTorrentThread = UTorrentThread(uTorrent)

    global total_process
    total_process = 0

    for e in Episode.getList([Episode.STATUS_PENDING, Episode.STATUS_FAIL]):
        if (e.serie.status == Serie.STATUS_ENABLE and e.release_date <= datetime.now()):
            thread = Episode_Downloader(
                e, uTorrentThread, global_vars_mutext, stdout_mutext)
            threads_list.append(thread)
            thread.start()
    
    while check_thread_live(threads_list):
        p = total_process / len(threads_list)
        with stdout_mutext:
            gui.progress("Downloading..", p, "{:.2f}%".format(p))

    for thread in threads_list:
        thread.join()

    uTorrentThread.join()

    print("\nALL DOWNLOADS DONE")
    gui.pause()

def check_thread_live(thread_list):
    for t in thread_list:
        if t.isAlive():
            return True
    return False


class UTorrentThread(Thread):

    REQUEST_ADD_URL = 1
    REQUEST_ACTION = 2

    def __init__(self, api):
        Thread.__init__(self)
        self.name = "UTorrentAPI"
        self.request_queue = []
        self.request_counter = 0
        self.request_responce = []
        self.api = api
        self.torrentList = []
        self.exit = False
        Thread.start(self)

    def run(self):
        while not self.exit:
            self.torrentList = self.api.get_list()
            time.sleep(1)
            while len(self.request_queue) > 0:
                r = self.request_queue.pop(0)
                responce = None
                if (r["type"] == UTorrentThread.REQUEST_ADD_URL):
                    responce = self.api.add_url(r["url"])
                elif (r["type"] == UTorrentThread.REQUEST_ACTION):
                    responce = self.api.action(r["torrent"], r["action"])
                
                self.request_responce.append(
                    {"id": r["id"], "responce": responce})
                time.sleep(1)

    def addRequest(self, request):
        request["id"] = self.request_counter
        self.request_counter = self.request_counter + 1
        self.request_queue.append(request)
        return request["id"]

    def getRequestResponce(self, request_id):
        while 1:
            for r in self.request_responce:
                if (r["id"] == request_id):
                    responce = r["responce"]
                    self.request_responce.remove(r)
                    return responce

    def getTorrentList(self):
        return self.torrentList

    def getTorrent(self, torrent_hash):
        torrent_list = self.getTorrentList()
        for torrent in torrent_list:
            if torrent.hash.upper() == torrent_hash.upper():
                return torrent

    def join(self):
        self.exit = True
        Thread.join(self)


class Episode_Downloader(Thread):

    def __init__(self, episode, uTorrentThread, global_vars_mutext, stdout_mutext):
        Thread.__init__(self)
        self.name = f"{episode.serie.name} - {episode.name}"
        self.global_vars_mutext = global_vars_mutext
        self.stdout_mutext = stdout_mutext
        self.episode = episode
        self.uTorrentThread = uTorrentThread
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

        self._move_file()

    def join(self):
        self.episode.save()
        Thread.join(self)

    def _search_torrent(self):
        global total_process
        tpb = TPB()
        search_string = re.sub(r'\(\d{4}\)',
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

        request_number = self.uTorrentThread.addRequest(
            {"type": UTorrentThread.REQUEST_ADD_URL, "url": self.torrent_magnet})

        if not self.uTorrentThread.getRequestResponce(request_number):
            with self.global_vars_mutext:
                total_process += 100
            with self.stdout_mutext:
                print("\r[%s]Can't add the torrent to the uTorrent download list"%(self.name),
                    file=sys.stderr)
            return False

        while not self.torrent:
            self.torrent = self.uTorrentThread.getTorrent(
                self.torrent_hash)
        return True

    def _wait_for_torrent_to_start(self):
        while self.torrent.size <= 0:
            self.torrent = self.uTorrentThread.getTorrent(self.torrent.hash)
            time.sleep(2)

    def _mointor_torrent(self):
        global total_process
        with self.global_vars_mutext:
            total_process += self.torrent.progress

        last_progress_value = self.torrent.progress

        while (self.torrent.progress < 100):
            self.torrent = self.uTorrentThread.getTorrent(self.torrent.hash)
            
            with self.global_vars_mutext:
                total_process += (self.torrent.progress - last_progress_value)

            last_progress_value = self.torrent.progress
            time.sleep(1)

    def _remove_torrent(self):
        request_number = self.uTorrentThread.addRequest(
            {"type": UTorrentThread.REQUEST_ACTION, "action": TorrentAction.REMOVE, "torrent": self.torrent})
        if not self.uTorrentThread.getRequestResponce(request_number):
            with self.stdout_mutext:
                print("\rCan't add the torrent to the uTorrent download list",
                      file=sys.stderr)
    
    def _update_epidode_done_status(self):
        self.episode.status = Episode.STATUS_DONE
        self.episode.magnet_link = self.torrent_magnet
        self.episode.download_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _update_epidode_start_status(self):
        self.episode.status = Episode.STATUS_FAIL

    def _move_file(self):
        season_name = "Season {:02d}".format(self.episode.season_number)
        folder = os.path.join(
            Settings.getInstance().download_folder,
            self.episode.serie.name,
            season_name
            )
        
        if not os.path.isdir(folder):
            pathlib.Path(
                folder).mkdir(parents=True, exist_ok=True)

        for root, dirs, files in os.walk(self.torrent.download_folder):
            for file in files:
                if file.endswith(('.mkv', '.avi')):
                    filename, file_extension = os.path.splitext(file)
                    filename = "S{:02d}E{:02d} - {:s}{:s}".format(
                        self.episode.season_number,
                        self.episode.number,
                        self.episode.name,
                        file_extension)
                    os.rename(os.path.join(root, file),
                              os.path.join(folder, filename))
                    shutil.rmtree(self.torrent.download_folder)
                    return
        
