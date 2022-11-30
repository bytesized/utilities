#!/usr/bin/env python3
# Kirk Steuber, 2022-11-30

config = None
paths = None

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
