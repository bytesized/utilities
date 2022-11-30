#!/usr/bin/env python3
# Kirk Steuber, 2022-11-30
import os
import subprocess

from . import global_vars

def to_unix_path(to_convert):
  if os.name != "nt":
    return to_convert

  paths = global_vars.get_paths()
  return subprocess.check_output([paths["system"]["cygpath"],
                                 "-u",
                                 to_convert]).decode().strip()
