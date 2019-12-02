#!/bin/bash

# I usually do this in ~/mscac to update ~/mscac/public_html
# it depends on having my ssh public key (id_rsa.pub) known by gradbackup@gradapps.cs.toronto.edu
# lloyd will have to set this up for you.

GRAD_APPS="gradbackup@gradapps.cs.toronto.edu"
CMD="rsync -av $GRAD_APPS:archive/mscac.2020/mscac20/public_html ."

if test ! -d public_html
then
	/bin/pwd
	echo where are you? cannot see public_html dir in .
	exit 2
fi

echo trying ssh $GRAD_APPS whoami
echo ssh whoami should return "``gradapps''" almost instantly.. if hanging below start up CSLAB VPN..

set -x
ssh $GRAD_APPS whoami
set -

echo you should see "''"gradapps"``" above indicating that ssh has access to the right machine.
echo $CMD

read -p "hit enter to rsync backup server to . > " JUNK
set -x
$CMD

