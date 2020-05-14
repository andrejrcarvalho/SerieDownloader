from utils import Database
from datetime import datetime
import models

class Episode:

    STATUS_UNLISTED = "PASS"
    STATUS_PENDING = "PENDING"
    STATUS_UNDATED = "UNDATED"
    STATUS_FAIL = "FAIL"
    STATUS_DONE = "DONE"

    def __init__(self, id="", name="", number=1, season_number=0, release_date=None,
                 download_date=None, magnet_link="", serie=None, status=""):
        self.id = id
        self.name = name
        self.number = number
        self.season_number = season_number
        self.release_date = release_date
        self.download_date = download_date
        self.magnet_link = magnet_link
        self.serie = serie
        self.status = status

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
        self._name = value
    
    @property
    def number(self):
        return self._number
    
    @number.setter
    def number(self, value):
        if value < 0:
            raise ValueError("Invalid given value Episode<number>")
        self._number = value

    @property
    def season_number(self):
        return self._season_number
    
    @season_number.setter
    def season_number(self, value):
        if value < 0:
            raise ValueError("Invalid given value Episode<season_number>")
        self._season_number = value

    @property
    def release_date(self):
        return self._release_date
    
    @release_date.setter
    def release_date(self, value):
        if isinstance(value, datetime) or value == None:
            self._release_date = value
        elif isinstance(value, str) and len(value) > 0:
            self._release_date = datetime.strptime(
                value, "%Y-%m-%d %H:%M:%S")
        else:
            raise ValueError("Invalid given value Episode<release_date>")
            
    @property
    def download_date(self):
        return self._download_date

    @download_date.setter
    def download_date(self, value):
        if isinstance(value, datetime) or value == None:
            self._download_date = value
        elif isinstance(value, str) and len(value) > 0:
            self._download_date = datetime.strptime(
                value, "%Y-%m-%d %H:%M:%S")
        else:
            raise ValueError("Invalid given value Episode<download_date>")

    @property
    def magnet_link(self):
        return self._magnet_link
    
    @magnet_link.setter
    def magnet_link(self, value):
        self._magnet_link = value

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        if value not in [Episode.STATUS_DONE, Episode.STATUS_FAIL, Episode.STATUS_PENDING, Episode.STATUS_UNDATED, Episode.STATUS_UNLISTED]:
            raise ValueError("Invalid given value Episode<status>")
        self._status = value

    @property
    def serie(self):
        return self._serie
    
    @serie.setter
    def serie(self, value):
        if value == None or len(value) == 0:
            self._serie = None
        else:
            serie = models.Serie.get(value)
            if serie == None:
                self._serie = value
            else:
                self._serie = serie

    def save(self):
        update = Episode.get(self.id)
        d = Database.getInstance()

        serie_id = self.serie.id if isinstance(self.serie, models.Serie) else self.serie

        if update == None:
            d.execute(
                f"""INSERT INTO episode (imdb_id, name, number, season_number, magnet_link, 
                                        download_date, release_date, serie_id, status) VALUES (?,?,?,?,?,?,?,?,?)""",
                (self.id, self.name, self.number, self.season_number, self.magnet_link,
                 self.download_date, self.release_date, serie_id, self.status))
        else:
            d.execute(
                f"""UPDATE episode SET name = ?, number = ?, season_number = ?, magnet_link = ?,
                                    download_date = ?, release_date = ?, serie_id = ?, status = ? WHERE imdb_id = ?""",
                ( self.name, self.number, self.season_number, self.magnet_link,
                  self.download_date, self.release_date, serie_id, self.status, self.id))

    @staticmethod
    def get(imdb_id):
        d = Database.getInstance()
        l = d.get_row(
            f"""SELECT imdb_id, name, number, season_number, magnet_link,
            download_date, release_date, serie_id, status FROM episode WHERE imdb_id={imdb_id}""")
        if l == None:
            return None
        s = Episode(l[0],l[1],l[2],l[3],l[6],l[5],l[4],l[7],l[8])
        return s

    @staticmethod
    def getList(status=[], serie_id=''):
        result = list()
        query = "SELECT imdb_id, name, number, season_number, release_date, download_date, magnet_link, serie_id, status FROM episode"
        
        conditions = []
        if (len(status) > 0):
            string = "status in ("
            string += ','.join([f"'{elem}'" for elem in status])
            string += ')'
            conditions.append(string)
        if len(serie_id) > 0:
            string = f"serie_id = {serie_id}"
            conditions.append(string)

        if len(conditions) > 0:
            query += " WHERE "
            query += ' AND '.join([f"{elem}" for elem in conditions])

        d = Database.getInstance()
        r = d.get_rows(query)
        for e in r:
            release_date = e[4] if e[4] != None else None
            download_date = e[5] if e[5] != None else None
            episode = Episode(e[0], e[1], e[2], e[3], release_date, download_date, e[6], e[7], e[8])
            result.append(episode)
        return result

    def __str__(self):
        return f"{self.number} - {self.name}"

    def __repr__(self):
        return f"Episode({self.id}, {self.name}, {self.number})"

