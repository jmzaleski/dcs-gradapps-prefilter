#!/bin/bash

TOOLS=~/git/dcs-gradapps-prefilter/

if test ! -z "$1"
then
	SCHOOL="$1"
	echo $0 "filter by $SCHOOL"
else
	read -p "pre-filter by SCHOOL? (enter filter string eg TORONTO and hit enter to continue) > " SCHOOL
fi

DCS_STATUS=pf
echo running prefilter helper filtered by $SCHOOL ...

echo python3 $TOOLS/eat.py $SCHOOL

set -x
python3 $TOOLS/eat.py --skip-prefiltered "$SCHOOL" 
