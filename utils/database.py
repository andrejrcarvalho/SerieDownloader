import sqlite3, sys
from os import path

class Database:
    __instance = None
    @staticmethod
    def getInstance():
        if Database.__instance == None:
            raise Exception("Object not inicialised")
        return Database.__instance

    def __init__(self, file_path):
        if Database.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Database.__instance = self
            try:
                self.conn = sqlite3.connect(file_path)
                self.cursor = self.conn.cursor()
                self._create_db()
            except sqlite3.Error as error:
                print(f"Database error:\n\t{error}",file=sys.stderr)
            except :
                self._show_errors()

    def execute(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.Error as error:
            print(f"Database error:\n\t{error}")
        except:
            self._show_errors()
        finally:
            return False

    def get_row(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchone()
        except sqlite3.Error as error:
            print(f"Database error:\n\t{error}")
        except:
            self._show_errors()
        return None

    def get_rows(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as error:
            print(f"Database error:\n\t{error}")
        except Exception as error:
            self._show_errors()
        return []

    def close(self):
        self.conn.close()

    def _create_db(self):
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS serie (
                    imdb_id TEXT PRIMARY KEY, 
                    name TEXT,
                    number_seasons INTEGER,
                    create_date DATETIME,
                    update_date DATETIME,
                    status TEXT
                );
                ''')
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS episode (
                    imdb_id TEXT PRIMARY KEY, 
                    name TEXT,
                    number INTEGER,
                    season_number INTEGER,
                    serie_id TEXT,
                    release_date DATETIME,
                    download_date DATETIME,
                    magnet_link TEXT,
                    status TEXT,
                    FOREIGN KEY(serie_id) REFERENCES serie(imdb_id)
                );
                ''')

    def _show_errors(self):
        print(
            f"Unexpected error while making a request:", file=sys.stderr)
        for error in sys.exc_info():
            print(f"\t{error}", file=sys.stderr)
