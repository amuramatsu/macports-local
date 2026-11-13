#! /usr/bin/env python3

import re
from pathlib import Path
import semver

ORIG_PORT_DIR = Path("/opt/local/var/macports/sources/rsync.macports.org/"
                     "macports/release/tarballs/ports")
LOCAL_PORT_DIR = Path(__file__).parent

VER_CHECK_RE = re.compile(r'\s*(version|revision)\s+([^\s]+)')
GIT_VER = re.compile(r'\s*(gitlab|github)\.setup\s+'
                     r'([^\s]+)\s+([^\s]+)\s+([^\s]+)')
def check_port_version(portfile):
    portname = portfile.parent.stem
    version = None
    git_version = None
    revision = 0
    with open(portfile, encoding="utf-8") as f:
        for line in f:
            m = VER_CHECK_RE.match(line)
            if m:
                name = m.group(1)
                data = m.group(2)
                if name == "version":
                    version = data
                if name == "revision":
                    revision = data
                continue
            m = GIT_VER.match(line)
            if m:
                git_version = m.group(4)
    if version is None:
        version = git_version
    return portname, version, revision

def check_local_ports():
    for f in LOCAL_PORT_DIR.glob('*/*/Portfile'):
        portname, version, revision = check_port_version(f)
        orig_port = list(ORIG_PORT_DIR.glob('*/{}/Portfile'.format(portname)))
        if len(orig_port) == 1:
            _, orig_version, orig_revision = check_port_version(orig_port[0])
            updated = False
            try:
                if semver.compare(version, orig_version) < 0:
                    updated = True
            except:
                pass
            if int(revision) < int(orig_revision):
                updated = True
            if updated:
                print(f"{portname} is updated by upstream "
                      f"({version}_{revision} --> "
                      f"{orig_version}_{orig_revision})")
        
if __name__ == "__main__":
    check_local_ports()
