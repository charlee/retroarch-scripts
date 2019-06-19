import os
import binascii
import pickle
import zipfile
import requests
import urllib.parse
from io import BytesIO
from .dat import DatFile
from .bundle_dir import BundleDir


CORE_INFO = {
    'mame2010_libretro': {
        'name': 'mame2010',
        'datfile': 'MAME v0.139 (xml).zip',
        'unzipped_datfile': 'MAME v0.139.dat',
        'dbfile': 'mame2010.pkl',
    }
}

def abspath(path):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


class MAME:

    def __init__(self, root):
        self.root = abspath(root)
        self.mamedb_path = abspath('~/.retroarch-scripts/mamedb')
        self.mamedbs = {}

    def cores(self):
        cores_dir = os.path.join(self.root, 'cores')
        cores = []
        for _, _, filelist in os.walk(cores_dir):
            for fname in filelist:
                if not fname.startswith('mame'):
                    continue

                core_name = fname.rsplit('.', 1)[0]
                core_info = CORE_INFO.get(core_name)
                if core_info:
                    cores.append(core_info)

        return cores

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

        datfile = DatFile()
        mamedb = datfile.parse(content)

        with open(dbfile, 'wb') as dbf:
            pickle.dump(mamedb, dbf)

    def ensure_mamedbs(self):
        for core in self.cores():
            db = self.download_mamedb(core)
            self.mamedbs[core['name']] = db

    def fix_bundles(self, romdir):
        bundle_dir = BundleDir(romdir)
        bundle_dir.load_bundles()

        for dirname, _, filelist in os.walk(romdir):
            for fname in filelist:
                if not fname.endswith('.zip'):
                    continue

                bundle_file = os.path.join(dirname, fname)

                zf = zipfile.ZipFile(bundle_file)
                namelist = zf.namelist()
                if 'version.json' in namelist:
                    print('%s is already fixed, skip...')
                    continue

                # TODO: scan roms

                print('Checking %s...' % fname)

                for mamedb in self.mamedbs.values():
                    game = mamedb.get_game(fname)
                    bundle = bundle_dir.get_bundle_by_path(bundle_file)
                    for rom in game.roms:
                        if bundle.get_rom_by_crc(rom.crc):
                            print('  - %s found' % rom.name)
                        elif bundle_dir.get_rom_by_crc(rom.crc):
                            print('  - %s found in other files' % rom.name)
                        else:
                            print('  - %s: %s missing' % (rom.name, rom.crc))

