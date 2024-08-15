#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import urllib.request

from . import global_vars
from .output import output

# Always use https URLs here so that authentication and unknown ssh hosts aren't a problem.
repos = {
  "rust": {
    "bcalc": "https://github.com/bytesized/bcalc.git",
  },
}

def fetch():
  paths = global_vars.get_paths()

  initial_cwd = os.getcwd()

  for lang, lang_repos in repos.items():
    lang_dir_path = os.path.join(paths["user"]["repos"], lang)
    os.makedirs(lang_dir_path, exist_ok = True)
    for name, url in lang_repos.items():
      output(f"Fetching {name}...")
      path = os.path.join(lang_dir_path, name)
      if os.path.exists(path):
        os.chdir(path)
        result = subprocess.run(
          [paths["system"]["git"], "pull"],
          stderr = subprocess.STDOUT,
          stdout = subprocess.PIPE,
          encoding = "utf8"
        )
        if result.returncode != 0:
          print(f"Error pulling from external repository '{name}'\n", file = sys.stderr)
          print(result.stdout, file = sys.stderr)
          sys.exit(1)
      else:
        result = subprocess.run(
          [paths["system"]["git"], "clone", url, path],
          stderr = subprocess.STDOUT,
          stdout = subprocess.PIPE,
          encoding = "utf8"
        )
        if result.returncode != 0:
          print(f"Error cloning external repository '{name}'\n", file = sys.stderr)
          print(result.stdout, file = sys.stderr)
          sys.exit(1)
      global_vars.add_build_dir(lang, name, path)

  os.chdir(initial_cwd)
