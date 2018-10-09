#!/bin/sh

# sh remove_entities.sh remove_entities.py /ws/zebrafish-phenotype-ontology/src/patterns/data/manual/ /ws/zebrafish-phenotype-ontology/zp_unsat.txt unsat
SCRIPT=$1
PATTERNSDIR=$2
OUTDIR=$3

for filename in $PATTERNSDIR/*.tsv; do
    [ -e "$filename" ] || continue
    # ... rest of the loop body
    fn=$OUTDIR"/"${filename##*/}"_definedclasses.txt"
    echo $filename
    echo $fn
    python $SCRIPT $filename $fn
done
