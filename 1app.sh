#!/bin/bash

TOOLS=~/git/dcs-gradapps-prefilter/

if test ! -z "$1"
then
	app_num="$*"
	echo  "will filter by $app_num" 
else
	read -p "pre-filter enter app_num and hit enter to continue) > " app_num
fi

echo running prefilter helper filtered by $app_num ...

DCS_STATUS=pf
#the * is important.
echo python3 $TOOLS/eat.py --app_num_list="$app_num" '".*"' 

set -x
python3 $TOOLS/eat.py --app_num_list="$app_num" '.*'
