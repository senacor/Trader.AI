Trader AI
===
[![Build Status](https://travis-ci.org/senacor/Trader.AI.svg?branch=master)](https://travis-ci.org/senacor/Trader.AI.svg?branch=master)

## Abstract
Python application to show AI functionality based on Keras and TensorFlow.

## Table Of Content
* [Abstract](#abstract)
* [Table Of Content](#table-of-content)
* [Overview](#overview)
* [Components](#components)
  * [Stock Exchange](#stock-exchange) 
  * [Trader](#trader)
  * [Predictor](#predictor)
* [Required Tools](#required-tools)
  * [Installing Python and pip 3 on Mac](#installing-python-3-and-pip-on-mac)
  * [Installing Python and pip 3 on Windows](#installing-python-3-and-pip-on-windows)
  * [Optional: Installing virtualenv](#optional-installing-virtualenv)
* [Run the Application](#run-the-application)
  * [Clone the Repository](#clone-the-repository)
  * [Create a Virtual Environment (optional)](#create-a-virtual-environment-optional-)
  * [Install All Dependencies](#install-all-dependencies)
  * [Run](#run)
* [Development](#development)
  * [IDE](#ide)
  * [Overview Of This Repository](#overview-of-this-repository)
* [Authors](#authors)

## Overview
This Python application simulates a computer-based stock trading program. Its goal is to demonstrate the basic 
functionality of neural networks trained by supervised learning and reinforcement learning (deep Q-learning).

The application consists of a stock exchange and serveral connected traders. The stock exchange asks each trader once 
per day for its orders, and executes any received ones. Each trader computes its orders using stock market information 
provided by the stock exchange. A trader consists of two components: A neural network for predicting future stock 
prices, and a neural network for computing orders based on these predictions. Thereby, the first neural network can be 
trained using supervised learning, and the latter neural network can be trained using reinforcement learning (deep 
Q-learning).

The following resources provide some basic introductions into the topic of Neural Networks:
* \# TODO [Material aus Confluence](https://tech-projects.senacor.com/confluence/pages/viewpage.action?pageId=30638253) -> 
    sollten wir noch einzeln je nach Sinnhaftigkeit verlinken
* \# TODO Unsere Präsentation fürs InnoLab, jedenfalls die Folien zum AI-/NN-/ML-Thema allgemein

Some other interesting links: \# TODO
* AI basics
  * [30 amazing applications of deep learning](http://www.yaronhadad.com/deep-learning-most-amazing-applications/)
  * [Neural Network to play a snake game – Towards Data Science – Medium](https://medium.com/towards-data-science/today-im-going-to-talk-about-a-small-practical-example-of-using-neural-networks-training-one-to-6b2cbd6efdb3)
  * [The AI Revolution: The Road to Superintelligence](https://waitbutwhy.com/2015/01/artificial-intelligence-revolution-1.html)
  * [Using Keras and Deep Q-Network to Play FlappyBird](https://yanpanlau.github.io/2016/07/10/FlappyBird-Keras.html)
  
* Reinforcement Learning
  * [Wikipedia: Reinforcement Learning](https://en.wikipedia.org/wiki/Reinforcement_learning)
  * [Demystifying Deep Reinforcement Learning - Intel Nervana](https://www.intelnervana.com/demystifying-deep-reinforcement-learning/)
  
* Python
  * [Learn Python - Free Interactive Python Tutorial](https://www.learnpython.org/en/Welcome)

## Components
### Stock Exchange
The Innovation Lab Stock Exchange ("ILSE") represents the central 'metronome' of the application. It is implemented by 
a class 'StockExchange'. ILSE maintains both the stock prices and the trader's portfolios. This means that all traders 
connected to ILSE are assigned one portfolio which ILSE manages to prevent fraud. A portfolios comprises not only the 
inventory of all stocks and their quantity, but also the available cash amount. 

ILSE emulates trading days by calling the connected traders. To keep it simple the traders are only called on day's end. 
ILSE then provides each trader with both the latest close prices and its respective portfolio. A trader is supposed to 
reply with a list of orders which ILSE has to execute. An order is one of the following actions for all stocks that are 
traded at ILSE: Buy or sell. After obtaining all orders for all connected traders ILSE executes the orders one by one. 
This is only limited by checks whether the specific order is valid for a given portfolio. That means, for buying stocks 
the portfolio's cash reserve must suffice. For selling stocks, the corresponding quantity of stocks must reside in the 
portfolio.

After executing all orders for all connected traders the current trading day has ended and the next one begins.
  
### Trader
Each trader is implemented by a separate trader class (e.g., 'SimpleTrader' or 'DqlTrader') and responsible to tell ILSE
which orders should be executed. Traders are provided with both the latest close prices and their current portfolio. 
Based on these informatiosn one of the following actions with the wished quantity can be selected: Buy or sell.

Most times the traders' decisions are not based on their own algorithms but rather get those information by one or more
connected predictors in the background. 

### Predictor
A predictor (implemented by separate predictor classes like 'PerfectPredictor') works behind a trader and provides - 
if applicable - a price estimation for a specific stock. Among other ways, providing a price estimate can be 
accomplished by using a neural network that has been trained on a set of past stock prices. To receive an estimated 
stock price the trader calls its specific predictor with the latest stock prices and the predictor in turn replies with 
the estimated future stock price.   

## Required Tools
Trader AI's codebase relies on Python 3. To run Trader AI the following tools are required:
* Python 3
* pip (may come with your Python installation)
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

## Run the Application
After installing all required tools (Python, *pip*, *\[virtualenv]*) execute the following commands:

### Clone the Repository
```
$ git clone https://github.com/senacor/Trader.AI.git
$ cd Trader.AI
```

### Create a Virtual Environment (optional)
If you want to use *virtualenv*, create a virtual environment. The directory *virtual_env* is already added to 
*.gitignore*.

#### On Mac
```
$ virtualenv -p python3 virtual_env
$ source virtual_env/bin/activate
```

#### On Windows
```
$ virtualenv -p [path\to\python3\installation\dir\]python virtual_env
$ virtual_env/Scripts/activate
```

### Install All Dependencies
This installs all required dependencies by Trader.AI.
```
$ pip install -r requirements.txt
```

### Run
```
$ python stock_exchange.py
```
After some Terminal action this should show a diagram depicting the course of different portfolios which use different
Trader implementations respectively.

Furthermore you can execute the test suite to see if all works well:
```
$ python test_suite_all.py
```

## Development
### IDE
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

### Overview Of This Repository
This repository contains a number of packages and files. Following a short overview:
* datasets - CSV dumps of stock prices
* evaluating - Python package which contains all evaluating/ILSE logic
* model - Python package which contains all shared model classes
* predicting - Python package which contains all predicting logic
* trading - Python package which contains all trading logic
* `.travis.yml` - Configuration for Travis CI. See [https://travis-ci.org/senacor/Trader.AI/]()
* `definitions.py` - Contains some project-wide Python constants
* `dependency_injection_containers.py` - Contains all configured dependencies for dependency injection
* `logger.py` - Contains project-wide logger configuration
* `README.md` - This file
* `requirements.txt` - Contains an export of all project dependencies (by running `$ pip freeze > requirements.txt`)
* `stock_exchange.py` - Contains the central main method. This starts ILSE
* `utils.py` - Contains utility methods that are needed project-wide

## Authors
* [Jonas Holtkamp](mailto:jonas.holtkamp@senacor.com)
* [Richard Müller](mailto:richard.mueller@senacor.com)
* [Janusz Tymoszuk](mailto:janusz.tymoszuk@senacor.com)
