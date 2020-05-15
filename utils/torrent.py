import requests
import sys
import time
import urllib.parse
from lxml import html

class TorrentAPI(object):
    
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        self.token, self.cookies = self._get_access_token()

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
        except requests.ConnectionError as error:
            print(
                F"Error while connecting to uTorrent API:\n\t{error}\nCheck if the uTorrent is started and the uri and access data are corret!", file=sys.stderr)
        except:
            self._show_errors()

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
            print(
                F"Error while connecting to uTorrent API:\n\t{error}", file=sys.stderr)
        except:
            self._show_errors()
        return None

    def get_list(self):
        response = self._request({"list":1})
        if response != None and response.status_code == 200:
            return TorrentList(response.json(),self)

        return []

    def add_url(self, magnet_link):

        response = self._request({"action": "add-url", "s": magnet_link})
        if response != None and response.status_code == 200:
            return True

        return False

    def is_authenticated(self):
        if len(self.token) <= 0 or len(self.cookies) <= 0:
            return False
        return True

    def _show_errors(self):
        print(
            f"Unexpected error while getting IMDB data:", file=sys.stderr)
        for error in sys.exc_info():
            print(f"\t{error}", file=sys.stderr)

class Torrent(TorrentAPI):

    def __init__(self, json,torrentApi):
        super().__init__(torrentApi.base_url, torrentApi.username, torrentApi.password)
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

    def start(self):
        return self._action('start')

    def stop(self):
        return self._action('stop')

    def pause(self):
        return self._action('pause')

    def unpause(self):
        return self._action('unpause')

    def forcestart(self):
        return self._action('forcestart')

    def recheck(self):
        return self._action('recheck')

    def remove(self):
        return self._action('remove')

    def removeda(self):
        return self._action('removeda')

    def queuebottom(self):
        return self._action('queuebottom')

    def queuedown(self):
        return self._action('queuedown')

    def queuetop(self):
        return self._action('queuetop')

    def queueup(self):
        return self._action('queueup')

    def get_files(self):
        response = self._request({"action": "getfiles", "hash": self.hash})
        if response != None and response.status_code == 200:
            data = response.json()
            if "files" not in data:
                return []
            return data["files"][1]
        return False

    def refresh(self):
        torrentlist = self.get_list()
        for torrent in torrentlist:
            if (torrent.hash == self.hash):
                self.__dict__ = torrent.__dict__
        
    def _action(self, action):
        response = self._request({"action":action,"hash":self.hash})
        if response != None and response.status_code == 200:
            return True
        return False

    def __str__(self):
        return f"{self.name} - {self.progress}%"

class TorrentList(object):
    def __init__(self, json, torrentApi):
        self.build = json['build']
        self.labels = [Label(x) for x in json['label']]
        self.torrents = [Torrent(x, torrentApi) for x in json['torrents']]
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