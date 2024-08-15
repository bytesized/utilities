#!/usr/bin/env python3
import argparse
from collections import namedtuple
import json
import os
import shutil
import stat
import sys

from . import bashrc, external_repos, global_vars, mozilla, python_deps, rust
from .output import output

def force_remove_dir(dir_path):
  already_fixed = set()
  while True:
    try:
      shutil.rmtree(dir_path)
    except FileNotFoundError:
      pass
    except PermissionError as ex:
      if ex.filename in already_fixed:
        raise ex
      os.chmod(ex.filename, stat.S_IWRITE)
      already_fixed.add(ex.filename)
      continue
    break

def create_dirs_recursive(p):
  for value in p.values():
    if isinstance(value, dict):
      create_dirs_recursive(value)
    else:
      os.makedirs(value, exist_ok = True)

paths = {}
paths["user"] = {}
paths["user"]["home"] = os.path.expanduser("~")
paths["user"]["root"] = os.path.join(paths["user"]["home"], ".bytesized_utilites")
paths["user"]["config"] = os.path.join(paths["user"]["root"], "config")
paths["user"]["data"] = os.path.join(paths["user"]["root"], "data")
paths["user"]["repos"] = os.path.join(paths["user"]["root"], "repos")
paths["user"]["lib"] = {}
paths["user"]["lib"]["root"] = os.path.join(paths["user"]["root"], "lib")
paths["user"]["lib"]["python"] = os.path.join(paths["user"]["lib"]["root"], "python")

paths["source"] = {}
paths["source"]["root"] = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
paths["source"]["config"] = os.path.join(paths["source"]["root"], "config")
paths["source"]["bin"] = {}
paths["source"]["bin"]["python"] = os.path.join(paths["source"]["root"], "python", "bin")
paths["source"]["lib"] = {}
paths["source"]["lib"]["python"] = os.path.join(paths["source"]["root"], "python", "lib")

paths["system"] = {}
if os.name == "nt":
  paths["system"]["cygpath"] = shutil.which("cygpath")
paths["system"]["cargo"] = shutil.which("cargo")
paths["system"]["git"] = shutil.which("git")

install_config_path = os.path.join(paths["user"]["config"], "install.json")

# - `default` should be the default value. It will not be validated or parsed, so it should already
#   be a valid value.
# - `arg_parser` should be a function suitable to be passed in as the `type` argument to
#   `argparse.ArgumentParser.add_argument`.
# - `validator` should be a function that takes a candidate value and either returns the validated
#   value, or raises a `ValueError` if the value is invalid.
# - `options` should be a list of strings describing the option names used to set the config value.
# - `metavar` should be the value that ought to be passed as the `metavar` argument of
#   `argparse.ArgumentParser.add_argument`, or `None` if not applicable.
# - `help` should be the help string passed to `argparse.ArgumentParser.add_argument`. It may
#   contain the string `%DEFAULT_VALUE%`, which will be replaced by the value that will be used if
#   another is not specified (either `ConfigValue.default` or the value read from the install
#   config file).
# - `var_name` should be the resulting name that the config value will have in the `argparse`
#   namespace.
ConfigValue = namedtuple(
  "ConfigValue",
  ["default", "arg_parser", "validator", "options", "metavar", "help", "var_name"]
)

def bool_arg_parser(string):
  clean_string = string.lower().strip()
  if clean_string in ["true", "t", "yes", "y", "1"]:
    return True
  if clean_string in ["false", "f", "no", "n", "0"]:
    return False
  raise argparse.ArgumentTypeError(
    f"'{string}' could not be parsed to a boolean value (use 'true'/'false')"
  )

def bool_validator(b):
  if isinstance(b, bool):
    return b
  raise ValueError

config_options = {
  "mozilla": ConfigValue(
    default = False,
    arg_parser = bool_arg_parser,
    validator = bool_validator,
    options = ["--mozilla"],
    metavar = "BOOL",
    help = "Whether or not to add extra Mozilla-specific configuration "
           "(default = %DEFAULT_VALUE%)",
    var_name = "mozilla",
  ),
  "build": ConfigValue(
    default = True,
    arg_parser = bool_arg_parser,
    validator = bool_validator,
    options = ["--build"],
    metavar = "BOOL",
    help = "Whether or not to build utilities that require being built "
           "(default = %DEFAULT_VALUE%)",
    var_name = "build",
  ),
  "configure": ConfigValue(
    default = True,
    arg_parser = bool_arg_parser,
    validator = bool_validator,
    options = ["--config"],
    metavar = "BOOL",
    help = "Whether or not to install configuration files "
           "(default = %DEFAULT_VALUE%)",
    var_name = "config",
  ),
  "python": ConfigValue(
    default = True,
    arg_parser = bool_arg_parser,
    validator = bool_validator,
    options = ["--python"],
    metavar = "BOOL",
    help = "Whether or not to download and install the Python packages that some of these "
           "utilities depend on "
           "(default = %DEFAULT_VALUE%)",
    var_name = "python",
  ),
}

# Read the JSON install config which will be used as the default values to hand to `argparse`.
# We will then take whatever `argparse` returns and write it back to the JSON file. By doing this,
# the options to this script only need to be specified the first time. 
json_config = None
try:
  with open(install_config_path) as f:
    json_config = json.load(f)
except FileNotFoundError:
  pass
except Exception as e:
  print(
    f"Warning! Unable to read configuration data for an unexpected reason, so default values will"
    f"be used.\n{e}\n",
    file = sys.stderr
  )

parser = argparse.ArgumentParser(
  description = "Builds utilities and installs configuration files. Note that the options below "
                "default to the values that were given the last time that this script was run."
)
parser.add_argument("--uninstall", "-u", action = "store_true",
                    help = "If this is specified, this script uninstalls instead of installing")
parser.add_argument("--leave-config", "-L", action = "store_true",
                    help = "Only relevant if --uninstall is specified. Prevents configuration and "
                           "data from being cleaned up during the uninstall.")
parser.add_argument("--quiet", "-q", action = "store_true",
                    help = "Whether or not to output status text")

for config_value in config_options:
  default = config_options[config_value].default
  arg_parser = config_options[config_value].arg_parser
  validator = config_options[config_value].validator
  options = config_options[config_value].options
  metavar = config_options[config_value].metavar
  help_string = config_options[config_value].help
  var_name = config_options[config_value].var_name

  if json_config and config_value in json_config:
    try:
      default = validator(json_config[config_value])
    except ValueError:
      print(
        f"Warning! Invalid configuration value for '{config_value}'. Using the default.",
        file = sys.stderr
      )

  help_string = help_string.replace("%DEFAULT_VALUE%", str(default))

  parser.add_argument(*options, type = arg_parser, default = default, metavar = metavar,
                      dest = var_name, help = help_string)
args = parser.parse_args()

args_dict = vars(args)
config = {}
for config_value in config_options:
  var_name = config_options[config_value].var_name
  config[config_value] = args_dict[var_name]

if not args.uninstall:
  # Don't create all the directories until after we run `argparse`. It sucks to throw an error even
  # when showing the help text.
  create_dirs_recursive(paths["user"])

  # Some additional validation that shouldn't be necessary if we are uninstalling.
  if os.name == "nt" and paths["system"]["cygpath"] is None:
    print("Error: Cannot find 'cygpath' in PATH.", file = sys.stderr)
    sys.exit(1)
  if config["build"]:
    if paths["system"]["cargo"] is None:
      print("Error: Cannot find 'cargo' in PATH.", file = sys.stderr)
      sys.exit(1)
    if paths["system"]["git"] is None:
      print("Error: Cannot find 'git' in PATH.", file = sys.stderr)
      sys.exit(1)

  with open(install_config_path, "w") as f:
    json.dump(config, f)

# Extra options that are not part of `config_options` are added into the config only after we save
# it to the disk.
config["uninstall"] = args.uninstall
config["quiet"] = args.quiet
config["leave-config"] = args.leave_config

global_vars.init(config, paths)

if config["build"] and not config["uninstall"]:
  output("=== Build Stage Start")

  output("== Fetching Code Start")
  external_repos.fetch()
  output("== Fetching Code Complete\n")

  output("== Build Rust Start")
  rust.build()
  output("== Build Rust Complete")

  output("=== Build Stage Complete\n")

# This both configures on install and "un-configures" on uninstall.
if config["configure"]:
  output("=== Configure Stage Start")

  output("Configuring Mozilla...")
  mozilla.configure()

  output("Configuring bashrc...")
  bashrc.configure()

  output("=== Configure Stage Complete\n")

if config["python"] and not config["uninstall"]:
  output("=== Python Stage Start")

  # The uninstallation for this will be handled in the cleanup stage below since we install into
  # `paths["user"]["lib"]["python"]`
  output("Installing Python dependencies...")
  python_deps.install();

  output("=== Python Stage Complete\n")


if config["uninstall"]:
  output("=== Cleanup Start")

  if config["leave-config"]:
    output(f'Removing "{paths["user"]["repos"]}"...')
    force_remove_dir(paths["user"]["repos"])
    output(f'Removing "{paths["user"]["lib"]["root"]}"...')
    force_remove_dir(paths["user"]["lib"]["root"])
  else:
    output(f'Removing "{paths["user"]["root"]}"...')
    force_remove_dir(paths["user"]["root"])

  output("=== Cleanup Complete\n")

if config["uninstall"]:
  output("Uninstall Complete")
else:
  output("Installation Complete")
