from mame import MAME
from mame.bundle_dir import BundleDir

mame = MAME('~/.var/app/org.libretro.RetroArch/config/retroarch')
mame.ensure_mamedbs()

mame.fix_bundles('./roms1')