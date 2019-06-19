from mame import MAME

mame = MAME('~/.var/app/org.libretro.RetroArch/config/retroarch')

mame.fix_bundles('./roms1')
mame.make_playlist('./roms1', 'MAME.lpl')