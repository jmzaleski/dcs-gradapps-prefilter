#!/bin/bash

TOOLS=~/git/dcs-gradapps-prefilter/

SCHOOL1="TORONTO|BRITISH COLUMBIA|MCGILL|MCMASTER|ALBERTA|OTTAWA|WATERLOO|WESTERN ONTARIO|DALHOUSIE|QUEEN'S|SIMON FRASER"
SCHOOL2="BISHOP'S|ATHABASCA|SENECA|RYERSON|ST MARY'S|XAVIER|MEMORIAL UNIV|LAKEHEAD|KINGSTON|GEORGE BROWN|CONCORDIA|WILFRID LAURIER|MANITOBA|GUELPH|UNIV OF VICTORIA|REGINA|WINDSOR"

#UNIV OF NORTHERN B C
#CONESTOGA COLL OF A A & T,1,1001,-,-

SCHOOL="$SCHOOL1"

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

set -x
python3 $TOOLS/eat.py --skip-prefilter "$SCHOOL"
