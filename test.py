from mame.dat import DatFile

datfile = DatFile()
# content = open('./mamedb/MAME v0.139.dat').read()
content = open('./mamedb/MAME v0.78.dat').read()
datfile.parse(content)
import ipdb; ipdb.set_trace()