#!/bin/bash

TOOLS=~/git/dcs-gradapps-prefilter/

if test ! -z "$1"
then
	app_num="$1"
	read -p "hit enter to filter by $app_num >" junk
else
	read -p "pre-filter enter app_num and hit enter to continue) > " app_num
fi

echo running prefilter helper filtered by $app_num ...

#the * is important.
echo python3 $TOOLS/eat.py -"$app_num" '".*"'

set -x
python3 $TOOLS/eat.py -"$app_num" '.*'
