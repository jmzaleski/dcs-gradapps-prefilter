#!/bin/bash

TOOLS=~/git/dcs-gradapps-prefilter/

SCHOOL='TORONTO|WATERLOO|BRITISH COLUMBIA|MCGILL|ALBERTA'
APP_NUMBER_FN=app_numbers

echo $0 runs prefilter tool for schools in the application numbers listed by $APP_NUMBER_FN
ls -l $APP_NUMBER_FN
echo
echo just hit enter to NOT overwrite
read -p "continue with  this $APP_NUMBER_FN file or overwrite with fresh one (y or n) >" RESP
case $RESP in
	[qQxX]*)
		echo you entered something I interpreted as quit..
		exit 0
		;;
	[yY]*)
		echo okay, I enterpret that as a yes, overwriting..
		set -x
		./find-profile-data-app-numbers.sh > $APP_NUMBER_FN
		ls -l $APP_NUMBER_FN
		set -
		;;
	*)
		echo you entered something I interpreted as no, so not overwriting $APP_NUMBER_FN
		;;
esac


echo
echo default filter $SCHOOL '(ostensibly)' finds the top Canadians unis
echo you can put this on command line or enter new one below
echo

if test ! -z "$1"
then
	SCHOOL="$1"
	echo $0 "filter by $SCHOOL"
else
	echo you can give another regexp on command line. or enter one below, if you enter nothing assumes above
	echo an example filter would be "$SCHOOL"
	read -p "enter school filter.. (just enter uses above default) > " school
	if test ! -z $school
	then
		SCHOOL="$school"
	fi
fi

DCS_STATUS=pf
echo running prefilter helper --skip-prefilter app_numbers filtered by $SCHOOL ...

#echo python3 $TOOLS/eat.py --skip-prefilter app_numbers $SCHOOL $DCS_STATUS

ls -l app_numbers
set -x
python3 $TOOLS/eat.py --skip-prefilter app_numbers "$SCHOOL" $DCS_STATUS
