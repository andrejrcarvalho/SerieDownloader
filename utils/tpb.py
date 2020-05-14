import requests
import sys, re
from lxml import html

class TPB():
    """The Pirate Bay Seach Class\n
    With this class you can search by torrent a get their magnet link and their hash
    """

    #https://thepiratebay0.org/search/DCs%20Legends%20of%20Tomorrow%20S05E08/1/99/208
    #//*[@id="main-content"]/table/tr/td[position()=2]/a[position()=1]/@href'
    def __init__(self):
        self.search_uri = "https://thepiratebay0.org/search/"
        self.magnet_link = []

    def search(self, string, cat):
        """Search by string and fetch results

        Arguments:
            string {str} -- Keyword to search for
            cat {int} -- Categorie number

        Returns:
            list -- List of magent links founded
        """

        self.magnet_link.clear()
        string = string.replace("'",'')
        try:
            response = requests.get(f"{self.search_uri}{string}/1/99/{cat}")
            if (response.status_code == 200):
                xtree = html.fromstring(response.content)
                self.magnet_link = xtree.xpath('//*[@id="main-content"]/table/tr/td[position()=2]/a[position()=1]/@href')
                return len(self.magnet_link)
            else:
                print(f"Request error (status code = {response.status_code})",file=sys.stderr)
        except requests.ConnectionError as error:
            print(error, file=sys.stderr)
        except Exception as error:
            print(f"Unexpected error while making a request\n\t{error}", file=sys.stderr)
        return 0

    def get_torrent_magent_link(self, pos=0):
        """Get a magnet link from the buffer

        Keyword Arguments:
            pos {int} -- index of the magnet link (default: {0})

        Returns:
            str -- the magnet link
        """

        if (len(self.magnet_link) > 0):
            return self.magnet_link[pos]
        return ""

    def get_torrent_hash(self, pos=0):
        """Get a hash from the buffer

        Keyword Arguments:
            pos {int} -- index of the magnet link (default: {0})

        Returns:
            str -- the hash of the magent link
        """
        if (len(self.magnet_link) > 0):
            info_hash = re.search(
                '(btih:)(\w+)', self.magnet_link[pos])[2]
            return info_hash
        return ""

