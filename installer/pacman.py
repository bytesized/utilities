#!/usr/bin/env python3
import subprocess
import sys

packages = [
  "vim",
]

class PacmanFailed(Exception):
  """
    Raised if we try to run pacman and it fails
    """
  pass

def run_pacman(args, capture_stderr = True):
  pip_args = ["pacman"] + args
  stderr = subprocess.STDOUT if capture_stderr else None
  result = subprocess.run(pip_args, stdout = subprocess.PIPE, stderr = stderr)
  if result.returncode != 0:
    print(result.stdout, file = sys.stderr)
    raise PacmanFailed()
  return result.stdout.decode("utf-8")

def install():
  for package in packages:
    run_pacman(["-S", "--noconfirm", package])

def uninstall():
  for package in packages:
    run_pacman(["-R", "--noconfirm", package])
