#!/bin/bash

TOOLS=~/git/dcs-gradapps-prefilter/

if test ! -z "$1"
then
	app_num="$*"
	read -p "hit enter to filter by $app_num >" junk
else
	read -p "pre-filter enter app_num and hit enter to continue) > " app_num
fi

echo running prefilter helper filtered by $app_num ...

DCS_STATUS=pf
#the * is important.
echo python3 $TOOLS/eat.py -"$app_num" '".*"' $DCS_STATUS

set -x
python3 $TOOLS/eat.py -"$app_num" '.*' $DCS_STATUS
