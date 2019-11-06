#!/bin/bash

TOOLS=~/git/dcs-gradapps-prefilter/

set -x
$TOOLS/rsync-backup.sh
$TOOLS/find-profile-data-app-numbers.sh > app_numbers
set -

SCHOOL=WATERLOO
echo this is just an example of how to filter by $SCHOOL
echo run command: python3 $TOOLS/eat.py app_numbers $SCHOOL

read -p "pre-filter by $SCHOOL? (hit enter to continue)>"

set -x
python3 $TOOLS/eat.py app_numbers $SCHOOL
