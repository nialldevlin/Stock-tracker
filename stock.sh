#!/bin/zsh
conda activate stocktracker
python stock-tracker.py > stockout.txt 2> stockerr.txt
conda deactivate
