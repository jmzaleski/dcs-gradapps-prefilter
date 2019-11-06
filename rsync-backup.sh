#!/bin/bash

# I usually do this in ~/mscac to update ~/mscac/public_html
# it depends on having my ssh public key (id_rsa.pub) known by gradbackup@gradapps.cs.toronto.edu
# lloyd will have to set this up for you.

CMD="rsync -av gradbackup@gradapps.cs.toronto.edu:archive/mscac.2020/mscac20/public_html ."

echo you will exec: $CMD
read -p "hit enter to rsync gradapps backup to ." JUNK
set -x
$CMD

