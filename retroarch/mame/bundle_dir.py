import os
import zipfile
import binascii
import json


def get_game_name(path):
    filename = os.path.basename(path)
    if filename.endswith('.zip'):
        filename = filename[:-4]

    return filename

class Bundle:

    def __init__(self, bundle_set, path):
        """
        """
        self.bundle_set = bundle_set
        self.path = path
        self.name = get_game_name(path)
        self.roms = []

        fd = os.open(path, os.O_RDONLY)
        mtime = os.fstat(fd).st_mtime
        os.close(fd)

        cached = self.bundle_set.get_bundle_cache(self.name)
        if cached is not None and mtime <= cached['mtime']:
            # Cache valid, load from cache
            self.roms = cached['roms']

        else:

            # Cache not exist, load from file
            zf = zipfile.ZipFile(self.path)
            for filename in zf.namelist():
                with zf.open(filename) as f:
                    crc = binascii.crc32(f.read())
                    crc = format(crc, '08x')

                    self.roms.append({
                        'name': filename,
                        'crc': crc,
                    })
            
            # Store to cache
            self.bundle_set.set_bundle_cache(
                self.name,
                { 'mtime': mtime, 'roms': self.roms }
            )

        # Create ROM crc map
        self.crc_map = {r['crc']: r['name'] for r in self.roms}

    def compare_with_db(self, game):
        """Compare this bundle with MAMEDB entry to see if
        all ROMs exist.
        :param game: mamedb.Game object.
        """
        result = {}
        for r in game.roms:
            if r.crc in self.crc_map:
                result[r.name] = 'ok'
            elif self.bundle_set.get_rom_by_crc(r.crc):
                result[r.name] = 'other'
            else:
                result[r.name] = 'missing'

        return result

    def get_rom_by_crc(self, crc):
        for rom in self.roms:
            if rom['crc'] == crc:
                return rom

        return None

    def write_version(self, core_name, description):
        """Write version.json in the bundle.
        """
        version = {'core_name': core_name, 'description': description}
        with zipfile.ZipFile(self.path, mode='a') as zf:
            f = zf.open('version.json', 'w')
            f.write(json.dumps(version).encode())
            f.close()

    def read_version(self):
        zf = zipfile.ZipFile(self.path)
        namelist = zf.namelist()
        if 'version.json' in namelist:
            content = zf.open('version.json').read()
            return json.loads(content.decode())

        return None

    def fix_bundle(self, game):
        """Copy ROMs from other bundle to this bundle.
        """
        for r in game.roms:
            # If this bundle already contains given ROM, skip
            if r.crc in self.crc_map:
                continue
            
            # otherwise, see if BundleSet contains ROM
            rom_loc = self.bundle_set.get_rom_by_crc(r.crc)
            other_bundle = self.bundle_set.get_bundle_by_path(rom_loc['bundle_path'])
            rom_content = other_bundle.get_rom_content(rom_loc['name'])
            self.set_rom_content(r.name, rom_content)
            print('Copy %s:%s => %s' % (rom_loc['bundle_name'], rom_loc['name'], r.name))
        
    def get_rom_content(self, rom_name):
        zf = zipfile.ZipFile(self.path)
        return zf.open(rom_name).read()

    def set_rom_content(self, rom_name, content):
        zf = zipfile.ZipFile(self.path, mode='a')
        f = zf.open(rom_name, 'w')
        f.write(content)
        f.close()


class BundleSet:

    def __init__(self, bundle_dir):
        self.bundle_dir = bundle_dir
        self.bundles = []
        self.cache = {}

        cache_file = os.path.join(self.bundle_dir, '.bundlecache.json')
        if os.path.exists(cache_file):
            self.cache = json.loads(open(cache_file).read())

        for bundle_path in self.iter_bundle_paths():
            print('Scanning %s...' % bundle_path)
            self.bundles.append(Bundle(self, bundle_path))

        # Build CRC map
        self.crc_map = {}
        for bundle in self.bundles:
            for rom in bundle.roms:
                self.crc_map[rom['crc']] = {
                    'name': rom['name'],
                    'bundle_name': bundle.name,
                    'bundle_path': bundle.path,
                }

        open(cache_file, 'w').write(json.dumps(self.cache, indent=4))

    def iter_bundle_paths(self):
        for dirname, _, filelist in os.walk(self.bundle_dir):
            for fname in filelist:
                if not fname.endswith('.zip'):
                    continue

                bundle_path = os.path.join(dirname, fname)
                yield(bundle_path)

    def get_bundle_cache(self, name):
        return self.cache.get(name)

    def set_bundle_cache(self, name, bundle):
        self.cache[name] = bundle


    def get_bundle_by_path(self, path):
        for bundle in self.bundles:
            if bundle.path == path:
                return bundle

        return None

    def get_rom_by_crc(self, crc):
        return self.crc_map.get(crc)
