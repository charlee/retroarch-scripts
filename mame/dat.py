import xml.etree.ElementTree as ET
from .cm import CMParser

class Rom:
    def __init__(self, **kwargs):
        for k in ('name', 'size', 'crc', 'sha1'):
            setattr(self, k, kwargs.get(k))

    def __repr__(self):
        return '<Rom: name=%s>' % self.name

class Game:
    def __init__(self, **kwargs):
        for k in ('name', 'description', 'year', 'manufacturer',
                  'sourcefile', 'cloneof', 'romof'):
            setattr(self, k, kwargs.get(k))
        self.roms = []

    def add_rom(self, rom):
        self.roms.append(rom)

    def __repr__(self):
        return '<Game: name=%s>' % self.name


class MameDB:
    def __init__(self, **kwargs):
        for k in ('name', 'description', 'category', 'version', 'author'):
            setattr(self, k, kwargs.get(k))
        self.games = []

    def add_game(self, game):
        self.games.append(game)

    def __repr__(self):
        return '<MameDB: name=%s>' % self.name

class DatFile:

    def parse(self, content):
        if '<?xml version="1.0"?>' in content:
            self.parse_xml(content)
        else:
            self.parse_cm(content)

    def extract_child(self, elem, child_tag):
        child = elem.find(child_tag)
        if child is not None:
            return child.text
        else:
            return None

    def extract_attr(self, elem, attr_name):
        return elem.attrib.get(attr_name)

    def parse_xml(self, content):
        db = MameDB()
        root = ET.fromstring(content)
        for g in root:
            if g.tag == 'header':
                db.name = self.extract_child(g, 'name')
                db.description = self.extract_child(g, 'description')
                db.category = self.extract_child(g, 'category')
                db.version = self.extract_child(g, 'version')
                db.author = self.extract_child(g, 'author')

            if g.tag == 'game':
                game = Game(
                    name=self.extract_attr(g, 'name'),
                    description=self.extract_child(g, 'description'),
                    year=self.extract_child(g, 'year'),
                    manufacturer=self.extract_child(g, 'manufacturer'),
                    sourcefile=self.extract_attr(g, 'sourcefile'),
                    cloneof=self.extract_attr(g, 'cloneof'),
                    romeof=self.extract_attr(g, 'romof'),
                )

                for r in g.findall('rom'):
                    rom = Rom(
                        name=self.extract_attr(r, 'name'),
                        merge=self.extract_attr(r, 'merge'),
                        size=self.extract_attr(r, 'size'),
                        crc=self.extract_attr(r, 'crc'),
                        sha1=self.extract_attr(r, 'sha1'),
                    )
                    game.add_rom(rom)

                db.add_game(game)
        
        self.db = db

    def parse_cm(self, content):
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
                    rom = Rom(
                        name=rv.get('name'),
                        merge=rv.get('merge'),
                        size=rv.get('size'),
                        crc=rv.get('crc'),
                        sha1=rv.get('sha1'),
                    )

                    game.add_rom(rom)

                db.add_game(game)

        self.db = db