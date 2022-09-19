# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\json\tool.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1508 bytes
import argparse, json, sys

def main():
    prog = 'python -m json.tool'
    description = 'A simple command line interface for json module to validate and pretty-print JSON objects.'
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument('infile', nargs='?', type=(argparse.FileType()), help='a JSON file to be validated or pretty-printed')
    parser.add_argument('outfile', nargs='?', type=(argparse.FileType('w')), help='write the output of infile to outfile')
    parser.add_argument('--sort-keys', action='store_true', default=False, help='sort the output of dictionaries alphabetically by key')
    options = parser.parse_args()
    infile = options.infile or sys.stdin
    outfile = options.outfile or sys.stdout
    sort_keys = options.sort_keys
    with infile:
        try:
            obj = json.load(infile)
        except ValueError as e:
            try:
                raise SystemExit(e)
            finally:
                e = None
                del e

    with outfile:
        json.dump(obj, outfile, sort_keys=sort_keys, indent=4)
        outfile.write('\n')


if __name__ == '__main__':
    main()