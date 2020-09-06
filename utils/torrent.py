import requests
import sys
import time
import urllib.parse
from lxml import html

class TorrentAPI():
    
    def __init__(self, base_url, username, password):
        if not base_url or not isinstance(base_url, str):
            raise AttributeError("Invalid attribute parsed to base_url")
        if not username or not isinstance(username, str):
            raise AttributeError("Invalid attribute parsed to username")
        if not password or not isinstance(password, str):
            raise AttributeError("Invalid attribute parsed to password")

        self.base_url = base_url
        self.username = username
        self.password = password
        self.auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        self.token, self.cookies = self._get_access_token()
        self.torrent_list = []

    def _get_access_token(self):
        url = self.base_url + '/token.html'
        token = ""
        cookies = ""

        try:
            response = requests.get(url, auth=self.auth)
            if response.status_code == 200:
                xtree = html.fromstring(response.content)
                token = xtree.xpath('//*[@id="token"]/text()')[0]
                guid = response.cookies['GUID']
                cookies = dict(GUID=guid)
            else:
                raise RuntimeError("Cant't get the token from uTorrent:\n\t HTTP error code %d"%response.status_code)
        except requests.ConnectionError as error:
            raise RuntimeError(
                F"Error while connecting to uTorrent API: \n\t{error}\nCheck if the uTorrent is started and the uri and access data are corret!")
        except BaseException as error:
            raise Exception(
                f"Unexpected error while connecting to uTorrent API\n\t{error}")

        return token, cookies

    def _request(self, params):

        if (len(params.keys()) <= 0):
            raise ValueError("Invalid params given!")

        params["token"] = self.token
        params["t"] = int(round(time.time() * 1000))

        params_query = urllib.parse.urlencode(params)
        url = f"{self.base_url}/?{params_query}"
        headers = {
            'Content-Type': "application/json"
        }
        try:
            response = requests.get(
                url, auth=self.auth, cookies=self.cookies, headers=headers)
            response.encoding = 'utf8'
            return response
        except requests.ConnectionError as error:
            raise RuntimeError(f"Error while connecting to uTorrent API:\n\t{error}")
        except BaseException as error:
            raise Exception(
                f"Unexpected error while connecting to uTorrent API\n\t{error}")
        return None

    def get_list(self):
        response = self._request({"list":1})
        if response != None and response.status_code == 200:
            self.torrent_list = TorrentList(response.json(), self)
            return TorrentList(response.json(),self)

        return []

    def add_url(self, magnet_link):

        response = self._request({"action": "add-url", "s": magnet_link})
        if response != None and response.status_code == 200:
            return True

        return False

    def action(self, torrent, action):

        if not isinstance(torrent, Torrent):
            raise AttributeError("Invalid attribute parsed to torrent")
        elif len(torrent.hash) <= 0:
            raise AttributeError("Torrent attribute have no valid hash")
        elif action not in TorrentAction.get_list():
            raise AttributeError("Invalid attribute parsed to action")

        response = self._request(
            {"action": action, "hash": torrent.hash})
        if response != None and response.status_code == 200:
            return True

        return False

    def is_authenticated(self):
        if len(self.token) <= 0 or len(self.cookies) <= 0:
            return False
        return True

class Torrent():

    def __init__(self, json, torrentApi):
        self.hash = json[0]
        self.status = Status(json[1])
        self.name = json[2]
        self.size = json[3]
        self.progress = json[4]/10
        self.downloaded = json[5]
        self.uploaded = json[6]
        self.ratio = json[7]
        self.upload_speed = json[8]
        self.download_speed = json[9]
        self.eta = json[10]
        self.lable = json[11]
        self.peers_connected = json[12]
        self.peers_swarm = json[13]
        self.seeds_connected = json[14]
        self.seeds_in_swarm = json[15]
        self.availability = json[16]
        self.queue_order = json[17]
        self.remaining = json[18]
        self.download_folder = json[26]

    def __str__(self):
        return f"{self.name} - {self.progress}%"

class TorrentAction():
    START = 'start'
    STOP = 'stop'
    PAUSE = 'pause'
    UNPAUSE = 'unpause'
    FORCE_START = 'forcestart'
    RECHECK = 'recheck'
    REMOVE = 'remove'
    REMOVE_ALL = 'removeda'
    QUEUE_BOTTOM = 'queuebottom'
    QUEUE_DOWN = 'queuedown'
    QUEUE_STOP = 'queuetop'
    QUEUE_UP = 'queueup'

    @staticmethod
    def get_list():
        return [TorrentAction.START, TorrentAction.STOP, TorrentAction.PAUSE, TorrentAction.UNPAUSE, TorrentAction.FORCE_START, TorrentAction.RECHECK, TorrentAction.REMOVE, TorrentAction.REMOVE_ALL, TorrentAction.QUEUE_BOTTOM, TorrentAction.QUEUE_DOWN, TorrentAction.QUEUE_STOP, TorrentAction.QUEUE_UP]

class TorrentList(object):
    def __init__(self, json, torrentApi):
        self.build = json['build']
        self.labels = [Label(x) for x in json['label']]
        self.torrents = [Torrent(x,torrentApi) for x in json['torrents']]
        self.torrent_cache_id = json['torrentc']
        self.index = -1

    def __iter__(self):
        return iter(self.torrents)

    def __next__(self):
        return next(self.torrents)

class Label:
    def __init__(self, json):
        self.label = json[0]
        self.torrents_in_label = json[1]

class Status:

    STARTED = "Started"
    CHECKING = "Checking"
    START_AFTER_CHECK = "Start after check"
    CHECKED = "Checked"
    ERROR = "Error"
    PAUSED = "Paused"
    QUEUED = "Queued"
    LOADED = "Loaded"

    def __init__(self,code):
        self.code = code
        self.status_list = list()

        status_list = [Status.STARTED, Status.CHECKING, Status.START_AFTER_CHECK,
                    Status.CHECKED , Status.ERROR , Status.PAUSED , Status.QUEUED , Status.LOADED]

        for i in range(0, 8):
            mask = 1 << i
            if (code & mask) != 0:
                self.status_list.append(status_list[i])

    def __str__(self):
        return ' , '.join( s for s in self.status_list)

    def are(self, status):
        return status in self.status_list
