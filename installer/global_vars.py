#!/usr/bin/env python3
# Kirk Steuber, 2022-11-30

config = None
paths = None
build_dirs = {}
additional_bin_dirs = []

def init(config_init, paths_init):
  global config, paths

  config = config_init
  paths = paths_init

def get_config():
  global config
  return config

def get_paths():
  global paths
  return paths

def add_build_dir(lang, name, dir_path):
  global build_dirs
  if lang not in build_dirs:
    build_dirs[lang] = {}
  build_dirs[lang][name] = dir_path

def get_build_dirs(lang):
  global build_dirs
  return build_dirs[lang]

def add_bin_dir(dir_path):
  global additional_bin_dirs
  additional_bin_dirs.append(dir_path)

def get_additional_bin_dirs():
  global additional_bin_dirs
  return additional_bin_dirs
