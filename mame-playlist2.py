def generate_mame_playlist(root, romdir):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=str, nargs=1, required=True, help='RetroArch root dir.')
    parser.add_argument('--romdir', type=str, nargs=1, required=True, help='ROM directory.')
    args = parser.parse_args()

    playlist = generate_mame_playlist(args.root[0], args.romdir[0])
    

