import json
import os.path, sys

class Settings():
    __instance = None
    def __init__(self, path):
        if Settings.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Settings.__instance = self
            self.path = path
            self._init_default_values()
            try:
                self._load_values_from_file()
            except FileNotFoundError:
                print("Configuration file not founded, runnig on the defaut settings")
                self._create_config_file()
            finally:
                self.utorrent_gui_url = f"http://{self.utorrent_gui_addr}:{self.utorrent_gui_port}/gui"
    
    def _init_default_values(self,):
        self.config_file = f"{self.path}/default.conf"
        self.download_folder = os.path.join(self.path, "series")
        self.database_file = os.path.join(self.path, "database.sqlite3")
        self.utorrent_gui_addr = "127.0.0.1"
        self.utorrent_gui_port = "8080"
        self.utorrent_gui_user = "admin"
        self.utorrent_gui_password = "admin"
        
    def _load_values_from_file(self):
        with open(self.config_file) as json_file:
            data = json.load(json_file)
            if "download_folder" in data.keys() and os.path.isdir(data["download_folder"]):
                self.download_folder = data["download_folder"]
            if "database_file" in data.keys() and os.path.isfile(data["database_file"]):
                self.database_file = data["database_file"]
            if "torrent" in data.keys():
                if "address" in data["torrent"].keys():
                    self.utorrent_gui_addr = data["torrent"]["address"]
                if "port" in data["torrent"].keys():
                    self.utorrent_gui_port = data["torrent"]["port"]
                if "user" in data["torrent"].keys():
                    self.utorrent_gui_user = data["torrent"]["user"]
                if "password" in data["torrent"].keys():
                    self.utorrent_gui_password = data["torrent"]["password"]
    
    def _create_config_file(self):
        with open(self.config_file, 'a') as outfile:
            data = {
                "download_folder": self.download_folder,
                "database_file": self.database_file,
                "torrent": {
                    "address": self.utorrent_gui_addr,
                    "port": self.utorrent_gui_port,
                    "user": self.utorrent_gui_user,
                    "password": self.utorrent_gui_password
                }
            }
            json.dump(data, outfile, indent=4)
            if not os.path.isdir(self.download_folder):
                os.mkdir(self.download_folder)

    @staticmethod
    def getInstance():
        if Settings.__instance == None:
            raise Exception("Object not inicialised")
        return Settings.__instance
  
