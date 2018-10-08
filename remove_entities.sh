#!/bin/sh

# sh remove_entities.sh remove_entities.py /ws/zebrafish-phenotype-ontology/src/patterns/data/manual/ /ws/zebrafish-phenotype-ontology/zp_unsat.txt unsat
REMOVEENTITIESPYTHON=$1
PATTERNSDIR=$2
REMOVE=$3
SUFFIX=$4
for filename in $PATTERNSDIR/*.tsv; do
    [ -e "$filename" ] || continue
    # ... rest of the loop body
    echo $filename
    python $REMOVEENTITIESPYTHON $filename $REMOVE $SUFFIX
done
