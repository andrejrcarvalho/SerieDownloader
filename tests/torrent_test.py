import unittest

from utils.torrent import TorrentAPI

class Test_TorrentTest(unittest.TestCase):

    def test_connection(self):
        with self.assertRaises(AttributeError):
            TorrentAPI("", "test", "test")
        with self.assertRaises(AttributeError):
            TorrentAPI("127.0.0.1", "", "test")
        with self.assertRaises(AttributeError):
            TorrentAPI("127.0.0.1", "test", "")
        with self.assertRaises(AttributeError):
            TorrentAPI(61656, "test", "")
        with self.assertRaises(AttributeError):
            TorrentAPI("127.0.0.1", 684651, "")
        with self.assertRaises(AttributeError):
            TorrentAPI("127.0.0.1", "test", 9179)

    def test_get_list(self):
        t = TorrentAPI("127.0.0.1", "test", "test")
        self.assertIsInstance(t.get_list(), list)
