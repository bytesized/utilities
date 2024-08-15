#!/usr/bin/env python3
import os
import json
import subprocess
import sys

from . import cygpath, global_vars

from .output import output

# The fact that these packages may have their own dependencies makes this whole thing sort of
# annoying, but we do our best to keep track of everything that got installed when we ran pip so
# that we can uninstall all of them when requested.
dependencies = [
  "progressbar2",
  "win11toast",
]

class PipFailed(Exception):
  """
    Raised if we try to run pip and it fails
    """
  pass

def run_pip(args, capture_stderr = True):
  pip_args = ["python3", "-m", "pip"] + args
  stderr = subprocess.STDOUT if capture_stderr else None
  result = subprocess.run(pip_args, stdout = subprocess.PIPE, stderr = stderr)
  if result.returncode != 0:
    print(result.stdout, file = sys.stderr)
    raise PipFailed()
  return result.stdout.decode("utf-8")

def install():
  paths = global_vars.get_paths()

  output(f"Installing {', '.join(sorted(dependencies))}")
  for dependency in dependencies:
    run_pip(["install", "--upgrade", "--target", paths["user"]["lib"]["python"], dependency])

