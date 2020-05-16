from utils import Database
from datetime import datetime
import models

class Serie:

    STATUS_ENABLE = "ENABLE"
    STATUS_DISABLE = "DISABLE"

    def __init__(self, id="", name="", number_seasons=0, status=STATUS_DISABLE):
        self.id = id
        self.name = name
        self.number_seasons = number_seasons
        self.status = status
        self.seasons = list()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, str):
            raise ValueError("Invalid given value Episode<id>")
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Invalid given value Episode<name>")
        self._name = value.replace('"','')

    @property
    def number_seasons(self):
        return self._number_seasons

    @number_seasons.setter
    def number_seasons(self, value):
        if value < 0:
            raise ValueError("Invalid given value Episode<number_seasons>")
        self._number_seasons = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in (Serie.STATUS_ENABLE,Serie.STATUS_DISABLE):
            raise ValueError("Invalid given value Episode<status>")
        self._status = value


    def loadSeasons(self,status=[]):
        self.seasons = [list()] * self.number_seasons

        result = models.Episode.getList(status=status, serie_id=self.id)
        for episode in result:
            if len(self.seasons[episode.season_number - 1]) == 0:
                self.seasons[episode.season_number - 1] = []
            self.seasons[episode.season_number - 1].append(episode)

    def save(self):
        update = Serie.get(self.id)
        d = Database.getInstance()

        if update == None:
            d.execute(
                f"INSERT INTO serie (imdb_id, name, number_seasons, create_date, status) VALUES (?,?,?,?,?)",
                (self.id, self.name, self.number_seasons, datetime.now(), self.status))
        else:
            d.execute(
                f"UPDATE serie SET name = ?, number_seasons = ?, update_date = ?, status = ? WHERE imdb_id = ?",
                (self.name, self.number_seasons, datetime.now(), self.status, self.id))

    @staticmethod
    def get(imdb_id):
        d = Database.getInstance()
        l = d.get_row(
            f"SELECT imdb_id, name, number_seasons, status FROM serie WHERE imdb_id={imdb_id}")
        if l == None:
            return None
        s = Serie(l[0], l[1], l[2], l[3])
        return s

    @staticmethod
    def getList():
        #TODO Adicionar condição para importar apenas series enabled
        d = Database.getInstance()
        l = d.get_rows("SELECT imdb_id, name, number_seasons, status FROM serie")
        result = []
        for e in l:
            s = Serie(e[0],e[1],e[2],e[3])
            result.append(s)
        return result

    def __str__(self):
        return f"{self.name} ({self.number_seasons} seasons) STATUS={self.status}"