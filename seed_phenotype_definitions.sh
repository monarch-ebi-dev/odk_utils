#!/bin/sh

SCRIPT=$1
PATTERNSDIR=$2
OUTDIR=$3

for filename in $PATTERNSDIR/*.tsv; do
    [ -e "$filename" ] || continue
    # ... rest of the loop body
    fn=$OUTDIR"/"${filename##*/}"_definedclasses.txt"
    echo $filename
    echo $fn

done
