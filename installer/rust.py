#!/usr/bin/env python3
import os
import subprocess
import sys

from . import global_vars
from .output import output

install_script_url = "https://sh.rustup.rs"

exe_extension = ""
if os.name == "nt":
  exe_extension = ".exe"

def install_cargo():
  paths = global_vars.get_paths()

  if paths["system"]["curl"] is None:
    raise EnvironmentError("Error: Cannot find 'curl' in PATH.")
  if paths["system"]["sh"] is None:
    raise EnvironmentError("Error: Cannot find 'sh' in PATH.")

  download_process = subprocess.Popen(
    [paths["system"]["curl"], "--proto", "=https", "--tlsv1.2", "-sSf", install_script_url],
    stdout = subprocess.PIPE, stderr = subprocess.DEVNULL)
  shell_process = subprocess.run(
    [paths["system"]["sh"], "-s", "--", "-y"],
    stdin = download_process.stdout, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
  download_process.stdout.close()
  if download_process.wait() != 0:
    raise Exception("Rust install failed")
  shell_process.check_returncode()

  if os.name == "nt":
    paths["system"]["cargo"] = \
      os.path.join(os.environ["USERPROFILE"], ".cargo", "bin", "cargo.exe")
  else:
    paths["system"]["cargo"] = \
      os.path.join(os.environ["HOME"], ".cargo", "bin", "cargo")

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
