#!/bin/bash

TOOLS=~/git/dcs-gradapps-prefilter/

set -s
$TOOLS/rsync-backup.sh
$TOOLS/find-profile-data-app-numbers.sh > app_numbers
python3 $TOOLS/eat.py app_numbers HOPKI
