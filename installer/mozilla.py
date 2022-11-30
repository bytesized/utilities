#!/usr/bin/env python3
# Kirk Steuber, 2022-11-29
import os
import shutil

from . import global_vars

def configure():
  config = global_vars.get_config()
  paths = global_vars.get_paths()

  if config["uninstall"]:
    # There isn't really anything to be done here. All the Mozilla configuration lives in the
    # utilities user config directory which will be removed during the uninstall anyways.
    return;

  # The existence of this folder tells `universal.bashrc` to set some Mozilla-specific variables.
  mozilla_config_dir_path = os.path.join(paths["user"]["config"], "mozilla")
  if config["mozilla"]:
    os.makedirs(mozilla_config_dir_path, exist_ok = True)
  else:
    try:
      shutil.rmtree(mozilla_config_dir_path)
    except FileNotFoundError:
      pass
