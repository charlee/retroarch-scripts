import os
import json

from .common import abspath
from .thumbnail import Thumbnail

class Playlist:

    def __init__(self, root, name):
        self.root = abspath(root)
        self.name = name
        self.path = os.path.join(self.root, 'playlists', name)

        if os.path.exists(self.path):
            with open(self.path) as f:
                self.playlist = json.loads(f.read())
        else:
            self.playlist = {
                'version': '1.0',
                'items': [],
            }

    def reset(self):
        self.playlist['items'] = []

    def add_entry(self, path, label, core_path):
        self.playlist['items'].append({
            'path': path,
            'label': label,
            'core_path': core_path,
            'core_name': 'DETECT',
            'crc32': 'DETECT',
            'db_name': self.name,
        })

    def save(self):
        with open(self.path, 'w') as f:
            f.write(json.dumps(self.playlist, indent=2))
    
    def download_thumbnails(self):
        for game in self.playlist['items']:
            Thumbnail(self.root, self.name).download(game['label'])