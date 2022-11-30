#!/usr/bin/env python3
# Kirk Steuber, 2022-11-30
import os
import subprocess

def to_unix_path(config, paths, to_convert):
  if os.name != "nt":
    return to_convert
  return subprocess.check_output([paths["system"]["cygpath"],
                                 "-u",
                                 to_convert]).decode().strip()
