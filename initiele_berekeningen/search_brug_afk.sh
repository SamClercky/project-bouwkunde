#!/bin/bash

shopt -s expand_aliases
alias LOG="tee -a bruggen.txt"

echo "=========================" | LOG
echo "=== START BRUG SECTIE ===" | LOG
echo "=========================" | LOG

while :
do
	echo "[*] Start brug berekenen" | LOG
	date | LOG
	python ./search_brug.py | LOG
	echo "\n" | LOG
	echo "[*] End brug berekenen" | LOG
done
