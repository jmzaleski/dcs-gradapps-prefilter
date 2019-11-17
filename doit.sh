#!/bin/bash

TOOLS=~/git/dcs-gradapps-prefilter/

SCHOOL=SRM
read -p "pre-filter by $SCHOOL? (hit enter to continue)>" new_school

if test -z "$new_school"
then
	echo filter by $SCHOOL
else
	SCHOOL="$new_school"
fi

set -x
$TOOLS/rsync-backup.sh
$TOOLS/find-profile-data-app-numbers.sh > app_numbers
set -

DCS_STATUS=pf
echo example of how to filter by $SCHOOL

echo run command: python3 $TOOLS/eat.py app_numbers $SCHOOL $DCS_STATUS

set -x
python3 $TOOLS/eat.py app_numbers $SCHOOL $DCS_STATUS
