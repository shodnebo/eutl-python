# eutl-python
This is a demo of data download and parsing of the EU Transaction Log using python

## Required packages
* pip install pandas
* pip install lxml
* pip install requests
* pip install html5lib
* pip install beautifulsoup4
* pip install matplotlib
* pip install geocoder
* pip install Flask
To install scipy download generated binaries from http://www.lfd.uci.edu/~gohlke/pythonlibs/
* pip install numpy-1.11.3+mkl-cp35-cp35m-win32.whl
* pip install scipy-0.19.0-cp35-cp35m-win32.whl

## eutl-getdata.py
This will download data and store locally. 
To fetch the data again set FETCH_NEW = True

## eutl-sum.py
Create an aggregate and plot the result

## eutl-geocode.py
Find missing geocoding based on name and address

## eutl-rest.py
Use Flask to run a service

## eutl-forecast.py
Try to predict a year and compare to actual

