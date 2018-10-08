import sys
import pandas as pd


tsv = sys.argv[1]
entities = sys.argv[2]

#tsv = '/ws/c-elegans-phenotype-ontology/src/patterns/data/manual/abnormalMorphology.tsv'
#entities = 'abnormalMorphology_defined.txt'

# Read column names from file
df = pd.read_csv(tsv, sep='\t')

with open(entities, 'w') as f:
    for item in df['defined_class']:
        f.write("%s\n" % item)
