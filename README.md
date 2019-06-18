RetroArch Scripts
==================


This repo contains some scripts useful in [RetroArch](https://www.retroarch.com/).

## MAME

### `mame-playlist.py`

Generate mame playlist based on filename, not CRC.
You must specify a core file (`--core`), a ROM dir (`--romdir`) and the playlist file
you want to generate.

Example (if you are using flatpak installation):

```
$ python mame-playlist.py \
      --core=~/.var/app/org.libretro.RetroArch/config/retroarch/cores/mame2010_libretro.so
      --romdir=~/roms/MAME
      ~/.var/app/org.libretro.RetroArch/config/retroarch/playlists/MAME.lpl
```

### `mame-thumbnails.py`

Auto download thumbnails based on given playlist.
You must specify a playlist file (`--playlist`) located in your retroarch `playlists` directory.
Downloaded thumbnail files will be placed in the `thumbmails` directory.

Example (if you are using flatpak):

```
$ python mame-thumbnails.py \
      --playlist=~/.var/app/org.libretro.RetroArch/config/retroarch/playlists/MAME.lpl
```

In above example, downloaded thumbnails will be placed under `~/.var/app/org.libretro.RetroArch/config/retroarch/thumbnails`.
