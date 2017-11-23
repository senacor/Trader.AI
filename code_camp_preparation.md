# Preparations for the Code Camp
## Guide
1. [Install Python, pip and (optional) virtualenv.](#required-tools)
2. [Create a virtual environment.](#create-a-virtual-environment-optional-) This is optional, however recommended. It 
allows for easier dependency management and prevents messing up your system's Python installation and dependencies. The 
recommended way is to create *one* virtual environment for this Code Camp.
3. [Install all dependencies.](#install-dependencies)
4. Install and [configure an IDE](#configure-ide). We recommend either JetBrains PyCharm or PyDev (based on Eclipse)

## Required Tools
The following tools are required:
* Python 3
* pip
* virtualenv (optional)

Details on how to install these tools are listed below.

### Installing Python 3 and pip on Mac
On Mac there are two ways to install Python 3:
* The installer way: Visit https://www.python.org/downloads/release/python-363/ to install Python 3
* The Homebrew way: Visit http://docs.python-guide.org/en/latest/starting/install3/osx/ for a tutorial to install 
Python 3 using Homebrew

Check if *pip* is installed with running `$ pip --version`. In case it is not already installed:
* When using the installer: Install *pip* separately by running `$ python get-pip.py` after downloading 
[get-pip.py](https://bootstrap.pypa.io/get-pip.py)
* When using Homebrew: Execute `$ brew install pip`

### Installing Python 3 and pip on Windows
A good tutorial can be found here: http://docs.python-guide.org/en/latest/starting/install3/win/. To ease running Python
in the Command Line you should consider adding the Python installation directory to the PATH environment variable.

Check if *pip* is installed with running `$ pip --version`. In case it is not already installed run 
`$ python get-pip.py` after downloading [get-pip.py](https://bootstrap.pypa.io/get-pip.py).

### Optional: Installing virtualenv
The easiest and cleanest way to install all required dependencies is *virtualenv*. This keeps all dependencies in a 
specific directory which in turn will not interfere with your system's configuration. This also allows for easier 
version switching and shipping.

To install *virtualenv* run `$ pip install virtualenv`

## Create a Virtual Environment (optional)
If you want to use *virtualenv*, create a virtual environment. The directory *virtual_env* is already added to 
*.gitignore*.

### On Mac
```
$ virtualenv -p python3 virtual_env
$ source virtual_env/bin/activate
```

### On Windows
```
$ virtualenv -p [path\to\python3\installation\dir\]python virtual_env
$ virtual_env/Scripts/activate
```

## Install dependencies
Download `requirements.txt` and install all Code Camp-related dependencies (in the newly
created virtual environment):
```
$ wget https://raw.githubusercontent.com/senacor/Trader.AI/master/requirements.txt
$ pip install -r requirements.txt
```

## Configure IDE
To start developing Python applications, there are not any huge requirements actually. You could open your favorite text
editor (notepad.exe, TextEdit, vim, Notepad++, sublime, Atom, emacs, ...), type in some code and run it with 
`$ python your-file.py`. However, there are some IDEs which make developing and running Python applications more 
convenient. We worked with the following:
* [JetBrains PyCharm](jetbrains.com/pycharm/)
* [PyDev](http://www.pydev.org/) (based on Eclipse)

In your IDE you may have to select the correct Python environment. Mostly the IDEs can detect the correct environment
automatically. To check and - if needed - select the correct Python installation directory or the *virtual_env* 
directory inside your repository do as follows:
* **PyCharm**: Visit "Preferences" > "Project: Traider.AI" > "Project Interpreter" and check if the correct environment 
is selected. If not, select the gear symbol in the upper right
* **PyDev**: Visit "Window" > "Preferences" > "PyDev" > "Interpreters" > "Python Interpreter" and check if the correct
environment is selected. If not, select "New..."
