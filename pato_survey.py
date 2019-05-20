#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 8 14:24:37 2018

@author: matentzn
"""

import os
import shutil
import pathlib
import pandas as pd
import yaml
import urllib.request
from subprocess import check_call,CalledProcessError
import urllib.request



### Configuration

DATADIR = "/data/pato_survey_data/"
SURVEYJAR = "/ws/phenoworkbench/patternanalytics/target/patosurvey.jar"
AXIOMMETRICSJAR="/ws/phenoworkbench/patternanalytics/target/metrics.jar"
CORPORA = "/data/corpora/"
TMPDIR = "/data/tmp_pato/"
TMPONTS = TMPDIR+"ontologies/"
BLACKLIST=TMPDIR+"blacklist.txt"
TIMEOUT="60m"

PATO_URL = "http://purl.obolibrary.org/obo/pato.owl"

### Configuration end

def prepare_blacklist(ignore=False):
    global BLACKLIST
    f = open(BLACKLIST, 'r')
    file = f.readlines()
    y = [x.replace('\n', '') for x in file]
    if ignore:
        y = []
    f.close()
    return(y)

# Set up directories
def prepare_tmp_dir(TMPDIR,delete=True):
    if os.path.exists(TMPDIR) and os.path.isdir(TMPDIR) and delete:
        shutil.rmtree(TMPDIR)
    pathlib.Path(TMPDIR).mkdir(parents=True, exist_ok=True)

### Prepare corpora
def robot_merge(ontology_path, ontology_merged_path):
    print("Merging "+ontology_path+" to "+ontology_merged_path)
    global TIMEOUT
    try:
        check_call(['gtimeout',TIMEOUT,'robot', 'merge','-vvv','--input', ontology_path, '--output', ontology_merged_path])
    except yaml.YAMLError as exc:
        print(exc)
    except CalledProcessError as e:
        print(e.output)

def robot_remove_imports(ontology_path, ontology_merged_path):
    print("Removing imports from "+ontology_path+" to "+ontology_merged_path)
    global TIMEOUT
    try:
        check_call(['gtimeout',TIMEOUT,'robot', 'remove','--select','imports', '--input', ontology_path, '--output', ontology_merged_path])
    except yaml.YAMLError as exc:
        print(exc)
    except CalledProcessError as e:
        print(e.output)

def collect_data_ontology(ontology_path,pato_path,DATADIR):
    print("Collecting data for: "+ontology_path)
    global SURVEYJAR
    global TIMEOUT
    try:
        check_call(['gtimeout',TIMEOUT,'java', '-jar', '-Xms2G', "-Xmx12G", SURVEYJAR,pato_path,ontology_path,DATADIR])
    except yaml.YAMLError as exc:
        print(exc)
    except CalledProcessError as e:
        print(e.output)

def collect_metrics(ontology_path,DATADIR):
    print("Collecting metrics for: "+ontology_path)
    global AXIOMMETRICSJAR
    global TIMEOUT
    try:
        check_call(['gtimeout',TIMEOUT,'java', '-jar', '-Xms2G', "-Xmx12G", AXIOMMETRICSJAR,ontology_path,DATADIR])
    except yaml.YAMLError as exc:
        print(exc)
    except CalledProcessError as e:
        print(e.output)

def merge_files_in_corpus(corpora, merged_dir, overwrite=True,ignore_blacklist=True):
    print("Preprocessing ontologies..")
    blacklist = prepare_blacklist(ignore=ignore_blacklist)
    for corpus in os.listdir(corpora):
        corpus_path = os.path.join(corpora, corpus)
        if os.path.isdir(corpus_path):
            df = pd.DataFrame()
            for ontology in os.listdir(corpus_path):
                ontology_path = os.path.join(corpus_path, ontology)
                if os.path.isfile(ontology_path) and ontology_path.endswith('.owl'):
                    ontology_merged_path = os.path.join(merged_dir, corpus + "_merged_" + ontology)
                    ontology_noimports_path = os.path.join(merged_dir, corpus + "_noimports_" + ontology)
                    if ontology_path not in blacklist:
                        if (overwrite or not os.path.isfile(ontology_merged_path)):
                            print("Performing ROBOT preprocessing for " + ontology + "(Corpus: " + corpus + ")")
                            robot_merge(ontology_path, ontology_merged_path)
                            robot_remove_imports(ontology_path, ontology_noimports_path)
                        else:
                            print(ontology + " (Corpus: " + corpus + ") was already preprocessed, skipping..")
                    else:
                        print(ontology + " blacklisted, skipping..")

                    merged_success=False
                    if(os.path.isfile(ontology_merged_path)):
                        # Picked 550 here because it is the size of an empty ontology
                        if os.path.getsize(ontology_merged_path)>550:
                            merged_success = True
                        else:
                            os.remove(ontology_merged_path)

                    remove_success = False
                    if (os.path.isfile(ontology_noimports_path)):
                        if os.path.getsize(ontology_noimports_path)>550:
                            remove_success = True
                        else:
                            os.remove(ontology_noimports_path)

                    df = df.append({'filepath': ontology_path, 'mergedpath': ontology_merged_path, 'noimportspath': ontology_noimports_path, 'remove_success':remove_success,'merged_success':merged_success}, ignore_index=True)
            metadata_out=os.path.join(os.path.abspath(os.path.join(merged_dir, os.pardir)),"patosurvey_merge_"+corpus+".csv")
            df.to_csv(metadata_out, index=False)

def robot_label(o,out):
    print("Exporting labels " + o + " to " + out)
    global TIMEOUT
    try:
        check_call(
            ['gtimeout', TIMEOUT, 'robot', 'query', '--use-graphs', 'true', '-f','csv', '-i', o,'--query','term_table.sparql', out])
    except yaml.YAMLError as exc:
        print(exc)
    except CalledProcessError as e:
        print(e.output)

def prepare_pato(TMPDIR,overwrite=True):
    print("Preparing PATO..")
    global PATO_URL
    PATO=os.path.join(TMPDIR, "pato.owl")
    PATO_labels = os.path.join(TMPDIR, "patosurvey_labels_pato.csv")
    if overwrite or not os.path.isfile(PATO):
        urllib.request.urlretrieve(PATO_URL, PATO)
        robot_merge(PATO,PATO)
        robot_label(PATO,PATO_labels)
    else:
        print("PATO was already present, not downloading again.")
    return PATO

def collect_data(TMPONTS,DATADIR,PATO,overwrite=True):
    print("Collecting data..")
    for file in os.listdir(TMPONTS):
        o_path = os.path.join(TMPONTS, file)
        d_path = os.path.join(DATADIR, "patosurvey_axiomdata_"+file+".csv")
        a_path = os.path.join(DATADIR, "patosurvey_allaxiomdata_" + file + ".csv")
        if os.path.isfile(o_path):
            if overwrite or not os.path.isfile(d_path):
                print()
                collect_data_ontology(o_path,PATO,DATADIR)
            else:
                print("Data was already collected for "+file+", skipping data collection...")
            if overwrite or not os.path.isfile(a_path):
                print()
                collect_metrics(o_path,DATADIR)
            else:
                print("Metrics already collected for "+file+", skipping metrics collection...")


prepare_tmp_dir(TMPONTS,delete=False)
PATO = prepare_pato(TMPDIR,overwrite=False)
merge_files_in_corpus(CORPORA,TMPONTS,overwrite=False,ignore_blacklist=True)
collect_data(TMPONTS=TMPONTS,DATADIR=DATADIR,PATO=PATO,overwrite=False)