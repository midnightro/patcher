"""Replace one file inside a small override GRF, keeping every other member byte-identical.

The override archives (`thai_ui.grf`, `ai_system_ui.grf`, ...) are rebuilt from scratch
rather than patched in place, so this reads the current members out, swaps the one named
on the command line, writes the archive again with `make_grf.build`, then reads the result
back and compares every member against what went in.

A backup is taken before the first write and never overwritten, so re-running after a fix
still leaves the original archive recoverable.

Pass `--add` as a fifth argument to put in a member the archive does not have yet. That is
how a file living in a later archive gets overridden: `thai_ui.grf` is entry 0 in DATA.INI,
so a member added there wins over the same path in `new_ai_final.grf` or `data.grf`.
Without the flag an unknown member path is an error, so a typo cannot silently create a
second, dead copy of a file.

Usage: python replace_grf_member.py <grf> <member-path-in-grf> <new-file> <backup-suffix> [--add]

    python replace_grf_member.py Client/ai_system_ui.grf \
        "data\\luafiles514\\lua files\\stateicon\\stateiconinfo.lub" \
        stage/stateiconinfo.lub before_manual_stateicon_20260820
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grf import Grf
from make_grf import build


def main(grf_path, member, new_file, backup_suffix, add=False):
    target = member.encode('latin-1')
    payload = open(new_file, 'rb').read()

    src = Grf(grf_path)
    adding = target not in src.entries
    if adding and not add:
        raise SystemExit('%s has no member %r (pass --add to put it in)'
                         % (grf_path, member))

    backup = '%s.%s' % (grf_path, backup_suffix)
    if not os.path.exists(backup):
        shutil.copy2(grf_path, backup)
        print('backup ->', backup)
    else:
        print('backup kept ->', backup)

    files = []
    for name in src.entries:
        data = payload if name == target else src.read(name)
        files.append((name, data))
        # repr(bytes) stays ASCII-safe even when the Windows console uses CP874
        # and the archive member contains Korean filename bytes.
        print('  %-8s %r (%d bytes)' % ('replace' if name == target else 'keep',
                                        name, len(data)))
    if adding:
        files.append((target, payload))
        print('  %-8s %r (%d bytes)' % ('add', target, len(payload)))

    # Windows denies opening the archive for rewrite while the reader still
    # holds it open.  All member data is in memory now, so release the handle
    # before make_grf.build() truncates and recreates the same path.
    src.close()
    build(grf_path, files)

    check = Grf(grf_path)
    for name, data in files:
        if check.read(name) != data:
            raise SystemExit('member did not survive the write: %r' % name)
    print('verify OK: %d member(s) round-trip' % len(files))


if __name__ == '__main__':
    args = sys.argv[1:]
    add = '--add' in args
    args = [a for a in args if a != '--add']
    if len(args) != 4:
        raise SystemExit(__doc__)
    main(*args, add=add)
