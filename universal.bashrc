#!/bin/bash
# A cross-platform .bashrc featuring conditional extras intended for Mozilla development and a very
# silly, very heavy prompt. The Windows variant is intended for use with MSYS.

# Sometimes we will want to leave things in the global "namespace", but we won't want to interfere
# with other things that might be similarly named, so we will prefix with `_B_` and hope that that
# is enough.

_B_OS="unknown"
if [[ "$OSTYPE" == "msys" ]]; then
  _B_OS="windows"
elif [[ "$OSTYPE" == "darwin"* ]]; then
  _B_OS="mac"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  _B_OS="linux"
fi

_B_UTIL_DIR="${HOME}/.bytesized_utilites"
_B_UTIL_CONFIG_DIR="${_B_UTIL_DIR}/config"
_B_UTIL_BIN_DIR="${_B_UTIL_DIR}/bin"
_B_UTIL_DATA_DIR="${_B_UTIL_DIR}/data"

_B_MOZILLA="false"
_B_MOZILLA_CONFIG="${_B_UTIL_CONFIG_DIR}/mozilla"
if [[ -f "$_B_MOZILLA_CONFIG" ]]; then
  _B_MOZILLA="true"
fi

export PATH="${PATH}:${HOME}/bin"
export PATH="${PATH}:${_B_UTIL_BIN_DIR}"
if [[ "$_B_OS" == "windows" ]]; then
  export PATH="${PATH}:/c/Program Files/Git/bin"
  if [[ "$_B_MOZILLA" == "true" ]]; then
    export PATH="${PATH}:${HOME}/.cargo/bin"
    export PATH="${PATH}:/c/mozilla-build/Python3/Scripts"
    export PATH="${PATH}:${HOME}/.mozbuild/node/"
  fi
elif [[ "$_B_OS" == "mac" ]]; then
  export PATH="/usr/local/Homebrew/bin:${PATH}"
  export PATH="/usr/local/bin:${PATH}"
  export PATH="${PATH}:/sbin"
  export PATH="${PATH}:/usr/local/sbin"
elif [[ "$_B_OS" == "linux" ]]; then
  export PATH="${PATH}:/sbin"
  export PATH="${PATH}:${HOME}/.local/bin/"
  if [[ "$_B_MOZILLA" == "true" ]]; then
    if [ -f "${HOME}/.cargo/env" ]
    then
      . "${HOME}/.cargo/env"
    fi
  fi
fi

# Filter pwd ('.') out of my PATH. I HATE that. And some environments I've been in seem to just add
# it for you.
export PATH=$(echo "$PATH" | sed 's|:\.:|:|g;s|:\.$||;s|^\.:||')

export LESS="-FMRSXQ"
export GIT_SSH="$(which ssh)"
export EDITOR="vim"
export PAGER="less -R"
if [[ "$_B_OS" == "linux" ]]; then
  if [[ -z "$DISPLAY" ]]; then
    export DISPLAY=":0"
  fi
elif [[ "$_B_OS" == "mac" ]]; then
  export BASH_SILENCE_DEPRECATION_WARNING=1
fi
if [[ "$_B_MOZILLA" == "true" ]]; then
  export MACH_NOTIFY_MINTIME=0
fi

# LESS man page colors (makes Man pages more readable).
export LESS_TERMCAP_mb=$'\E[01;31m'
export LESS_TERMCAP_md=$'\E[01;31m'
export LESS_TERMCAP_me=$'\E[0m'
export LESS_TERMCAP_se=$'\E[0m'
export LESS_TERMCAP_so=$'\E[01;44;33m'
export LESS_TERMCAP_ue=$'\E[0m'
export LESS_TERMCAP_us=$'\E[01;32m'

# Exit if this is not an interactive session
if ! [[ $- == *i* ]]
then
  return
fi

unalias -a

alias bc='bc -lq'
alias ci='vim'  # Not sure what ci is, but I always type it instead of vi and get confused
alias cp='cp -i'
alias cwd='pwd'
alias df='df -Th'
alias du='du -h'
# I have some enviornment variables that are color escape sequences, but I want to see the actual
# value of these variables rather than having them randomly color my env output
alias env="env | sed 's/'$'\E''/\\\\E/'"
alias grep='grep --color=auto -E'
alias ls='ls -h --color=auto'
alias lsb='$(which ls) --color=auto -l'
alias mv='mv -i'
alias vi='vim'

if [[ "$_B_OS" == "windows" ]]; then
  alias clear="python -c \"print '\n'*1000\""
  if [[ "$_B_MOZILLA" == "true" ]]; then
    alias hg="hg.exe"
  fi
elif [[ "$_B_OS" == "linux" ]]; then
  alias helgrind='valgrind --tool=helgrind'
  alias xopen='xdg-open'
elif [[ "$_B_OS" == "mac" ]]; then
  alias fix_audio='sudo killall coreaudiod'
  # Installed via brew install coreutils
  alias shred='gshred -u'
  alias vlc="/Applications/VLC.app/Contents/MacOS/VLC &> /dev/null &"
fi

# This seems to fix some obnoxious problems I sometimes have. Ex:
# open vi, resize terminal window, close vi
# Try to type something long enough that the line should wrap
# Line wraps, but does not move to the next line, typing starts overwriting current line.
# Everything goes haywire until window is resized outside of vi
shopt -s checkwinsize
# I read that these next three lines are necessary otherwise some BASH completions will fail
shopt -s extglob
set +o nounset
shopt -s progcomp

if [[ "$_B_OS" == "linux" ]]; then
  # Displays information about the CPUs and RAM on this machine
  function get_specs {
    # Before we get started, I want to read the data for each logical CPU into an array
    declare -a core_data_array
    local divisions=$(grep -n "^$" /proc/cpuinfo | cut -d ':' -f 1)
    local copy_from=1
    local copy_to=
    local index=0
    while [[ -n "$divisions" ]]
    do
      copy_to=$(echo "$divisions" | sed '1!d')
      divisions=$(echo "$divisions" | sed '1d')
      
      core_data_array[$index]=$(sed "${copy_from},${copy_to}!d" /proc/cpuinfo)
      
      copy_from=$(($copy_to + 1))
      (( index = index + 1 ))
    done
    
    # Get the total number of logical cores and make sure we read the same number of elements into
    # the array
    local total_count=$(grep -E -c "^processor\s+:\s" /proc/cpuinfo)
    if [[ $total_count -ne $index ]]; then
      echo "CPU parsing failed"
      return
    fi
    
    # Get and print the number of physical CPUs (not cores, whole processors)
    local cpu_count=$(grep -E "^physical id\s+: " /proc/cpuinfo | sort -u | wc -l)
    echo "CPU count: ${cpu_count}"
    # Get a list of the CPU ids so we can get the info on each CPU individually
    local cpu_id_list=$(grep -E "^physical id\s+: " /proc/cpuinfo | sort -u | sed -r 's/^physical id[ \t]+: //')
    local which_cpu=1
    while [[ $which_cpu -le $cpu_count ]]
    do
      local cpu_id=$(echo "$cpu_id_list" | sed "${which_cpu}!d")
      
      # Loop through the data for each core. If the core belongs to this cpu, we want to add its
      # core id to the list and get the speed
      local core_speed=""
      local model_name=""
      local core_id_list=
      index=0
      while [[ $index -lt $total_count ]]
      do
        # Only bother with this core if it belongs to the processor in question
        if echo "${core_data_array[$index]}" | grep -E -q "^physical id\s+: ${cpu_id}$"; then
          # We found a core of the correct CPU
          # If we haven't already, get the core speed and model name. This will be done the first
          # pass through each time
          if [[ -z "$core_speed" ]]; then
            core_speed=$(echo "${core_data_array[$index]}" | grep -E '^cpu MHz\s+: ' | sed -r 's/^cpu MHz[ \t]+: //')
            # Convert to Ghz
            core_speed=$(echo "${core_speed} / 1000" | bc -l | awk '{printf "%.1f\n", $1}')
            
            model_name=$(echo "${core_data_array[$index]}" | grep -E '^model name\s+: ' | sed -r 's/^model name\s+: //;s/[ \t]+/ /g')
          fi
          # Add the core id to the list
          local core_id=$(echo "${core_data_array[$index]}" | grep -E '^core id\s+: ' | sed -r 's/^core id[ \t]+: //')
          core_id_list="${core_id_list}${core_id}"$'\n'
        fi
        (( index = index + 1 ))
      done
      local physical_core_count=$(echo -n "$core_id_list" | sort -u | wc -l)
      local logical_core_count=$(echo -n "$core_id_list" | wc -l)
      
      # Output differently depending on whether the cpu has hyperthreading
      if [[ $physical_core_count -eq $logical_core_count ]]; then
        # No logical cores have duplicate id numbers. This CPU has no hyperthreading
        # Just echo a newline rather than printing anything
        echo -e "  CPU $((${cpu_id}+1)):\n    ${model_name}\n    ${core_speed} Ghz\n    ${physical_core_count} cores"
      elif [[ $((${physical_core_count} * 2 )) -eq $logical_core_count ]]
      then
        echo -e "  CPU $((${cpu_id}+1)):\n    ${model_name}\n    ${core_speed} Ghz\n    ${physical_core_count} cores with hyperthreading"
      else
        echo -e "  CPU $((${cpu_id}+1)):\n    ${model_name}\n    ${core_speed} Ghz\n    ${physical_core_count} physical cores\n    ${logical_core_count} logical cores"
      fi
      
      (( which_cpu = which_cpu + 1 ))
    done
    
    # Now let's do some quick ram info
    local total_ram=$(grep -E '^MemTotal:\s+' /proc/meminfo | sed -r 's/^MemTotal:[ \t]+//')
    
    # Make sure the measurement is in kB
    if [[ "$total_ram" =~ kB$ ]]
    then
      local kilobytes=$(echo "$total_ram" | sed -r 's/^[^0-9]*([0-9]+)[^0-9]*$/\1/')
      local megabytes=$(($kilobytes / 1024))
      local gigabytes=$(($megabytes / 1024))
      if [[ $gigabytes -lt 1 ]]; then
        echo "RAM: ${megabytes} MB"
      else
        echo "RAM: ${gigabytes} GB"
      fi
    else
      # If the units are not in kB, just display as is
      echo "RAM: ${total_ram}"
    fi
  }
fi

###
### A few functions for easier navigation using labels
###
# Usage examples:
# > label name1 /etc
# labels the directory /etc as name1
# > goto name1
# cd's to directory labeled name1 (/etc)
# > label name1
# labels pwd as name1
# > label
# labels pwd as nameless
# > goto
# returns to the directory labeled nameless
# > rmlabel name1
# removes label name1
# > rmlabel
# removes label nameless
# > lslabel
# Lists all labels and the directories they label
# > lslabel name*
# Lists all labels starting with name (and their directories)
_B_LABEL_DIR="${_B_UTIL_DATA_DIR}/labels"
if [[ ! -e "${_B_LABEL_DIR}" ]]; then
  mkdir -p "${_B_LABEL_DIR}"
fi
function label {
  local label
  local dir_name
  local response

  if [[ $# -ge 1 ]]; then
    label="$1"; shift
  else
    label="nameless"
  fi
  if [[ $# -eq 1 ]]; then
    dir_name="$1"; shift
  else
    dir_name="$(pwd)"
  fi
  dir_name="$(brealpath "$dir_name")"
  if [[ $# -ne 0 ]]; then
    echo "Usage: label [label-name] [directory]"
    echo -e "\tdirectory defaults to pwd"
    echo -e "\twith no arguments, label-name defaults to nameless"
    return
  fi
  # Make sure the proposed label is a valid filename
  if [[ "$label" == "" || "$label" == "." || "$label" == ".." ]] || !  echo "$label" | grep -q "^[a-zA-Z0-9_.]*$"
  then
    echo "Label names must follow these rules:"
    echo -e "\tCannot be empty (\"\")"
    echo -e "\tCannot be \".\" or \"..\""
    echo -e "\tMay only contain the following characters:"
    echo -e "\t\tLetters"
    echo -e "\t\tNumbers"
    echo -e "\t\tUnderscores (\"_\")"
    echo -e "\t\tPeriods (\".\")"
    return
  fi

  echo -n "$dir_name" > "${_B_LABEL_DIR}/${label}"
}
function rmlabel {
  local label
  
  if [[ $# -ge 1 ]]
  then
    label="$1"; shift
  else
    label="nameless"
  fi
  
  while [[ -n "$label" ]]
  do
    # Make sure the proposed label is a valid filename
    if [[ "$label" == "" || "$label" == "." || "$label" == ".." ]] || ! echo "$label" | grep -q "^[-a-zA-Z0-9_.]*$"
    then
      echo "Label \"$label\" is not a valid filename"
      continue
    fi
    
    # Make sure the label exists
    if [[ ! -f "${_B_LABEL_DIR}/${label}" ]]; then
      echo "No label named \"${label}\""
      continue
    fi
    
    # Remove the label
    rm "${_B_LABEL_DIR}/${label}"
    
    # Get the next label before we loop
    label="$1"; shift
  done
}
function lslabel {
  local output
  local labels
  local oldpwd=$(pwd)
  
  cd "$_B_LABEL_DIR"
  
  labels=$(ls $@ 2>/dev/null)
  
  first_line="True"
  output=""
  for label in $labels
  do
    if [[ -n "$first_line" ]]; then
      first_line=""
    else
      output+=$'\n'
    fi
    output+="${label}"
    output+=$':\t'
    output+="$(cat "${label}" 2>/dev/null)"
  done

  echo -n "$output" | bcols $'\t'
  
  cd "$oldpwd"
}
function goto {
  local label
  local dir
  
  if [[ $# -ge 1 ]]
  then
    label="$1"
    shift
  else
    label="nameless"
  fi
  
  if [[ $# -ne 0 ]]
  then
    echo "Usage: goto [label-name]"
    return
  fi
  
  # Make sure the proposed label is a valid filename
  if [[ "$label" == "" || "$label" == "." || "$label" == ".." ]] || !  echo "$label" | grep -q "^[-a-zA-Z0-9_.]*$"
  then
    echo "Invalid label name"
    return
  fi

  if [[ ! -f "${_B_LABEL_DIR}/${label}" ]]
  then
    echo "Label does not exist"
    return
  fi

  dest=$(cat "${_B_LABEL_DIR}/${label}")
  cd "${dest}"
}
# I also want bash completion of label names
# Note to self: compgen = completion generation
function _label_compgen {
  local cur
  cur=${COMP_WORDS[COMP_CWORD]}
  # Return a list of basenames for files in the _B_LABEL_DIR
  COMPREPLY=( $(compgen -W "$(for file in $(ls ${_B_LABEL_DIR} 2>/dev/null); do echo $(basename "$file"); done)" -- $cur ) )
  return 0
}
# Complete rmlabel, lslabel and goto with names from _label_compgen
complete -F _label_compgen rmlabel lslabel goto
# label takes a directory as its second argument. Including the -d allows completions to directory names in addition to names from _label_compgen
complete -d -F _label_compgen label

if [[ "$_B_OS" == "mac" ]]; then
  # Normal Colors
  BLACK=$(tput setaf 0)
  RED=$(tput setaf 1)
  GREEN=$(tput setaf 2)
  YELLOW=$(tput setaf 3)
  BLUE=$(tput setaf 4)
  PURPLE=$(tput setaf 5)
  CYAN=$(tput setaf 6)
  WHITE=$(tput setaf 7)

  # Bold
  BOLD_BLACK=$(tput bold; tput setaf 0)
  BOLD_RED=$(tput bold; tput setaf 1)
  BOLD_GREEN=$(tput bold; tput setaf 2)
  BOLD_YELLOW=$(tput bold; tput setaf 3)
  BOLD_BLUE=$(tput bold; tput setaf 4)
  BOLD_PURPLE=$(tput bold; tput setaf 5)
  BOLD_CYAN=$(tput bold; tput setaf 6)
  BOLD_WHITE=$(tput bold; tput setaf 7)

  # Background
  ON_BLACK=$(tput setaf 0)
  ON_RED=$(tput setaf 1)
  ON_GREEN=$(tput setaf 2)
  ON_YELLOW=$(tput setaf 3)
  ON_BLUE=$(tput setaf 4)
  ON_PURPLE=$(tput setaf 5)
  ON_CYAN=$(tput setaf 6)
  ON_WHITE=$(tput setaf 7)

  # Color Reset
  NC=$(tput sgr0)
  # Especially attention-grabbing color combination
  ALERT=${BOLD_WHITE}${ON_RED}
else
  # Normal Colors
  BLACK='\e[0;30m'
  RED='\e[0;31m'
  GREEN='\e[0;32m'
  YELLOW='\e[0;33m'
  BLUE='\e[0;34m'
  PURPLE='\e[0;35m'
  CYAN='\e[0;36m'
  WHITE='\e[0;37m'
  
  # Bold
  BOLD_BLACK='\e[1;30m'
  BOLD_RED='\e[1;31m'
  BOLD_GREEN='\e[1;32m'
  BOLD_YELLOW='\e[1;33m'
  BOLD_BLUE='\e[1;34m'
  BOLD_PURPLE='\e[1;35m'
  BOLD_CYAN='\e[1;36m'
  BOLD_WHITE='\e[1;37m'
  
  # Background
  ON_BLACK='\e[40m'
  ON_RED='\e[41m'
  ON_GREEN='\e[42m'
  ON_YELLOW='\e[43m'
  ON_BLUE='\e[44m'
  ON_PURPLE='\e[45m'
  ON_CYAN='\e[46m'
  ON_WHITE='\e[47m'
  
  # Color Reset
  NC="\e[m"
  # Especially attention-grabbing color combination
  ALERT=${BOLD_WHITE}${ON_RED}
fi

if [[ -n "${SSH_CONNECTION}" ]]; then
  CONNECTION_COLOR="${GREEN}"
elif [[ "$_B_OS" == "linux" && "${DISPLAY%%:0*}" != "" ]]; then
  # Above uses BASH parameter expansion to remove trailing ":0"* from $DISPLAY
  CONNECTION_COLOR="${ALERT}"
else
  CONNECTION_COLOR="${BOLD_CYAN}"
fi

if [[ ${USER} == "root" ]]; then
    USER_COLOR="${ALERT}"
elif [[ ${USER} != $(logname 2>/dev/null) ]]; then
    USER_COLOR=${BOLD_RED}
else
    USER_COLOR=${BOLD_CYAN}
fi

function disk_color() {
  if ! which df &> /dev/null; then
    echo -en "${BOLD_PURPLE}" 
    return
  fi
  if [[ ! -w "${PWD}" ]] ; then
    # No 'write' privilege in the current directory.
    echo -en "${RED}"
  elif [[ -s "${PWD}" || "$_B_OS" == "windows" ]] ; then
    local used=$(df "$PWD" | grep -Eo '[0-9]+%' | sed 's|%||')
    if [[ ${used} -gt 95 ]]; then
      # Disk almost full (>95%).
      echo -en "${ALERT}"
    elif [[ ${used} -gt 90 ]]; then
      # Free disk space almost gone.
      echo -en "${BOLD_RED}"
    else
      # Free disk space is ok.
      echo -en "${GREEN}"
    fi
  else
    # Current directory is size '0' (like /proc, /sys etc).
    echo -en "${BOLD_WHITE}"
  fi
}

function pre_prompt {
  if [[ "$_B_OS" != "linux" ]]; then
    history -a
  fi

  _B_USER=$(whoami | sed 's|^.*\\||')
  local hg_summary="$(hg summary 2>/dev/null)"
  local git_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
  unset info_bar_array
  unset info_color_array
  local info_array_size
  local info_bar_trim_start
  local info_color_array
  local info_bar_array
  if [[ -z "$hg_summary" ]]
  then
    if [[ -z "$git_branch" ]]
    then
      info_bar_trim_start="True"
      info_color_array[$info_array_size]="${GREEN}"
      info_bar_array[$info_array_size]="$(pwd)"
      (( info_array_size = info_array_size + 1 ))
    else
      info_bar_trim_start="False"
      info_color_array[$info_array_size]="${GREEN}"
      info_bar_array[$info_array_size]="branch: "
      (( info_array_size = info_array_size + 1 ))
      info_color_array[$info_array_size]="${BOLD_CYAN}"
      info_bar_array[$info_array_size]="${git_branch}"
      (( info_array_size = info_array_size + 1 ))
    fi
  else
    local hg_branch="$(echo "$hg_summary" | grep '^branch: ' | sed 's|^branch: ||')"

    info_bar_trim_start="False"
    info_color_array[$info_array_size]="${GREEN}"
    info_bar_array[$info_array_size]="branch: "
    (( info_array_size = info_array_size + 1 ))
    info_color_array[$info_array_size]="${BOLD_CYAN}"
    info_bar_array[$info_array_size]="${hg_branch} "
    (( info_array_size = info_array_size + 1 ))

    local active_bookmark="$(echo "$hg_summary" | grep '^bookmarks: ' | grep '\*' | sed 's|^[^*]*\*\(\S*\).*$|\1|')"
    local hg_parents="$(hg parents)"
    local bookmarks="$(echo "$hg_parents" | grep '^bookmark:' | sed 's|^bookmark:\s*\(\S*\)\s*$|\1|')"
    local fxtree="$(echo "$hg_parents" | grep '^fxtree:' | sed 's|^fxtree:\s*\(\S*\)\s*$|\1|')"
    local changeset="$(echo "$hg_parents" | grep '^changeset:' | sed 's|^changeset:\s*\([0-9]*\):.*$|\1|')"

    if [[ -n "$fxtree" ]]
    then
      info_color_array[$info_array_size]="${GREEN}"
      info_bar_array[$info_array_size]="fxtree:"
      (( info_array_size = info_array_size + 1 ))
      while read -r line
      do
        info_color_array[$info_array_size]="${BOLD_CYAN}"
        info_bar_array[$info_array_size]=" ${line}"
        (( info_array_size = info_array_size + 1 ))
      done <<< "$fxtree"

    elif [[ -n "$bookmarks" ]]
    then
      info_color_array[$info_array_size]="${GREEN}"
      info_bar_array[$info_array_size]="bookmark:"
      (( info_array_size = info_array_size + 1 ))
      local bookmark
      while read -r bookmark
      do
        if [[ "$active_bookmark" = "$bookmark" ]]
        then
          # I don't like active bookmarks. I want my bookmarks to stay where I
          # freaking put them. If we have an active bookmark, deactivate it.
          hg bookmark -i
        fi
        info_color_array[$info_array_size]="${BOLD_CYAN}"
        info_bar_array[$info_array_size]=" ${bookmark}"
        (( info_array_size = info_array_size + 1 ))
      done <<< "$bookmarks"
    else
      info_color_array[$info_array_size]="${GREEN}"
      info_bar_array[$info_array_size]="changeset: "
      (( info_array_size = info_array_size + 1 ))
      info_color_array[$info_array_size]="${BOLD_CYAN}"
      info_bar_array[$info_array_size]="$changeset"
      (( info_array_size = info_array_size + 1 ))
    fi
  fi

  # Generate colorless info bar so we know its length
  _B_INFO_BAR=""
  local info_bar_index=0
  while [[ "$info_bar_index" -lt "$info_array_size" ]]
  do
    _B_INFO_BAR="${_B_INFO_BAR}${info_bar_array[$info_bar_index]}"
    (( info_bar_index = info_bar_index + 1 ))
  done

  _B_HOST=$(echo -n $HOSTNAME | sed -e "s|[\.].*$||")

  # Determine the number of characters in the prompt 
  local prompt_size=$(echo -n "..(${_B_USER}@${_B_HOST})..().." | wc -c | tr -d " ")
  local info_bar_size=$(echo -n "${_B_INFO_BAR}" | wc -c | tr -d " ")

  # Determine the space remaining on the screen to be filled
  if [ -z "${COLUMNS}" ]
  then
    local chars_left=$(( 80 - ${prompt_size} ))
  else
    local chars_left=$(( ${COLUMNS} - ${prompt_size} ))
  fi

  if [[ "$info_bar_size" -gt "$chars_left" ]]
  then
    # Reserve space for the '...'
    (( chars_left = chars_left - 3 ))
  fi
  _B_INFO_BAR=""
  if [[ "$chars_left" -gt "0" ]]
  then
    if [[ "$info_bar_trim_start" = "True" ]]
    then
      # The beginning of the info bar may be trimmed
      info_bar_index=$(( $info_array_size - 1 ))
      while [[ "$info_bar_index" -ge "0" ]]
      do
        local text_color="${info_color_array[$info_bar_index]}"
        local text_segment="${info_bar_array[$info_bar_index]}"
        if [[ "$chars_left" -eq "0" ]]
        then
          text_segment="..."
        elif [[ "${#text_segment}" -gt "$chars_left" ]]
        then
          chars_to_skip=$(( ${#text_segment} - $chars_left ))
          text_segment="...${text_segment:$chars_to_skip:$chars_left}"
        fi
        _B_INFO_BAR="${text_color}${text_segment}${_B_INFO_BAR}"
        chars_left=$(( ${chars_left} - ${#text_segment} ))
        if [[ "$chars_left" -lt "0" ]]
        then
          # Strictly less than 0, because == 0 means we did not add the '...'
          break
        fi
        (( info_bar_index = info_bar_index - 1 ))
      done
    else
      # The end of the info bar may be trimmed
      info_bar_index=0
      while [[ "$info_bar_index" -lt "$info_array_size" ]]
      do
        text_color="${info_color_array[$info_bar_index]}"
        text_segment="${info_bar_array[$info_bar_index]}"
        if [[ "$chars_left" -eq "0" ]]
        then
          text_segment="..."
        elif [[ "${#text_segment}" -gt "$chars_left" ]]
        then
          text_segment="${text_segment:0:$chars_left}..."
        fi
        _B_INFO_BAR="${_B_INFO_BAR}${text_color}${text_segment}"
        chars_left=$(( ${chars_left} - ${#text_segment} ))
        if [[ "$chars_left" -lt "0" ]]
        then
          # Strictly less than 0, because == 0 means we did not add the '...'
          break
        fi
        (( info_bar_index = info_bar_index + 1 ))
      done
    fi
  fi
  _B_INFO_BAR="$(echo -en "$_B_INFO_BAR")"

  # While there is space remaining, add more characters to the fill variable
  _B_PROMPT_FILL=""
  while [[ "$chars_left" -gt "0" ]]
  do
    _B_PROMPT_FILL="${_B_PROMPT_FILL}─"
    (( chars_left = chars_left - 1 ))
  done
}
PROMPT_COMMAND="pre_prompt"
PS1=$"\[${NC}\]\n"
# Leading filler
PS1="${PS1}\[${BOLD_BLUE}\]┌─(\[${NC}\]"
# Username and host
PS1="${PS1}\[${USER_COLOR}\]\${_B_USER}\[${NC}\]\[${YELLOW}\]@\[${NC}\]\[${GREEN}\]\${_B_HOST}\[${NC}\]"
# Filler
PS1="${PS1}\[${BOLD_BLUE}\])─\${_B_PROMPT_FILL}─(\[${NC}\]"
# Infobar
PS1="${PS1}\${_B_INFO_BAR}\[${NC}\]"
# Trailing Filler and newline
PS1="${PS1}\[${BOLD_BLUE}\])──\[${NC}\]\n"
# Current directory and prompt
PS1="${PS1}\[${BOLD_BLUE}\]└─[\[${NC}\]\[\$(disk_color)\]\W\[${NC}\]\[${BOLD_BLUE}\]] > \[${NC}\]"

# Output the specs of the machine to stdout
if [[ "$_B_OS" == "linux" ]]; then
  echo -e "${BOLD_BLUE}$(get_specs)${NC}"
fi
