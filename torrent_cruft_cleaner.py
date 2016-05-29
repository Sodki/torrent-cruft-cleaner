#!/usr/bin/env python

import re
import sys
import os
import argparse


#
# handle command line options and parameters
#

parser = argparse.ArgumentParser(description="Lists missing and unknown local files using information from torrent files")
parser.add_argument("directory", metavar="directory", help="directory to check for files")
parser.add_argument("torrents", metavar="torrent", nargs="+", help="source torrent files")
parser.add_argument("-d", "--delete", action="store_true", help="delete files that are not present on the torrent files")
parser.add_argument("-q", "--quiet", action="store_true", help="quiet mode, don't output anything")
args = parser.parse_args()


#
# bencode decoder (from http://effbot.org/zone/bencode.htm)
#

def tokenize(text, match=re.compile("([idel])|(\d+):|(-?\d+)").match):
    i = 0
    while i < len(text):
        m = match(text, i)
        s = m.group(m.lastindex)
        i = m.end()
        if m.lastindex == 2:
            yield "s"
            yield text[i:i+int(s)]
            i = i + int(s)
        else:
            yield s

def decode_item(next, token):
    if token == "i":
        # integer: "i" value "e"
        data = int(next())
        if next() != "e":
            raise ValueError
    elif token == "s":
        # string: "s" value (virtual tokens)
        data = next()
    elif token == "l" or token == "d":
        # container: "l" (or "d") values "e"
        data = []
        tok = next()
        while tok != "e":
            data.append(decode_item(next, tok))
            tok = next()
        if token == "d":
            data = dict(zip(data[0::2], data[1::2]))
    else:
        raise ValueError
    return data

def decode(text):
    try:
        src = tokenize(text)
        data = decode_item(src.next, src.next())
        for token in src: # look for more tokens
            raise SyntaxError("trailing junk")
    except (AttributeError, ValueError, StopIteration):
        raise SyntaxError("syntax error")
    return data


#
# main code
#

# create an array with torrent file list

torrent_files = []
for torrent in args.torrents:
    t = decode(open(torrent, "rb").read())
    for file in t["info"]["files"]:
        torrent_files.append("/".join(file["path"]))

# create an array with directory file list

directory_files = []
for root, subFolders, files in os.walk(args.directory):
    for file in files:
        directory_files.append(os.path.relpath(os.path.join(root, file), args.directory))

# show files in directory that aren't listed in the torrent file

if not args.quiet and not args.delete:
    print "*** files that can be deleted because they're not listed in the torrent files ***"
    for f in sorted(list(set(directory_files).difference(set(torrent_files)))):
        print f

# show files in torrent that are missing in the directory

if not args.quiet and not args.delete:
    print "*** files that are listed in the torrent files, but are not in the directory ***"
    for f in sorted(list(set(torrent_files).difference(set(directory_files)))):
        print f

# delete files that are not listed in the torrent files

if args.delete:
    for f in sorted(list(set(directory_files).difference(set(torrent_files)))):
        p = os.path.join(args.directory, f)
        if not args.quiet:
            print "deleting: %s" % p
        os.remove(p)

