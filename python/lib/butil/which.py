#!/usr/bin/env python3
import os
from shutil import which as shutil_which
import sys

# Shamelessly stolen from:
# https://searchfox.org/mozilla-central/rev/4496b3ed9bb535832e4826f09fbcb645b559a32d/testing/mozbase/mozfile/mozfile/mozfile.py#454
def which(command, mode = os.F_OK | os.X_OK, path = None, file_extensions = None, extra_search_dirs = ()):
  """
  A wrapper around `shutil.which` to make the behavior on Windows consistent with other platforms.

  On non-Windows platforms, this is a direct call to `shutil.which`. On Windows, this:

  * Ensures that `command` without an extension will be found. Previously it was only found if it
    had an extension in `PATHEXT`.
  * Ensures the absolute path to the binary is returned. Previously if the binary was found in
    `cwd`, a relative path was returned.
  * Checks the Windows registry if shutil.which doesn't come up with anything.

  The arguments are the same as the ones in `shutil.which`. In addition there is a 
  `file_extensions` argument that only has an effect on Windows. This is used to set a custom value
  for PATHEXT and is formatted as a list of file extensions.

  extra_search_dirs is a convenience argument. If provided, the strings in the sequence will be
  appended to the END of the given `path`.
  """

  if isinstance(path, (list, tuple)):
    path = os.pathsep.join(path)

  if not path:
    path = os.environ.get("PATH", os.defpath)

  if extra_search_dirs:
    path = os.pathsep.join([path] + list(extra_search_dirs))

  if sys.platform != "win32":
    return shutil_which(command, mode=mode, path=path)

  env_file_extensions = os.environ.get("PATHEXT", "")
  if not file_extensions:
    file_extensions = env_file_extensions.split(os.pathsep)

  # This ensures that `command` without any extensions will be found.
  # See: https://bugs.python.org/issue31405
  if "." not in file_extensions:
    file_extensions.append(".")

  os.environ["PATHEXT"] = os.pathsep.join(file_extensions)
  try:
    path = shutil_which(command, mode=mode, path=path)
    if path:
      return os.path.abspath(path.rstrip("."))
  finally:
    if env_file_extensions:
      os.environ["PATHEXT"] = env_file_extensions
    else:
      del os.environ["PATHEXT"]

  # If we've gotten this far, we need to check for registered executables before giving up.
  try:
    import winreg
  except ImportError:
    import _winreg as winreg
  if not command.lower().endswith(".exe"):
    command += ".exe"
  try:
    ret = winreg.QueryValue(
      winreg.HKEY_LOCAL_MACHINE,
      f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{command}",
    )
    return os.path.abspath(ret) if ret else None
  except winreg.error:
    return None
