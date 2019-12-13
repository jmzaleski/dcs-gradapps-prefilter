#!/bin/bash

TOOLS=~/git/dcs-gradapps-prefilter/

SCHOOL1="TORONTO|BRITISH COLUMBIA|MCGILL|MCMASTER|ALBERTA|OTTAWA|WATERLOO|WESTERN ONTARIO|DALHOUSIE|QUEEN'S|SIMON FRASER"

SCHOOL2="BISHOP'S|ATHABASCA|SENECA|RYERSON|ST MARY'S|XAVIER|MEMORIAL UNIV|LAKEHEAD|KINGSTON|GEORGE BROWN|CONCORDIA|WILFRID LAURIER|MANITOBA|GUELPH|UNIV OF VICTORIA|REGINA|WINDSOR"

if test -z "$SCHOOL"
then
	echo enter regexp below, if you enter nothing assumes above
	echo an example filter would be "TORONTO|WATERLOO|MCGILL"
	read -p "enter school filter.. (just enter uses above default) > " school
	if test ! -z $school
	then
		SCHOOL="$school"
	fi
fi

set -x
python3 $TOOLS/eat.py --skip-prefilter "$SCHOOL"
