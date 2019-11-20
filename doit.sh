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

# refresh local copy of gradapps from overnight backup site
# snapshot from early morning

set -x
$TOOLS/rsync-backup.sh
set -

# create a file of app numbers to prefilter

set -x
$TOOLS/find-profile-data-app-numbers.sh > app_numbers
set -

DCS_STATUS=pf
echo example of how to filter by $SCHOOL

# run the pre-filtering helper script. This version presents only apps from $SCHOOL sorted by gpa
echo run command: python3 $TOOLS/eat.py app_numbers $SCHOOL $DCS_STATUS

set -x
python3 $TOOLS/eat.py app_numbers $SCHOOL $DCS_STATUS
