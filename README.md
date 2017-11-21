# Trader AI
## Overview
This Python application comprises three components with which the functionality of Neural Networks is shown exemplarily. 
The following resources provide some basic introductions into the topic of Neural Networks:
* \# TODO [Material aus Confluence](https://tech-projects.senacor.com/confluence/pages/viewpage.action?pageId=30638253) -> 
    sollten wir noch einzeln je nach Sinnhaftigkeit verlinken
* \# TODO Unsere Präsentation fürs InnoLab, jedenfalls die Folien zum AI-/NN-/ML-Thema allgemein

Some other interesting links:
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
The Innovation Lab Stock Exchange ("ILSE") represents the central 'metronome' of the application. ILSE maintains both
the stock prices and the Trader's portfolios. This means that all Traders connected to ILSE are assigned one portfolio
which ILSE manages to prevent fraud. A portfolios comprises not only the inventory of all stocks and their quantity, but 
also the available cash amount. 

ILSE emulates trading days by calling the connected Traders. To keep it simple the Traders are only called on day's end. 
ILSE then provides each Trader with both the latest close prices and its respective portfolio. The Traders itself is
supposed to reply with a list of trading actions which ILSE has to execute. A trading action is one of the following
actions for all stocks that are traded at ILSE: Buy, Sell or *no action*. After obtaining all trading actions for all
connected Traders ILSE executes them one by one. This is only limited by the check if the specific planned action is
valid for a given portfolio. That means, for buying stocks the portfolio's cash reserve must suffice. On the other hand,
for selling stocks there the planned quantity of stocks must reside in the portfolio.

After execution of all trading actions for all connected Traders the current trading day has ended and the next one 
begins.
  
### Trader
As stated before each Trader is responsible to tell ILSE which trading actions should be executed. Traders are provided
both the latest close prices and their respective current portfolio. Based on this information on of the following
actions with the wished quantity can be selected - however only if the respective stock is tradable at ILSE: Buy or 
Sell.

Most times the Traders' decisions are not based on their own algorithms but rather get those information by one or more
connected Predictors in the background. 

### Predictor
A Predictor works behind a Trader and provides - if applicable - a price estimation for a specific stock. This for
example can be accomplished by working based on a Neural Network, that has been trained on a set of stock prices. To
receive an estimated stock price the Trader calls its specific Predictor with the latest stock prices and the Predictor
in turn replies with the estimated stock price.   

## Required Tools
Trader AI's codebase relies on Python 3. The following paragraphs describe which tools are required to run the 
application.

### Preface
To run Trader AI the following tools are required:
* Python 3
* pip (comes with Python)
* virtualenv (details see below)

### Installing Python 3 on a Mac
On Mac there are two ways to install Python 3:
* The installer way: Visit https://www.python.org/downloads/release/python-363/ to install Python 3
* The Homebrew way: Visit http://docs.python-guide.org/en/latest/starting/install3/osx/ for a tutorial to install 
Python 3 using Homebrew

### Installing Python 3 on a Windows
A good tutorial can be found here: http://docs.python-guide.org/en/latest/starting/install3/win/.

### Optional: Installing virtualenv
The easiest and cleanest way to install all required dependencies is `virtualenv`. This keeps all dependencies in a 
specific directory which in turn will not interfere with your system's configuration. This also allows for easier 
version switching and shipping.

To install virtualenv run `$ pip install virtual env`

### Run the application
After installing all required tools execute the following commands:

* Clone the repository
```
$ git clone https://github.com/senacor/Trader.AI.git
$ cd Trader.AI
```

* If you installed virtualenv the following commands run the following commands
```
$ virtualenv -p python3 virtual_env
$ source virtual_env/bin/activate
```

* Install all requirements
```
$ pip install -r requirements.txt
```

* Run the programm
```
$ python stock_exchange.py
```
After some Terminal action this should show a diagram depicting the course of different portfolios which use different
Trader implementations respectively.

## Development
### IDE
To start developing Python application basically there are not any huge requirements. You could open your favorite text
editor (notepad.exe, TextEdit, vim, Notepad++, sublime, Atom, emacs, ...), type in some code and run it with 
`$ python your-file.py`. However, there are some IDEs which make developing and running Python applications more 
convenient. We worked with the following:
* [JetBrains PyCharm](jetbrains.com/pycharm/)
* [PyDev](http://www.pydev.org/) (based on Eclipse)

In your IDE you may have to select the correct Python environment. Mostly the IDEs can detect the correct environment
automatically. To check and - if needed - reconfigure this do as follows:
* PyCharm: Visit "Preferences" > "Project: Traider.AI" > "Project Interpreter" and check if the right environment is
selected. If not, select the gear symbol in the upper right, click "Add Local" and select the `virtual_env` directory
inside your repository.
* PyDev: \# TODO

### Overview Of This Repository
This repository contains a number of packages and files. Following a short overview:
* datasets - CSV dumps of stock prices
* evaluating - Python package which contains all evaluating/ILSE logic
* model - Python package which contains all shared model classes
* predicting - Python package which contains all predicting logic
* research - \# TODO rm
* trading - Python package which contains all trading logic
* `definitions.py` - Contains some project-wide Python constants
* `dependency_injection_containers.py` - Contains all configured dependencies for dependency injection
* `logger.py` - Contains project-wide logger configuration
* `README.md` - This file
* `requirements.txt` - Contains an export of all project dependencies (by running `$ pip freeze > requirements.txt`)
* `stock_exchange.py` - Contains the central main method. This starts ILSE
* `test_suite_all.py` - Test suite containing all test classes from all packages
* `utils.py` - Contains utility methods that are needed project-wide

## Authors
* [Jonas Holtkamp](mailto:jonas.holtkamp@senacor.com)
* [Richard Müller](mailto:richard.mueller@senacor.com)
* [Janusz Tymoszuk](mailto:janusz.tymoszuk@senacor.com)
