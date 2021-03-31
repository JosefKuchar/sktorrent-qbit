# VERSION: 1.2
# AUTHORS: Josef Kuchař (josef@josefkuchar.com)

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter
from html.parser import HTMLParser
import requests
import tempfile
import os
import io
import gzip
import configparser
from urllib.parse import unquote
from bs4 import BeautifulSoup

class sktorrent(object):
    url = 'https://www.hd-cztorrent.cz/'
    name = 'SkTorrent'
    supported_categories = {'all': '0', 'movies': '6', 'tv': '4',
                            'music': '1', 'games': '2', 'anime': '7', 'software': '3'}

    def __init__(self):
        # Load config
        config = configparser.RawConfigParser()
        path = os.path.dirname(os.path.abspath(__file__)) + '/sktorrent.txt'

        print('asdfasfd')

        if os.path.isfile(path):
            config.read(path)
        else:
            file = open(path, 'w')
            file.write('[LOGIN]\nusername = YourUsername\npassword = YourPassword')
            file.close()
            exit()
        print(config['LOGIN']['password'])
        login = {
            'uid': config['LOGIN']['username'],
            'pwd': config['LOGIN']['password']
        }

        print(login)

        # Create cookie requests session
        self.session = requests.Session()

        # Login
        self.session.post(
            'http://sktorrent.eu/torrent/login.php', data=login)

        print('asdfasdf')

    def download_torrent(self, info):
        file, path = tempfile.mkstemp()
        file = os.fdopen(file, "wb")
        # Download url
        response = self.session.get(info)
        dat = response.content
        # Check if it is gzipped
        if dat[:2] == b'\x1f\x8b':
            # Data is gzip encoded, decode it
            compressedstream = io.BytesIO(dat)
            gzipper = gzip.GzipFile(fileobj=compressedstream)
            extracted_data = gzipper.read()
            dat = extracted_data

        # Write it to a file
        file.write(dat)
        file.close()
        # return file path
        print(path + " " + info)

    def search(self, what, cat='all'):
        print('asdfa')

        response = self.session.get(
            'http://sktorrent.eu/torrent/torrents_v2.php?search={}&category=0&zaner=&active=0'.format(what))

        soup = BeautifulSoup(response.text, 'html.parser')

        torrents = soup.findAll('img', {'class': 'lozad'})

        print(torrents[0].find_parent())
