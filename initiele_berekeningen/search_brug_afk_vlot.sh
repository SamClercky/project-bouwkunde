#!/bin/bash

shopt -s expand_aliases
alias LOG="tee -a bruggen5_vlot.txt"

echo "=========================" | LOG
echo "=== START BRUG SECTIE ===" | LOG
echo "=========================" | LOG

while :
do
	echo "[*] Start brug berekenen" | LOG
	date | LOG
	python3 ./search_brug_vlot.py | LOG
	echo "\n" | LOG
	echo "[*] End brug berekenen" | LOG
done
