#!/usr/bin/env python3
import os
import tempfile

from . import cygpath, global_vars

BASH_SHEBANG = "#!/bin/bash\n"
LOADER_UUID = "b52960a2-e8ed-4833-a86f-9aa7b401a557"
LOADER_START_SENTINEL = f"# >>> BYTESIZED BASHRC LOADER START({LOADER_UUID}) >>>\n"
LOADER_END_SENTINEL = f"# <<< BYTESIZED BASHRC LOADER END({LOADER_UUID}) <<<\n"

LOADER_CODE = """
# Do not tamper with this code or the surrounding sentinels.
# To remove this, it is best to run the bytesized utilities uninstaller.
# For more info, see: https://github.com/bytesized/utilities
if [[ -r "__BASHRC_PATH__" && "$_B_BASHRC_LOADED" != "true" ]]
then
  . "__BASHRC_PATH__"
fi
""".strip() + "\n"

BASH_REPO_PATH_VAR_NAME = "_B_UTIL_REPO_PATH"
PATH_REPLACEMENT_SIGIL = "__PATH_ADDITION__"
PATH_ADD_CODE = f'export PATH="${{PATH}}:{PATH_REPLACEMENT_SIGIL}"'
PYTHON_LIB_PATH_ADD_CODE_SUBSEQUENT = \
  f'export PYTHONPATH="${{PYTHONPATH}}:{PATH_REPLACEMENT_SIGIL}"'
# We are probably safe just assuming that the PATH variable is already set, but PYTHONPATH often
# is not.
PYTHON_LIB_PATH_ADD_CODE_FIRST = f"""
if [[ -z "$PYTHONPATH" ]]
then
  export PYTHONPATH="{PATH_REPLACEMENT_SIGIL}"
else
  {PYTHON_LIB_PATH_ADD_CODE_SUBSEQUENT}
fi
""".strip()

class BadFileContents(Exception):
  """
    Raised if we try to parse a file and the contents are inconsistent (ex: mismatched sentinels).
    """
  pass

def get_bash_path_string(path):
  path = cygpath.to_unix_path(path)

  # TODO: Actual escaping
  assert "\"" not in path
  assert "$" not in path

  return path

def get_bash_var_based_path_string(path, var_dict):
  path = cygpath.to_unix_path(path)

  # TODO: Actual escaping
  assert "\"" not in path
  assert "$" not in path

  var_name = None
  var_value = None
  for current_var_name, current_var_value in var_dict.items():
    if path.startswith(current_var_value):
      var_name = current_var_name
      var_value = current_var_value
      break
  else:
    return path

  path = "${" + var_name + "}" + path[len(var_value):]
  return path

def configure():
  config = global_vars.get_config()
  paths = global_vars.get_paths()

  # It doesn't seem to be entirely consistent whether the configuration is loaded from `.bashrc` or
  # `.bash_profile`. We are going to add the loader to both of them and just have the loader make
  # sure that it isn't loading the script twice.
  load_target = os.path.join(paths["source"]["config"], "universal.bashrc")
  to_modify = os.path.join(paths["user"]["home"], ".bashrc")
  update_loader_in_script(to_modify, load_target, config["uninstall"])
  to_modify = os.path.join(paths["user"]["home"], ".bash_profile")
  update_loader_in_script(to_modify, load_target, config["uninstall"])

  additional_bashrc_path = os.path.join(paths["user"]["config"], "additional.bashrc")
  additional_bashrc_contents = BASH_SHEBANG
  additional_bashrc_contents += "\n"

  repo_path = get_bash_path_string(paths["source"]["root"])
  additional_bashrc_contents += f"export {BASH_REPO_PATH_VAR_NAME}=\"{repo_path}\"\n"

  var_dict = {
    BASH_REPO_PATH_VAR_NAME: repo_path,
    # This is defined in `universal.bashrc`
    "_B_UTIL_DIR": cygpath.to_unix_path(paths["user"]["root"]),
  }

  python_script_path = get_bash_var_based_path_string(paths["source"]["bin"]["python"], var_dict)
  additional_bashrc_contents += PATH_ADD_CODE.replace(PATH_REPLACEMENT_SIGIL, python_script_path)
  additional_bashrc_contents += "\n"
  for dir_path in global_vars.get_additional_bin_dirs():
    dir_path = get_bash_var_based_path_string(dir_path, var_dict)
    additional_bashrc_contents += PATH_ADD_CODE.replace(PATH_REPLACEMENT_SIGIL, dir_path)
    additional_bashrc_contents += "\n"

  python_source_lib_path = \
    get_bash_var_based_path_string(paths["source"]["lib"]["python"], var_dict)
  additional_bashrc_contents += \
    PYTHON_LIB_PATH_ADD_CODE_FIRST.replace(PATH_REPLACEMENT_SIGIL, python_source_lib_path)
  additional_bashrc_contents += "\n"
  python_user_lib_path = get_bash_var_based_path_string(paths["user"]["lib"]["python"], var_dict)
  additional_bashrc_contents += \
    PYTHON_LIB_PATH_ADD_CODE_SUBSEQUENT.replace(PATH_REPLACEMENT_SIGIL, python_user_lib_path)
  additional_bashrc_contents += "\n"

  with open(additional_bashrc_path, "w") as f:
    f.write(additional_bashrc_contents)

def update_loader_in_script(script_path, load_target, remove_loader):
  """
    If the script located at `script_path` doesn't already have the loader code, it is added. If it
    does have it, the code is updated. If `remove_loader` is true, the code is removed.
    """
  loader_code = LOADER_CODE.replace("__BASHRC_PATH__", load_target)

  old_loader_found = False
  # Sometimes we want to know if the previous line was empty. If we are at the start of the file,
  # count it as the previous line being empty.
  last_line = "\n"
  try:
    with open(script_path) as orig_file:
      with tempfile.NamedTemporaryFile(mode = "w", delete = False) as temp_file:
        temp_path = temp_file.name
        in_marked_section = False
        just_wrote_loader = False
        for line in orig_file:

          if line == LOADER_START_SENTINEL:
            if in_marked_section:
              raise BadFileContents("Found a start sentinel without an end sentinel")
            in_marked_section = True
            if not old_loader_found and not remove_loader:
              # Add an extra line before the loader if there isn't one already.
              if last_line != "\n":
                temp_file.write("\n")
              temp_file.write(LOADER_START_SENTINEL)
              temp_file.write(loader_code)
              temp_file.write(LOADER_END_SENTINEL)
              just_wrote_loader = True
            old_loader_found = True

          if not in_marked_section:
            # Add an extra line after the loader if there isn't one already.
            if just_wrote_loader and line != "\n":
              temp_file.write("\n")
            temp_file.write(line)

            just_wrote_loader = False

          if line == LOADER_END_SENTINEL:
            if not in_marked_section:
              raise BadFileContents("Found an end sentinel without a start sentinel")
            in_marked_section = False

          last_line = line

        if in_marked_section:
          raise BadFileContents("Found a start sentinel without an end sentinel")
  except FileNotFoundError:
    if not remove_loader:
      with open(script_path, "w") as f:
        f.write(BASH_SHEBANG)
        f.write("\n")
        f.write(LOADER_START_SENTINEL)
        f.write(loader_code)
        f.write(LOADER_END_SENTINEL)
    return

  if old_loader_found:
    # Overwrite the file with the temp file.
    os.remove(script_path)
    os.rename(temp_path, script_path)
  else:
    # There was no loader to update. Just add it to the end of the script.
    os.remove(temp_path)
    if not remove_loader:
      with open(script_path, "a") as f:
        if not last_line.endswith("\n"):
          f.write("\n\n")
        elif last_line != "\n":
          f.write("\n")
        f.write(LOADER_START_SENTINEL)
        f.write(loader_code)
        f.write(LOADER_END_SENTINEL)
