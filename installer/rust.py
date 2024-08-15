#!/usr/bin/env python3
import os
import subprocess
import sys

from . import global_vars
from .output import output

def build():
  paths = global_vars.get_paths()

  initial_cwd = os.getcwd()

  for name, dir_path in global_vars.get_build_dirs("rust").items():
    output(f"Building {name}...")
    os.chdir(dir_path)
    result = subprocess.run(
      [paths["system"]["cargo"], "build", "--release"],
      stderr = subprocess.STDOUT,
      stdout = subprocess.PIPE,
      encoding = "utf8"
    )
    if result.returncode != 0:
      print(f"Error building '{name}'\n", file = sys.stderr)
      print(result.stdout, file = sys.stderr)
      sys.exit(1)
    global_vars.add_bin_dir(os.path.join(dir_path, "target", "release"))

  os.chdir(initial_cwd)
