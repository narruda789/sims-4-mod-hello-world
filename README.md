# Sims 4 Mod: Hello World
This mod adds a command to print "Hello, world!" from the cheat console in Live mode. The mod was made by following [June Hanabi's 2020 tutorial](https://levelup.gitconnected.com/the-sims-4-modern-python-modding-part-1-setup-83d1a100c5f6).

The main purpose of this project is to provide a pipeline for mod development on a Mac and testing on a PC. The PC should only be used to actually play the game—everything else should be either done on the Mac or automated on the PC.

## Dev environment setup
### Assumptions and prerequisites
- DevOps skills:
  - Some programming knowledge (Python)
  - Using virtual environments with Python
  - Version control with git and GitHub
- PC:
  - Windows 10 or greater
  - The Sims 4 installed
- Mac:
  - macOS Monterey or greater
  - Python 3.7 installed using [pyenv](https://github.com/pyenv/pyenv) and [pipenv](https://pipenv.pypa.io/en/latest/)
  - [PyCharm](https://www.jetbrains.com/pycharm/download/#section=mac) installed
- Familiarity installing and enabling mods in The Sims 4

#### I also highly recommend...
- Sims 4 Mod Manager (will include a link when I find it again!)

### Set up for development on Mac
1. Fork this repo in GitHub. Clone the copy to your Mac.
1. Create the Python virtual environment by one of the following methods:
   - **Option 1:** Open the project in PyCharm. When prompted to create a virtual environment, accept the prompt.
   - **Option 2:** In your terminal, navigate to the root directory of the project. Use `pipenv` to install dependencies, start the shell, and check that the virtual environment is running Python 3.7.
     ```
     $ pipenv install
     $ pipenv shell
     $ python --version
     ```

### Set up for testing mods on PC
1. Clone your copy of the repo to your PC.
1. Locate the Mods folder. The default location is `Documents\Electronic Arts\The Sims 4\Mods`.
1. Inside `Mods`, create a new folder called `Hello World`. Inside `Hello World`, create a folder called `Scripts`:
     ```
     Mods
     └── Hello World
         └── Scripts
     ```
   - The `Mods\<mod-name>\Scripts` folder can handle raw `*.py` files in a nested structure, which is handy for development. `<mod-name>` can be anything, but it must contain a directory named `Scripts`.
1. Locate the `hello-world` directory at the root level of the project. Copy this entire directory. (It should contain two files: `__init__.py` and `main.py`.)
1. Paste the `hello-world` directory into the `Mods\Hello World\Scripts` directory you created earlier:
     ```
     Mods
     └── Hello World
         └── Scripts
             └── hello-world
                 ├── __init__.py
                 └── main.py
     ```

## Using the mod
1. With the mod installed in your Mods directory (following the instructions above), launch The Sims 4.
1. In Live mode, open the cheat console with `Ctrl + Shift + C`.
1. Type `hellow` and hit enter.

:heavy_check_mark: You should see the text `Hello, world!` output to the console.

## Development pipeline
This is currently a manual process. Automation scripts are next on the list.
1. Do some development on the Mac and push changes to the remote repo.
1. On the PC, pull down changes.
1. Copy the root source directory to your `Mods\<mod-name>\Scripts` directory.
2. Run the game.

## Future extensions
- Automation scripts to improve the development pipeline
- Scripts to facilitate packaging and publishing mod releases
- List of katas level-appropriate for someone brand-new to scripting mods