#!/bin/bash

TOOLS=~/git/dcs-gradapps-prefilter/

read -p "pre-filter by SCHOOL? (enter filter string eg TORONTO and hit enter to continue) > " SCHOOL
echo will run:
echo python3 $TOOLS/eat.py app_numbers $SCHOOL

set -x
python3 $TOOLS/eat.py app_numbers $SCHOOL
