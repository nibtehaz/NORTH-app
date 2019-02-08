#!/bin/bash
sudo apt --assume-yes install nodejs npm
npm install
sudo apt-get --assume-yes install python3-pip
sudo pip3 install -U scikit-learn
sudo pip3 install -r requirements.txt
