import argparse
from retroarch.mame import MAME


def generate_mame_playlist(root, romdir):
    mame = MAME(root)
    mame.fix_bundles(romdir)
    mame.make_playlist(romdir, 'MAME.lpl')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=str, nargs=1, required=True, help='RetroArch root.')
    parser.add_argument('--romdir', type=str, nargs=1, required=True, help='ROM directory.')
    args = parser.parse_args()

    playlist = generate_mame_playlist(args.core[0], args.romdir[0])
    