#!/bin/zsh
echo $1 >> .gitignore
git rm -r --cached .
git add -A
git commit -am 'Removing ignored files'
git push
