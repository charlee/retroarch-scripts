import os
import zipfile
import binascii
import json

from .common import get_game_name


class Bundle:

    def __init__(self, cache=None):
        self.roms = []
        self.cache = cache
        self.name = None

    def load_bundle(self, bundle_file):

        self.name = get_game_name(bundle_file)
        self.bundle_file = bundle_file

        try:
            fd = os.open(bundle_file, os.O_RDONLY)
            mtime = os.fstat(fd).st_mtime
            os.close(fd)

            if self.cache:
                cached = self.cache.get(self.name)
                if cached is not None and mtime <= cached['mtime']:
                    # Cache valid, load from cache
                    self.roms = cached['roms']
                    return self.roms

            zf = zipfile.ZipFile(bundle_file)
            for filename in zf.namelist():
                with zf.open(filename) as f:
                    crc = binascii.crc32(f.read())
                    crc = format(crc, '08x')

                    self.roms.append({
                        'filename': filename,
                        'crc': crc,
                    })
            
            if self.cache:
                # Store to cache
                self.cache[self.name] = {
                    'mtime': mtime,
                    'roms': self.roms,
                }

        except OSError:
            # If file not found or any error occured, clear cache
            if self.cache and self.cache[self.name]:
                del self.cache[self.name]

    def get_rom_by_crc(self, crc):
        for rom in self.roms:
            if rom['crc'] == crc:
                return rom

        return None

class BundleDir:

    def __init__(self, bundle_dir):
        self.bundle_dir = bundle_dir
        self.bundles = []
        self.cache = {}

    def load_bundles(self):
        cache_file = os.path.join(self.bundle_dir, '.bundlecache.json')
        if os.path.exists(cache_file):
            self.cache = json.loads(open(cache_file).read())

        bundle_map = {}
        crc_map = {}

        for dirname, _, filelist in os.walk(self.bundle_dir):
            for fname in filelist:
                if not fname.endswith('.zip'):
                    continue

                print('Scanning %s...' % os.path.join(dirname, fname))
                bundle = Bundle(self.cache)
                bundle.load_bundle(os.path.join(dirname, fname))

                self.bundles.append(bundle)

        # Build CRC map
        self.crc_map = {}
        for bundle in self.bundles:
            for rom in bundle.roms:
                self.crc_map[rom['crc']] = {
                    'filename': rom['filename'],
                    'bundle_name': bundle.name,
                }

        self.cache['_crc_map'] = self.crc_map

        open(cache_file, 'w').write(json.dumps(self.cache, indent=4))

    def get_bundle_by_path(self, path):
        for bundle in self.bundles:
            if bundle.bundle_file == path:
                return bundle

        return None

    def get_rom_by_crc(self, crc):
        return self.crc_map.get(crc)