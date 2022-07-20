These are some simple utilities I have written. Perhaps they will be helpful to you. Many of these utilities depend on **Python 3**. If you do not already have it installed, you should do so. The installer can be found [here](https://www.python.org/downloads/).

All of my utilities have help pages accessible with the `-h` or `--help` option. Please use them.

I have done my best to make my utilities compatible with modern versions of Linux, Windows, and OSX. I cannot, however, make any guarantees about their compatibility or functionality. I have also done my best to make them run as expected and to prevent them from causing unexpected side effects, but ultimately you choose to use them at your own risk.

Have any questions about them? Feel free to reach out to me. I can be typically be reached between 9am and 5pm (Pacific Time) Monday-Friday on the [Mozilla Chat Server](https://chat.mozilla.org). I go by bytesized.

# Utilities

* **clearclipboard**: Very simple utility that takes no arguments and empties the clipboard. Tested on Windows 10 and Ubuntu.
* **digest**: Computes the digest of a file or string using the choice of any algorithm Python has available to it. Tested on Windows 10, OSX and Ubuntu
* **hexdump**: Prints the hexadecimal representation of file contents alongside the text contents. Automatically tries to fit output to the terminal width. Tested in Windows 10.
* **markdown**: Uses the GitHub API to render a Markdown file as HTML. Takes an input file and an output file. Tested on OSX.
* **regmv**: Moves files in a directory by performing regex substitution on their filenames.
* **colorchooser**: Helper for choosing a terminal color scheme and generating the ANSI escape code to produce that color scheme. Can output a static color chart, enter an interactive style chooser, or generate an ANSI escape sequence based on style information passed as arguments. Tested on OSX and Windows 10.

# To do

* Write an installer
* Write a single, unified version of my .bashrc file and add it to this repo. Currently I have a slightly different version on every system I use.
* Add config files for vim, mercurial, sublime text
* Add my Greasemonkey scripts
* Write an update checking script
* Write a calculator utility
