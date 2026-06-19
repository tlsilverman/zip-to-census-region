This is a script that fetches the census region for a list of states and zip codes and outputs a CSV file with the updated census region.
It also fetches the state in which a zip code is located if the CSV file line containing the zip code does not include a state.
This script is designed to work with the SaferProducts.gov incident report CSV file, and should not be expected to work with other CSV files.

You must install [python](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installation/) for this script to function. You should already have access to pip if you installed Python.

To run this script, type these commands into your terminal while within the root directory of the repository. The pip command only needs to be run once.
```
pip install -r requirements.txt
python main.py
```
This script has only been tested on Fedora Linux 44, but should work on Windows, macOS, and all major Linux distributions.
