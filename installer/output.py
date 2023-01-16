#!/usr/bin/env python3
# Kirk Steuber, 2023-01-16
from . import global_vars

def output(*args):
  config = global_vars.get_config()

  if not config["quiet"]:
    print(*args)
