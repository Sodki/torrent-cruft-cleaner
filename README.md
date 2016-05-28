# torrent-cruft-cleaner

Lists missing and unknown local files using information from torrent files.

## Usage

```
usage: torrent_cruft_cleaner.py [-h] [-d] [-q] directory torrent [torrent ...]

Lists missing and unknown local files using information from torrent files

positional arguments:
  directory     directory to check for files
  torrent       source torrent files

optional arguments:
  -h, --help    show this help message and exit
  -d, --delete  delete files that are not present on the torrent files
  -q, --quiet   quiet mode, don't output anything
```
