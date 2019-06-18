import os
import re
import urllib.parse
import json
import argparse
import requests
import zipfile
import xml.etree.ElementTree as ET

MAME_VER_MAP = {
    '2010': 'MAME v0.139 (xml).zip',
}

MAMEDB_PATH = 'mamedb'

def abspath(path):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

def ensure_db(db_file):
    db_path = os.path.join(MAMEDB_PATH, db_file)
    if not os.path.exists(db_path):
        os.makedirs(MAMEDB_PATH, exist_ok=True)
        url = 'http://www.logiqx.com/Dats/MAMEBeta/' + urllib.parse.quote(db_file)
        r = requests.get(url)
        open(db_path, 'wb').write(r.content)

    return db_path

def read_games(db_path):
    """Read MAME db xml file and generate a supported game database.
    Return value is a dictionary with form of {'game_name': 'game_title'}.
    """
    games = {}
    db = zipfile.ZipFile(db_path, 'r')
    db_entry = [f for f in db.namelist() if f.endswith('.dat')]
    if not db_entry:
        print('Error: db corrupted')
        exit(3)
    
    f = db.open(db_entry[0])
    xml = f.read()
    f.close()

    root = ET.fromstring(xml)
    for child in root:
        if child.tag == 'game':
            rom_name = child.attrib.get('name')
            desc = child.find('description')
            rom_title = desc.text

            if rom_name and rom_title:
                games[rom_name] = rom_title

    return games

def scan_roms(romdir):
    """Scan romdir and output full paths for all the zip files."""
    roms = []
    for dirname, _, filelist in os.walk(romdir):
        for fname in filelist:
            if not fname.endswith('.zip'):
                continue
            filepath = abspath(os.path.join(dirname, fname))
            roms.append(filepath)
    
    return roms

def make_playlist(core, owned_roms, games, playlist):
    db_name = os.path.basename(playlist)
    core_path = abspath(core)

    items = []

    for rom in owned_roms:
        rom_name = os.path.basename(rom).rsplit('.')[0]
        if rom_name not in games:
            continue

        entry = {
            'path': rom,
            'label': games[rom_name],
            'core_path': core_path,
            'core_name': 'DETECT',
            'crc32': 'DETECT',
            'db_name': db_name,
        }

        items.append(entry)

    return {
        'version': '1.0',
        'items': items,
    }


def generate_mame_playlist(core, romdir, output_playlist):
    core_name = os.path.basename(core)
    m = re.match(r'^mame(\d+)_.*$', core_name)
    if not m:
        print('Error: unknown core name')
        exit(1)

    mame_version = m.group(1)
    if mame_version not in MAME_VER_MAP:
        print('Error: unknown mame version')
        exit(2)
    
    db_file = MAME_VER_MAP[mame_version]
    db_path = ensure_db(db_file)
    games = read_games(db_path)

    owned_roms = scan_roms(romdir)
    playlist = make_playlist(core, owned_roms, games, output_playlist)
    open(output_playlist, 'w').write(json.dumps(playlist, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--core', type=str, nargs=1, required=True, help='Core file.')
    parser.add_argument('--romdir', type=str, nargs=1, required=True, help='ROM directory.')
    parser.add_argument('output_playlist', type=str, nargs=1, help='Output playlist.')
    args = parser.parse_args()

    playlist = generate_mame_playlist(args.core[0], args.romdir[0], args.output_playlist[0])
    
