These are some simple utilities I have written. Perhaps they will be helpful to you. Many of these utilities depend on **Python 3**. If you do not already have it installed, you should do so. The installer can be found [here](https://www.python.org/downloads/).

All of my utilities have help pages accessible with the `-h` or `--help` option.

I have done my best to make my utilities compatible with modern versions of Linux, Windows, and OSX. I cannot, however, make any guarantees about their compatibility or functionality. I have also done my best to make them run as expected and to prevent them from causing unexpected side effects, but ultimately you choose to use them at your own risk.

# Utilities

## BASH

* **universal.bashrc**: This `.bashrc` file should be usable across operating systems. It features an unnecessarily heavy, full-color prompt.

## Python

The Python utilities lack standard Python file extensions. But because they each contain a Python shebang, they should execute properly without having to explicitly invoke the Python executable.

* **bcols**: Formats delimited data so that it displays in columns.
* **brealpath**: Return the canonical path of the specified filename, eliminating any symbolic links encountered in the path. This utility mostly exists because `realpath` doesn't exist on macOS for some dumb reason.
* **clearclipboard**: Very simple utility that takes no arguments and empties the clipboard. Tested on Windows 10 and Ubuntu.
* **colorchooser**: Helper for choosing a terminal color scheme and generating the ANSI escape code to produce that color scheme. Can output a static color chart, enter an interactive style chooser, or generate an ANSI escape sequence based on style information passed as arguments. Tested on OSX and Windows 10.
* **digest**: Computes the digest of a file or string using the choice of any algorithm Python has available to it. Tested on Windows 10, OSX and Ubuntu.
* **hexdump**: Prints the hexadecimal representation of file contents alongside the text contents. Automatically tries to fit output to the terminal width. Tested in Windows 10.
* **markdown**: Uses the GitHub API to render a Markdown file as HTML. Takes an input file and an output file. Tested on OSX.
* **regmv**: Moves files in a directory by performing regex substitution on their filenames.

# To do

* Write an installer
* Add config files for vim, mercurial, sublime text
* Add my Greasemonkey scripts
* Write an update checking script
* Write a calculator utility
