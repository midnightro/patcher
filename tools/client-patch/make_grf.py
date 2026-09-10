"""
Build a minimal GRF v2.0 archive containing a few override files.

The client reads GRFs listed in DATA.INI in order, and an entry found in an
earlier archive wins, so a small archive listed first can override files that
live inside the big data.grf / new.grf.

Layout written here (standard GRF 0x200):
    header 46 bytes : "Master of Magic"(15) key(15) tableOffset(4) seed(4)
                      fileCountField(4) version(4)
    file data       : each entry zlib-compressed, back to back, from offset 46
    file table      : compSize(4) realSize(4) <zlib( name\\0 + 17-byte entry ... )>
"""
import struct, zlib, sys, os

MAGIC = b"Master of Magic"
KEY   = bytes(range(15))          # 00 01 02 ... 0E, the usual key
HEADER_LEN = 46
VERSION = 0x200
FLAG_FILE = 1

def build(out_path, files, verbose=True):
    """files: list of (archive_name_bytes, content_bytes)"""
    blobs = []
    entries = []
    offset = 0                     # relative to HEADER_LEN
    for name, content in files:
        comp = zlib.compress(content, 9)
        aligned = len(comp)
        blobs.append(comp)
        entries.append((name, len(comp), aligned, len(content), FLAG_FILE, offset))
        offset += len(comp)

    table = bytearray()
    for name, csize, aligned, rsize, flags, off in entries:
        table += name + b'\x00'
        table += struct.pack('<IIIBI', csize, aligned, rsize, flags, off)
    table_comp = zlib.compress(bytes(table), 9)

    table_offset = offset          # data ends here (relative to HEADER_LEN)

    with open(out_path, 'wb') as f:
        f.write(MAGIC)
        f.write(KEY)
        f.write(struct.pack('<IIII',
                            table_offset,
                            0,                       # seed
                            len(files) + 7,          # count field = files + seed + 7
                            VERSION))
        for b in blobs:
            f.write(b)
        f.write(struct.pack('<II', len(table_comp), len(table)))
        f.write(table_comp)

    if verbose:
        print(f"wrote {out_path} ({os.path.getsize(out_path)} bytes, {len(files)} file(s))")
        for name, _c, _a, rsize, _f, _o in entries:
            # member names carry raw Korean/Thai bytes; a CP874 console cannot encode them, so
            # write the bytes straight out rather than let print() raise mid-build
            line = b"   " + name + f"  ({rsize} bytes)\n".encode('latin-1')
            sys.stdout.flush()
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()

if __name__ == '__main__':
    out = sys.argv[1]
    files = []
    for pair in sys.argv[2:]:
        arch_name, disk_path = pair.split('=', 1)
        files.append((arch_name.encode('latin-1'), open(disk_path, 'rb').read()))
    build(out, files)
