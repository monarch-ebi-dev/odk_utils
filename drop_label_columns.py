import sys
import pandas as pd


tsv = sys.argv[1]
#tsv = '/ws/zebrafish-phenotype-ontology/src/patterns/abnormalQualityOccursInThing.tsv'
# Read column names from file
cols = list(pd.read_csv(tsv, nrows =1, sep='\t'))
print('Old columns: '+str(cols))
# Use list comprehension to remove the unwanted column in **usecol**
df=pd.read_csv(tsv, usecols=[i for i in cols if not i.endswith('label')], sep='\t')
print('New columns: '+str(df.columns.values))
df.to_csv(tsv, sep = '\t', index=False)
