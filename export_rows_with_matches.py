import sys
import pandas as pd


tsv = sys.argv[1]
entities = sys.argv[2]
suffix = sys.argv[3]
tsv = 'https://zfin.org/downloads/phenoGeneCleanData_fish.txt'
tsv = 'https://zfin.org/downloads/phenotype_fish.txt'

suffix = 'phenotype_fish_wronggo.txt'
entities = '/ws/zebrafish-phenotype-ontology/go_process_shortform_partof.txt'
# Read column names from file
df_all = pd.read_csv(tsv, sep='\t', header=None)

with open(entities) as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content]

df_out = df_all[df_all.isin(content).any(axis=1)]
df_out.to_csv(suffix, sep = '\t', index=False)
