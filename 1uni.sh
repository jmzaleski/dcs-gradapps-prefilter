#!/bin/bash

TOOLS=~/git/dcs-gradapps-prefilter/

if test ! -z "$1"
then
	SCHOOL="$1"
	read -p "hit enter to filter by $SCHOOL >" junk
else
	read -p "pre-filter by SCHOOL? (enter filter string eg TORONTO and hit enter to continue) > " SCHOOL
fi

DCS_STATUS=pf
echo running prefilter helper filtered by $SCHOOL ...

echo python3 $TOOLS/eat.py app_numbers $SCHOOL $DCS_STATUS

set -x
python3 $TOOLS/eat.py app_numbers "$SCHOOL" $DCS_STATUS
