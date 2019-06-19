import xml.etree.ElementTree as ET
from .cm import CMParser

class Rom:
    def __init__(self, **kwargs):
        for k in ('name', 'merge', 'size', 'crc', 'sha1'):
            setattr(self, k, kwargs.get(k))

    def __repr__(self):
        return '<Rom: name=%s>' % self.name

class Game:
    def __init__(self, **kwargs):
        for k in ('name', 'description', 'year', 'manufacturer',
                  'sourcefile', 'cloneof', 'romof'):
            setattr(self, k, kwargs.get(k))
        self.roms = []
        self.rom_map = {}

    def add_rom(self, rom):
        self.roms.append(rom)
        self.rom_map[rom.crc] = rom

    def __repr__(self):
        return '<Game: name=%s>' % self.name


class MameDB:
    def __init__(self, **kwargs):
        for k in ('name', 'description', 'category', 'version', 'author'):
            setattr(self, k, kwargs.get(k))
        self.core_name = None
        self.games = []
        self.game_map = {}

    def add_game(self, game):
        self.games.append(game)
        self.game_map[game.name] = game

    def get_game(self, game_name):
        if game_name.endswith('.zip'):
            game_name = game_name[:-4]

        return self.game_map.get(game_name)

    def __repr__(self):
        return '<MameDB: name=%s>' % self.name


def extract_child(elem, child_tag):
    child = elem.find(child_tag)
    if child is not None:
        return child.text
    else:
        return None

def extract_attr(elem, attr_name):
    return elem.attrib.get(attr_name)

def parse_xml(content):
    db = MameDB()
    root = ET.fromstring(content)
    for g in root:
        if g.tag == 'header':
            db.name = extract_child(g, 'name')
            db.description = extract_child(g, 'description')
            db.category = extract_child(g, 'category')
            db.version = extract_child(g, 'version')
            db.author = extract_child(g, 'author')

        if g.tag == 'game':
            game = Game(
                name=extract_attr(g, 'name'),
                description=extract_child(g, 'description'),
                year=extract_child(g, 'year'),
                manufacturer=extract_child(g, 'manufacturer'),
                sourcefile=extract_attr(g, 'sourcefile'),
                cloneof=extract_attr(g, 'cloneof'),
                romeof=extract_attr(g, 'romof'),
            )

            for r in g.findall('rom'):
                # Skip 'nodump' ROMS
                if extract_attr(r, 'status') == 'nodump':
                    continue

                rom = Rom(
                    name=extract_attr(r, 'name'),
                    merge=extract_attr(r, 'merge'),
                    size=extract_attr(r, 'size'),
                    crc=extract_attr(r, 'crc'),
                    sha1=extract_attr(r, 'sha1'),
                )
                game.add_rom(rom)

            db.add_game(game)
    
    return db

def parse_cm(content):
    db = MameDB()
    parser = CMParser()
    cm_data = parser.parse(content)
    for item in cm_data:
        if item[0] == 'clrmamepro':
            value = dict(item[1])
            db.name = value.get('name')
            db.description = value.get('description')
            db.category = value.get('category')
            db.version = value.get('version')
            db.author = value.get('author')
        
        if item[0] == 'game':
            value = dict([attr for attr in item[1] if attr[0] != 'rom'])
            game = Game(
                name=value.get('name'),
                description=value.get('description'),
                year=value.get('year'),
                manufacturer=value.get('manufacturer'),
                sourcefile=value.get('sourcefile'),
                cloneof=value.get('cloneof'),
                romeof=value.get('romof'),
            )

            roms_value = [dict(attr[1]) for attr in item[1] if attr[0] == 'rom']
            for rv in roms_value:
                # Skip 'nodump' ROMS
                if rv.get('status') == 'nodump':
                    continue

                rom = Rom(
                    name=rv.get('name'),
                    merge=rv.get('merge'),
                    size=rv.get('size'),
                    crc=rv.get('crc'),
                    sha1=rv.get('sha1'),
                )

                game.add_rom(rom)

            db.add_game(game)

    return db

def parse_datfile(content):
    if '<?xml version="1.0"?>' in content:
        return parse_xml(content)
    else:
        return parse_cm(content)
