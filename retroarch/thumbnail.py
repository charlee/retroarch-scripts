import os
import re
import requests

class Thumbnail:

    def __init__(self, root, playlist_name):
        if playlist_name.endswith('.lpl'):
            playlist_name = playlist_name[:-4]

        self.root = root
        self.playlist_name = playlist_name
    
    def download(self, game_label):
        for dirname in ('Named_Boxarts', 'Named_Snaps', 'Named_Titles'):
            path = os.path.join(self.root, 'thumbnails', self.playlist_name, dirname)
            os.makedirs(path, exist_ok=True)

            game_name = re.sub(r'[&*/:`<>?|\\]', '_', game_label)
            filename = os.path.join(path, '%s.png' % game_name)

            if not os.path.exists(filename):
                print('Downloading %s for "%s".....' % (dirname, game_label))

                url = 'http://thumbnails.libretro.com/MAME/%s/%s.png' % (dirname, game_name)

                r = requests.get(url)
                if r.status_code != 200:
                    print('Error: request %s returned %s' % (url, r.status_code))
                    return
                open(filename, 'wb').write(r.content)