#!/usr/bin/python3

import glob
import os
from optparse import OptionParser
from struct import Struct
from urllib.parse import parse_qs
from urllib.request import urlopen
from urllib.error import HTTPError
import struct
import codecs

table = [
    22136, 52719, 55146, 42104, 
    59591, 46934, 9248,  28891,
    49597, 52974, 62844, 4015,
    18311, 50730, 43056, 17939,
    64838, 38145, 27008, 39128,
    35652, 63407, 65535, 23473,
    35164, 55230, 27536, 4386,
    64920, 29075, 42617, 17294,
    18868, 2081
]

def tenhouHash(game):
    code_pos = game.rindex("-") + 1
    code = game[code_pos:]
    if code[0] == 'x':
        a,b,c = struct.unpack(">HHH", bytes.fromhex(code[1:]))     
        index = 0
        if game[:12] > "2010041111gm":
            x = int("3" + game[4:10])
            y = int(game[9])
            index = x % (33 - y)
        first = (a ^ b ^ table[index]) & 0xFFFF
        second = (b ^ c ^ table[index] ^ table[index + 1]) & 0xFFFF
        return game[:code_pos] + codecs.getencoder('hex_codec')(struct.pack(">HH", first, second))[0].decode('ASCII')
    else:
        return game

p = OptionParser()
p.add_option('-d', '--directory',
        default=os.path.expanduser('~/.tenhou-game-xml'),
        help='Directory in which to store downloaded XML')
opts, args = p.parse_args()
if args:
    p.error('This command takes no positional arguments')

sol_files = []
sol_files.extend(glob.glob(os.path.join(
    os.path.expanduser('~'),
    '.config/chromium/*/Pepper Data/Shockwave Flash/WritableRoot/#SharedObjects/*/mjv.jp/mjinfo.sol')))
sol_files.extend(glob.glob(os.path.join(
    os.path.expanduser('~'),
    '.config/google-chrome/*/Pepper Data/Shockwave Flash/WritableRoot/#SharedObjects/*/mjv.jp/mjinfo.sol')))
sol_files.extend(glob.glob(os.path.join(
    os.path.expanduser('~'),
    '.macromedia/Flash_Player/#SharedObjects/*/mjv.jp/mjinfo.sol')))

if not os.path.exists(opts.directory):
    os.makedirs(opts.directory)

for sol_file in sol_files:
    print("Reading Flash state file: {}".format(sol_file))
    with open(sol_file, 'rb') as f:
        data = f.read()
    # What follows is a limited parser for Flash Local Shared Object files -
    # a more complete implementation may be found at:
    # https://pypi.python.org/pypi/PyAMF
    header = Struct('>HI10s8sI')
    magic, objlength, magic2, mjinfo, padding = header.unpack_from(data)
    offset = header.size
    assert magic == 0xbf
    assert magic2 == b'TCSO\0\x04\0\0\0\0'
    assert mjinfo == b'\0\x06mjinfo'
    assert padding == 0
    ushort = Struct('>H')
    ubyte = Struct('>B')
    while offset < len(data):
        length, = ushort.unpack_from(data, offset)
        offset += ushort.size
        name = data[offset:offset+length]
        offset += length
        amf0_type, = ubyte.unpack_from(data, offset)
        offset += ubyte.size
        # Type 2: UTF-8 String, prefixed with 2-byte length
        if amf0_type == 2:
            length, = ushort.unpack_from(data, offset)
            offset += ushort.size
            value = data[offset:offset+length]
            offset += length
        # Type 6: Undefined
        elif amf0_type == 6:
            value = None
        # Type 1: Boolean
        elif amf0_type == 1:
            value = bool(data[offset])
            offset += 1
        # Other types from the AMF0 specification are not implemented, as they
        # have not been observed in mjinfo.sol files. If required, see
        # http://download.macromedia.com/pub/labs/amf/amf0_spec_121207.pdf
        else:
            print("Unimplemented AMF0 type {} at offset={} (hex {})".format(amf0_type, offset, hex(offset)))
        trailer_byte = data[offset]
        assert trailer_byte == 0
        offset += 1
        if name == b'logstr':
            loglines = filter(None, value.split(b'\n'))

    for logline in loglines:
        logname = parse_qs(logline.decode('ASCII'))['file'][0]
        logname = tenhouHash(logname)
        target_fname = os.path.join(opts.directory, "{}.xml".format(logname))
        if os.path.exists(target_fname):
            print("Game {} already downloaded".format(logname))
        else:
            print("Downloading game {}".format(logname))
            try:
                resp = urlopen('http://e.mjv.jp/0/log/?' + logname)
                data = resp.read()
                with open(target_fname, 'wb') as f:
                    f.write(data)
            except HTTPError as e:
                if e.code == 404:
                    print("Could not download game {}. Is the game still in progress?".format(logname))
                else:
                    raise
