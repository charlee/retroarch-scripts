"""Generate thumbnails for MAME playlist."""

import re
import os
import json
import argparse
import requests
from common import abspath, download_file


def download_thumbnails(playlist):
    playlist_content = json.loads(open(playlist).read())
    games = playlist_content['items']

    playlist_name = os.path.basename(playlist).rsplit('.', 1)[0]
    playlist_dir = os.path.join(
        os.path.dirname(os.path.dirname(playlist)),
        'thumbnails',
        playlist_name,
    )
    os.makedirs(playlist_dir, exist_ok=True)

    for dirname in ('Named_Boxarts', 'Named_Snaps', 'Named_Titles'):
        print('Downloading %s.....' % dirname)
        dirpath = os.path.join(playlist_dir, dirname)
        os.makedirs(dirpath, exist_ok=True)

        for game in games:
            game_name = re.sub(r'[&*/:`<>?|\\]', '_', game['label'])
            filename = os.path.join(dirpath, '%s.png' % game_name)
            if not os.path.exists(filename):
                url = 'http://thumbnails.libretro.com/MAME/%s/%s.png' % (dirname, game_name)
                download_file(url, filename)
                print(filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--playlist', type=str, nargs=1, required=True, help='Playlist file.')
    args = parser.parse_args()

    download_thumbnails(args.playlist[0])