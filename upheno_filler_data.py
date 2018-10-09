#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 8 14:24:37 2018

@author: matentzn
"""

import os
import yaml
import re
import urllib.request
import pandas as pd
from subprocess import check_call

### Configuration

java_sig = "/ws2/phenotype.utils/target/pheno-utils-signature.jar"
java_fill = '/ws2/phenotype.utils/target/pheno-utils-fillers.jar'
upheno_prefix = 'http://purl.obolibrary.org/obo/UPHENO_'
outdir_patterns = '/data/upheno_fillers'
upheno_id_map = "/data/upheno_id_map.txt"
upheno_filler_data_file = 'upheno_fillers.yml'
upheno_filler_ontologies_list = 'ontologies.txt'

curie_map = dict([("GO:", "http://purl.obolibrary.org/obo/GO_"),
                  ("CL:", "http://purl.obolibrary.org/obo/CL_"),
                  ("BFO:", "http://purl.obolibrary.org/obo/BFO_"),
                  ("MPATH:", "http://purl.obolibrary.org/obo/MPATH_"),
                  ("PATO:", "http://purl.obolibrary.org/obo/PATO_"),
                  ("BSPO:", "http://purl.obolibrary.org/obo/BSPO_"),
                  ("NBO:", "http://purl.obolibrary.org/obo/NBO_"),
                  ("UBERON:", "http://purl.obolibrary.org/obo/UBERON_"),
                  ("CHEBI:", "http://purl.obolibrary.org/obo/CHEBI_")])

upheno_pattern_repo = 'obophenotype/upheno/contents/src/patterns'

tsvs_repos = ["obophenotype/zebrafish-phenotype-ontology/contents/src/patterns/data/auto",
              "obophenotype/c-elegans-phenotype-ontology/contents/src/patterns/data/manual",
              "obophenotype/zebrafish-phenotype-ontology/contents/src/patterns/data/auto",
              "obophenotype/c-elegans-phenotype-ontology/contents/src/patterns/data/manual",
              "srobb1/planarian-phenotype-ontology/contents/src/patterns/"]

### Configuration end

### Methods

def get_files_of_type(q,type):
    gh = "https://api.github.com/repos/"
    contents = urllib.request.urlopen(gh+q).read()
    raw = yaml.load(contents)
    tsvs = []
    for e in raw:
        tsv = e['name']
        if tsv.endswith(type):
            tsvs.append(e['download_url'])
    return tsvs

def find_replace_remove(string, dictionary):
    if isinstance(string,list):
        out =  []
        for item in string:
            if ':' in item and '://' not in item:
                for k in dictionary.keys():
                    if item.startswith(k):
                        replace = item.replace(k, dictionary[k])
                        out.append(replace)
                        break
            else:
                out.append(item)
        return out
    if isinstance(string,str):
        if ':' in string and '://' not in string:
            for k in dictionary.keys():
                if string.startswith(k):
                    return string.replace(k, dictionary[k])
        else:
            return string

def get_all_tsv_urls(tsvs_repos):
    tsvs = []

    for repo in tsvs_repos:
        ts = get_files_of_type(repo,'.tsv')
        tsvs.extend(ts)

    tsvs_set = set(tsvs)
    return tsvs_set

def get_upheno_pattern_urls(upheno_pattern_repo):
    upheno_patterns = get_files_of_type(upheno_pattern_repo,'.yaml')
    return upheno_patterns

def get_upheno_filler_data(upheno_pattern_repo,tsvs_repos):
    upheno_patterns = get_upheno_pattern_urls(upheno_pattern_repo)
    tsvs_set = get_all_tsv_urls(tsvs_repos)
    data = dict()
    for pattern in upheno_patterns:
        x = urllib.request.urlopen(pattern).read()
        try:
            y = yaml.load(x)

            filename = os.path.basename(pattern)
            print(filename)
            data[filename] = dict()
            data[filename]['keys'] = dict()
            #ct += 1
            #if ct > 6:
                #break
            columns = dict()
            for v in y['vars']:
                vs = re.sub("[^0-9a-zA-Z _]", "", y['vars'][v])
                filler = y['classes'][vs]
                r = find_replace_remove(filler,curie_map)
                if r == None:
                    print("WARNING: "+filler+" not on curie map!")
                columns[vs]=r
            tsvfn = re.sub("[.]yaml$", ".tsv", filename)

            for tsv in tsvs_set:
                if tsv.endswith(tsvfn):
                    print(tsv)
                    df = pd.read_csv(tsv, usecols=list(columns.keys()), sep='\t')
                    print(str((df.shape)))
                    for col,filler in columns.items():
                        if col not in data[filename]:
                            data[filename][col] = dict()
                            data[filename][col]['keys'] = []
                            data[filename][col]['filler'] = filler
                        d = find_replace_remove(df[col].tolist(),curie_map)
                        data[filename][col]['keys'].extend(d)
        except yaml.YAMLError as exc:
            print(exc)

    for pattern in data:
        print(pattern)
    return data


def export_yaml(data,fn):
    with open(fn, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


def upheno_id(i):
    global last_upheno_index
    if(isinstance(i,str)):
        return i
    else:
        last_upheno_index = last_upheno_index + 1
        id = upheno_prefix+str(last_upheno_index).zfill(7)
        return id


def add_upheno_id(df,pattern):
    global upheno_map
    if 'defined_class' in df.columns:
        df = df.drop(['defined_class'], axis=1)
    df['pattern'] = pattern
    df['id'] = df.apply('-'.join, axis=1)
    df = pd.merge(df, upheno_map, on='id', how='left')
    df['defined_class'] = [upheno_id(i) for i in df['defined_class']]
    upheno_map = upheno_map.append(df[['id', 'defined_class']])
    df = df.drop(['pattern', 'id'], axis=1)
    return df


def add_upheno_ids_to_all_tables(outdir_patterns):
    for file in os.listdir(outdir_patterns):
        if file.endswith(".tsv"):
            f = (os.path.join(outdir_patterns, file))
            df = pd.read_csv(f, sep='\t')
            df = add_upheno_id(df,file.replace(".tsv$", ""))
            df.to_csv(f, sep='\t', index=False)



### Methods end

### Run

# Get the fillers from the available tsvs
data = get_upheno_filler_data(upheno_pattern_repo,tsvs_repos)

# Export the fillers to yaml file.
export_yaml(data,upheno_filler_data_file)

# Get everything in between the phenotype classes and the filler classes
check_call(['java', '-jar',java_fill,upheno_filler_data_file,upheno_filler_ontologies_list,outdir_patterns])

# Load previous map. This must be up to date!
upheno_map = pd.read_csv(upheno_id_map, sep='\t')

# Get the largest assigned id... This variable is global and incremented by the function that generates new ids.
last_upheno_index = max([int(i.replace(upheno_prefix,"").lstrip("0")) for i in upheno_map['defined_class']])

# Add UPHENO ids to all tables around
add_upheno_ids_to_all_tables(outdir_patterns)

# Save the updated UPheno ID map
upheno_map.drop_duplicates().to_csv(upheno_id_map,sep='\t', index=False)

