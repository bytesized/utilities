#!/usr/bin/env python3
import os
import json
import subprocess
import sys

from . import global_vars

from .output import output

dependencies = [
  "progressbar2",
]

windows_dependencies = [
  "win11toast",
]

class PipFailed(Exception):
  """
    Raised if we try to run pip and it fails
    """
  pass

def run_pip(args, capture_stderr = True):
  paths = global_vars.get_paths()

  if paths["system"]["yes"] is None:
    raise EnvironmentError("Error: Cannot find 'yes' in PATH.")

  yes_process = subprocess.Popen(
    [paths["system"]["yes"]],
    stdout = subprocess.PIPE, stderr = subprocess.DEVNULL)

  pip_args = [paths["system"]["python3"], "-m", "pip"] + args
  stderr = subprocess.STDOUT if capture_stderr else None
  result = subprocess.run(
    pip_args, stdin = yes_process.stdout, stdout = subprocess.PIPE, stderr = stderr)
  yes_process.stdout.close()
  yes_process.wait()
  if result.returncode != 0:
    print(result.stdout, file = sys.stderr)
    raise PipFailed()

def install():
  paths = global_vars.get_paths()

  all_deps = dependencies.copy()
  if os.name == "nt":
    all_deps.extend(windows_dependencies)
  all_deps.sort()

  output(f"Installing {', '.join(all_deps)}")
  for dependency in all_deps:
    run_pip(["install", "--upgrade", "--target", paths["user"]["lib"]["python"], dependency])

