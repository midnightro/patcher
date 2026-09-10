"""
Minimal reader for GRF v2.0 archives (the format used by Ragnarok Online).

Layout:
  header 46 bytes:  "Master of Magic"(15) key(15) tableOffset(4) seed(4)
                    fileCount(4) version(4)
  file table at 46+tableOffset:  compressedSize(4) realSize(4) <zlib data>
  each entry:  name\0  compressedSize(4) compressedSizeAligned(4)
               realSize(4) flags(1) offset(4)
  file data at 46+offset, zlib-compressed.
"""
import struct, zlib, sys, io

HEADER_LEN = 46
MAGIC = b"Master of Magic"

class Grf:
    def __init__(self, path):
        self.path = path
        self.f = open(path, 'rb')
        hdr = self.f.read(HEADER_LEN)
        # Some private-server tools rewrite the 15-byte magic (e.g. "Event Horizon")
        # while keeping the layout identical, so the version field is the real check.
        self.magic = hdr[:15]
        (self.table_offset, self.seed,
         self.file_count_raw, self.version) = struct.unpack_from('<IIII', hdr, 30)
        if self.version not in (0x200, 0x300):
            raise ValueError(f"unsupported GRF version 0x{self.version:X} "
                             f"(magic={self.magic!r})")
        self.entries = {}
        self._read_table()

    def _read_table(self):
        # v0x300 stores the table offset as 64 bits: the low dword in table_offset
        # and the high dword in the field that v0x200 uses as the seed. Without this
        # any archive larger than 4 GB (our own data.grf) reads garbage.
        offset = self.table_offset
        if self.version == 0x300:
            offset |= self.seed << 32
        self.f.seek(HEADER_LEN + offset)
        if self.version == 0x200:
            comp_size, real_size = struct.unpack('<II', self.f.read(8))
            entry_fmt, entry_len = '<IIIBI', 17          # 32-bit data offsets
        else:
            # v0x300 adds a leading field and stores 64-bit data offsets, which is
            # what lets an archive grow past 4 GB.
            _pad, comp_size, real_size = struct.unpack('<III', self.f.read(12))
            entry_fmt, entry_len = '<IIIBQ', 21          # 64-bit data offsets
        table = zlib.decompress(self.f.read(comp_size))
        pos = 0
        n = len(table)
        while pos < n:
            end = table.find(b'\x00', pos)
            if end == -1:
                break
            name = table[pos:end]
            pos = end + 1
            if pos + entry_len > n:
                break
            csize, csize_aligned, rsize, flags, offset = struct.unpack_from(entry_fmt, table, pos)
            pos += entry_len
            self.entries[name] = dict(csize=csize, rsize=rsize, flags=flags, offset=offset)

    def find(self, needle: bytes):
        needle = needle.lower()
        return [n for n in self.entries if needle in n.lower()]

    def read(self, name: bytes) -> bytes:
        e = self.entries[name]
        if e['flags'] & 0x06:
            raise NotImplementedError(f"{name!r} is DES-encrypted (flags={e['flags']})")
        self.f.seek(HEADER_LEN + e['offset'])
        raw = self.f.read(e['csize'])
        data = zlib.decompress(raw)
        if len(data) != e['rsize']:
            raise ValueError(f"size mismatch for {name!r}")
        return data

    def close(self):
        self.f.close()


if __name__ == '__main__':
    mode = sys.argv[1]
    grf_path = sys.argv[2]
    g = Grf(grf_path)
    if mode == 'find':
        out = sys.argv[4] if len(sys.argv) > 4 else None
        hits = g.find(sys.argv[3].encode('latin-1'))
        lines = [f"{len(g.entries)} entries in archive", f"{len(hits)} match(es):"]
        for h in hits[:60]:
            e = g.entries[h]
            lines.append(f"  {h.decode('latin-1')}  real={e['rsize']} flags={e['flags']}")
        text = '\n'.join(lines)
        if out:
            open(out, 'w', encoding='utf-8').write(text)
        print(text)
    elif mode == 'extract':
        name = sys.argv[3].encode('latin-1')
        dst = sys.argv[4]
        data = g.read(name)
        open(dst, 'wb').write(data)
        print(f"extracted {len(data)} bytes -> {dst}")
    g.close()
