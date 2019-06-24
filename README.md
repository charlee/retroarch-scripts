RetroArch Scripts
==================


This repo contains some scripts useful in [RetroArch](https://www.retroarch.com/).

## MAME

### `mame-playlist.py`

Generate mame playlist.
This script will do the following:

- Scan cores and download corresponding MAME DB
- Scan ROMs and find a core version that can run this ROM
- Re-bundle the ROMs so that all the necessary ROM files are combined in one zip file
  (a.k.a. "merge")
- Generate playlist using corresponding core of each ROM
- Download thumbnails for the playlist

You must specify the RetroArch root dir (`--root`), a ROM dir (`--romdir`).
The playlist generated will be named as `MAME.lst`.

Example (if you are using flatpak installation):

```
$ python mame-playlist.py \
      --root=~/.var/app/org.libretro.RetroArch/config/retroarch
      --romdir=~/roms/MAME
```

