#!/bin/zsh
git add .
git commit -m $1
git push
sudo cp -r /home/proffessordevnito/Documents/Python_Projects/Stock-tracker/* /var/www/html/
sudo rm /var/www/html/update.sh

