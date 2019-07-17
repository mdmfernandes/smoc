# A Stochastic Multi-objective Optimizer for Cadence Virtuoso (SMOC)

Client: [![Python -V client](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/release/python-360/)
Server: [![Python -V server](https://img.shields.io/badge/python-2.6%2B-blue.svg)](https://www.python.org/downloads/release/python-260/) [![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://github.com/mdmfernandes/smoc/blob/master/LICENSE)

**More documentation will be available soon!**

**SMOC** is a stochastic circuit optimizer based on the NSGA-II genetic algorithm (GA) for Cadence Virtuoso, written in Python. The GA is implemented using the [DEAP library][DEAP].

This application has two components:

* **Optimizer**: Performs the optimization of the circuit and communicates with the server to send circuit variables and get simulation results. This module is available [here](https://github.com/mdmfernandes/smoc/tree/master/smoc).
* **Server**: Communicates with Cadence Virtuoso and with the Optimizer to exchange circuit variables, simulation results, etc. This module is available [here](https://github.com/mdmfernandes/smoc/tree/master/smoc_cadence).

For more info about the communication, please check the [SOCAD project][SOCAD].

The circuit simulations are performed using the *Cadence Virtuoso ADE-XL*. If you only have access to *ADE-L*, you can modify SMOC to use it instead ([this tutorial](https://socad.readthedocs.io/en/latest/tutorials/common_source.html) may be helpful). The *ADE-XL* was used because it allows to perform parallel simulations, thus reducing the optimization time.

## Installation

**This section refers only to the optimizer.**

Although not mandatory, you can install the SMOC in your machine to simplify it's use (i.e. run it directly from the system's path). There are two options to install SMOC, as shown below.

### Build from source

Go to the project folder and run:

```shell
python setup.py install
```

### Install with *pip*

Although the project is not in PyPI, you can install it using *pip*. Go to the project folder and run:

```shell
pip install .
```

**NOTE:** run `pip install smoc` from the project directory doesn't work because pip will look for the package on PyPi.

After using one of these methods, all dependencies will be installed and SMOC will be added to your path as `smoc`.

If you prefer to not install SMOC, you can run it as like any Python program. To install the required depedencies please check the [Requirements](#requirements) below.

## Requirements

### Python versions

The optimizer module requires Python 3.6 or above, and the server module requires Python 2.6 or above (including Python 3.0+ versions). The required packages are shown below.

SMOC server is compatible out of the box with Python 2.6+, so no additional packages are required.

### Packages (optimizer)

 SMOC requires the following packages, which are specified in [requirements.txt](https://github.com/mdmfernandes/smoc/blob/master/requirements.txt):

* [DEAP][DEAP] - Implementation of the NSGA-II algorithm
* [SOCAD][SOCAD] - Communication between the optimizer and Cadence Virtuoso
* [Bokeh](https://bokeh.pydata.org/en/latest/) - Plot of the pareto fronts resulting from the optimization process
* [PyYAML](https://pyyaml.org/) - Parse of the optimizer configuration file, which is written in YAML

You can install the packages manually or by using the following command:

```shell
pip install -r requirements.txt
```

### Cadence Virtuoso

This app was tested with Cadence Virtuoso IC6.1.7-64b.500.15 and the ADE-XL environment.

## Usage

### Optimizer

The optimizer can be run from any machine that is able to communicate with the machine where Cadence Virtuoso is installed. It can be placed in the same machine (for more info about the communication, please check the [SOCAD project][SOCAD]).

```shell
$ smoc [-h] [-c FILE] [-d] CFG

positional arguments:
  CFG                   file with the optimizer parameters

optional arguments:
  -h, --help            show this help message and exit
  -c, --checkpoint FILE
                        continue the optimization from a checkpoint file
  -d, --debug           run the program in debug mode
```

Please note that if you didn't installed SMOC in your machine, you need to use the following command (from the project's root directory) to run the app:

```shell
python -m smoc [-h] [-c FILE] [-d] CFG
```

### Server

The SMOC server should be placed in the machine where Cadence Virtuoso is installed.

```shell
$ python start_cadence.py [-h] FILE

SMOC - A Stochastic Multi-objective Optimizer for Cadence Virtuoso

positional arguments:
  FILE        file with the SMOC server parameters

optional arguments:
  -h, --help  show this help message and exit
```

## Extras

You can find useful documents related to this project, but that doesn't fit in the project structure, in this [public repository](https://github.com/mdmfernandes/smoc-extras).

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [releases on the project repository](https://github.com/mdmfernandes/smoc/releases/).

## Authors

* **Miguel Fernandes** - *Initial work* - [mdmfernandes](https://github.com/mdmfernandes)

## License

This project is licensed under the GPLv3 License - see the project [LICENSE](https://github.com/mdmfernandes/smoc/blob/master/LICENSE) file for details.

[DEAP]: https://github.com/deap/deap
[SOCAD]: https://github.com/mdmfernandes/socad
