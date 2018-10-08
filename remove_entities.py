import sys
import pandas as pd


tsv = sys.argv[1]
entities = sys.argv[2]
suffix = sys.argv[3]
#tsv = '/data/test_pattern_removeunsat/abnormalQualityPartOfThing.tsv'
#suffix = 'unsat'
#entities = '/ws/zebrafish-phenotype-ontology/zp_unsat.txt'
# Read column names from file
df_all = pd.read_csv(tsv, sep='\t')

with open(entities) as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content]

df_in = df_all[~df_all.defined_class.isin(content)]
df_out = df_all[df_all.defined_class.isin(content)]

df_in.to_csv(tsv, sep = '\t', index=False)
df_out.to_csv(tsv+"_"+suffix, sep = '\t', index=False)
