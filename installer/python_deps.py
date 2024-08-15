#!/usr/bin/env python3
import os
import json
import subprocess
import sys

from . import global_vars

from .output import output

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

