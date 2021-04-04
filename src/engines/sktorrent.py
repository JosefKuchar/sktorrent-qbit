# VERSION: 1.7
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
import re
from urllib.parse import unquote
from bs4 import BeautifulSoup
import urllib.parse as urlparse
from urllib.parse import parse_qs

class sktorrent(object):
    url = 'http://sktorrent.eu/'
    name = 'SkTorrent'
    supported_categories = {'all': '0', 'movies': '6', 'tv': '4',
                            'music': '1', 'games': '2', 'anime': '7', 'software': '3'}

    def __init__(self):
        # Load config
        config = configparser.RawConfigParser()
        path = os.path.dirname(os.path.abspath(__file__)) + '/sktorrent.txt'

        if os.path.isfile(path):
            config.read(path)
        else:
            file = open(path, 'w')
            file.write(
                '[LOGIN]\nusername = YourUsername\npassword = YourPassword')
            file.close()
            exit()

        login = {
            'uid': config['LOGIN']['username'],
            'pwd': config['LOGIN']['password']
        }

        # Create cookie requests session
        self.session = requests.Session()

        # Login
        self.session.post(
            'http://sktorrent.eu/torrent/login.php', data=login)

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
        response = self.session.get(
            'http://sktorrent.eu/torrent/torrents_v2.php?search={}'.format(what))

        soup = BeautifulSoup(response.text, 'lxml')

        torrents = soup.findAll('img', {'class': 'lozad'})

        for torrent in torrents:
            details = {}

            t = torrent.parent
            info = torrent.find_parent('div').getText().splitlines()

            details['desc_link'] = 'http://sktorrent.eu/torrent/' + t['href']
            details['name'] = t.getText().strip()

            parsed = urlparse.urlparse(t['href'])

            id = parse_qs(parsed.query)['id'][0]

            details['link'] = 'http://sktorrent.eu/torrent/download.php?id=' + \
                id + '&f=file.torrent'

            size = re.search(r'^\w+ ([\w. ]+)\|', info[-4])
            details['size'] = size[1].strip()

            details['seeds'] = re.search(r'\d+', info[-3])[0]
            details['leech'] = re.search(r'\d+', info[-2])[0]
            details['engine_url'] = 'http://sktorrent.eu/'

            prettyPrinter(details)
