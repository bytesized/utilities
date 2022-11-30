#!/usr/bin/env python3
# Kirk Steuber, 2022-11-29
import os
import shutil

def configure(paths, config):
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
