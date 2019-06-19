import os
import json
import binascii
import pickle
import zipfile
import requests
import urllib.parse
from io import BytesIO
from .mamedb import parse_datfile
from .bundle_dir import BundleSet


CORE_INFO = {
    'mame2010_libretro': {
        'name': 'mame2010_libretro',
        'datfile': 'MAME v0.139 (xml).zip',
        'unzipped_datfile': 'MAME v0.139.dat',
        'dbfile': 'mame2010.pkl',
    },

    'mame2003_libretro': {
        'name': 'mame2003_libretro',
        'datfile': 'MAME v0.78 (cm).zip',
        'unzipped_datfile': 'MAME v0.78.dat',
        'dbfile': 'mame2003.pkl',
    }
}

def abspath(path):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


class MAME:

    def __init__(self, root):
        self.root = abspath(root)
        self.mamedb_path = abspath('~/.retroarch-scripts/mamedb')
        self.mamedbs = {}
        self.cores = []

        self.load_cores()
        self.ensure_mamedbs()

    def load_cores(self):
        cores_dir = os.path.join(self.root, 'cores')
        self.cores = []
        for dirname, _, filelist in os.walk(cores_dir):
            for fname in filelist:
                if not fname.startswith('mame'):
                    continue

                core_name = fname.rsplit('.', 1)[0]
                core_info = CORE_INFO.get(core_name)
                if core_info:
                    core_info['fullpath'] = abspath(os.path.join(dirname, fname))
                    self.cores.append(core_info)

    def download_mamedb(self, core_info):
        if not os.path.isdir(self.mamedb_path):
            os.makedirs(self.mamedb_path)
        
        dbfile = os.path.join(self.mamedb_path, core_info['dbfile'])
        if os.path.exists(dbfile):
            with open(dbfile, 'rb') as dbf:
                return pickle.load(dbf)

        # Download dat file and parse
        url = 'http://www.logiqx.com/Dats/MAMEBeta/' + urllib.parse.quote(core_info['datfile'])
        r = requests.get(url)
        if r.status_code != 200:
            print('Error: request %s returned %s' % (url, r.status_code))
            exit(1)

        zf = zipfile.ZipFile(BytesIO(r.content))
        with zf.open(core_info['unzipped_datfile']) as f:
            content = f.read().decode('utf-8')

        mamedb = parse_datfile(content)
        mamedb.core_name = core_info['name']

        with open(dbfile, 'wb') as dbf:
            pickle.dump(mamedb, dbf)

        return mamedb

    def ensure_mamedbs(self):
        for core in self.cores:
            db = self.download_mamedb(core)
            self.mamedbs[core['name']] = db

    def fix_bundles(self, romdir):
        bundle_set = BundleSet(romdir)

        for bundle in bundle_set.bundles:
            version = bundle.read_version()

            if version:
                print('%s is already fixed, skip...' % bundle.path)
                continue

            # TODO: scan roms

            print('Checking %s...' % bundle.path)

            for mamedb in self.mamedbs.values():
                game = mamedb.get_game(bundle.name)

                # Skip non-exist game
                if not game:
                    continue

                result = bundle.compare_with_db(game)

                if all(v == 'ok' for v in result.values()):
                    print('%s => version: %s'  % (bundle.path, mamedb.version))
                    bundle.write_version(mamedb.core_name, game.description)
                    break

                if all(v == 'ok' or v == 'other' for v in result.values()):
                    print('Fixing %s...' % bundle.path)
                    bundle.fix_bundle(game)
                    print('%s => version: %s'  % (bundle.path, mamedb.version))
                    bundle.write_version(mamedb.core_name, game.description)
                    break

    def make_playlist(self, romdir, playlist_name):
        bundle_set = BundleSet(romdir)
        cores_dir = os.path.join(self.root, 'cores')

        playlist_entries = []

        for bundle in bundle_set.bundles:
            version = bundle.read_version()

            # Skip if version.json does not exist
            if not version:
                continue 

            for core_info in self.cores:
                if core_info['name'] == version['core_name']:
                    entry = {
                        'path': abspath(bundle.path),
                        'label': version['description'],
                        'core_path': core_info['fullpath'],
                        'core_name': 'DETECT',
                        'crc32': 'DETECT',
                        'db_name': playlist_name,
                    }

                    playlist_entries.append(entry)
                    break

        playlist = {
            'version': '1.0',
            'items': playlist_entries,
        }

        playlist_file = os.path.join(self.root, 'playlists', playlist_name)
        open(playlist_file, 'w').write(json.dumps(playlist, indent=2))
        

