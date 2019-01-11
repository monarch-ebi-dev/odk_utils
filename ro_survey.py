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


# DATADIR = "/Volumes/EBI/ro_survey_data2/"
# ROSURVEYJAR = "/ws/phenoworkbench/patternanalytics/target/rosurvey.jar"
# CORPORA = "/Volumes/EBI/corpora2/"
# TMPDIR = "/Volumes/EBI/tmp2/ro/"
# TMPONTS = TMPDIR+"ontologies/"
# BLACKLIST=TMPDIR+"blacklist.txt"
# TIMEOUT="1m"


DATADIR = "/Volumes/EBI/ro_survey_data/"
ROSURVEYJAR = "/ws/phenoworkbench/patternanalytics/target/rosurvey.jar"
AXIOMMETRICSJAR="/ws/phenoworkbench/patternanalytics/target/metrics.jar"
CORPORA = "/Volumes/EBI/corpora/"
TMPDIR = "/Volumes/EBI/tmp/ro/"
TMPONTS = TMPDIR+"ontologies/"
BLACKLIST=TMPDIR+"blacklist.txt"
TIMEOUT="60m"

RO_URL = "https://raw.githubusercontent.com/oborel/obo-relations/master/ro.owl"

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

def collect_data_ontology(ontology_path,ro_path,DATADIR):
    print("Collecting data for: "+ontology_path)
    global ROSURVEYJAR
    global TIMEOUT
    try:
        check_call(['gtimeout',TIMEOUT,'java', '-jar', '-Xms2G', "-Xmx10G", ROSURVEYJAR,ro_path,ontology_path,DATADIR])
    except yaml.YAMLError as exc:
        print(exc)
    except CalledProcessError as e:
        print(e.output)

def collect_metrics(ontology_path,DATADIR):
    print("Collecting metrics for: "+ontology_path)
    global AXIOMMETRICSJAR
    global TIMEOUT
    try:
        check_call(['gtimeout',TIMEOUT,'java', '-jar', '-Xms2G', "-Xmx10G", AXIOMMETRICSJAR,ontology_path,DATADIR])
    except yaml.YAMLError as exc:
        print(exc)
    except CalledProcessError as e:
        print(e.output)

def merge_files_in_corpus(corpora, merged_dir, overwrite=True):
    print("Preprocessing ontologies..")
    blacklist = prepare_blacklist(ignore=True)
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
            metadata_out=os.path.join(os.path.abspath(os.path.join(merged_dir, os.pardir)),"rosurvey_merge_"+corpus+".csv")
            df.to_csv(metadata_out, index=False)


def prepare_ro(TMPDIR,overwrite=True):
    print("Preparing RO..")
    global RO_URL
    RO=os.path.join(TMPDIR, "ro.owl")
    if overwrite or not os.path.isfile(RO):
        urllib.request.urlretrieve(RO_URL, RO)
        robot_merge(RO,RO)
    else:
        print("RO was already present, not downloading again.")
    return RO

def collect_data(TMPONTS,DATADIR,overwrite=True):
    print("Collecting data..")
    for file in os.listdir(TMPONTS):
        o_path = os.path.join(TMPONTS, file)
        d_path = os.path.join(DATADIR, "rosurvey_axiomdata_"+file+".csv")
        a_path = os.path.join(DATADIR, "rosurvey_allaxiomdata_" + file + ".csv")
        if os.path.isfile(o_path):
            if overwrite or not os.path.isfile(d_path):
                print()
                collect_data_ontology(o_path,RO,DATADIR)
            else:
                print("Data was already collected for "+file+", skipping data collection...")
            if overwrite or not os.path.isfile(a_path):
                print()
                collect_metrics(o_path,DATADIR)
            else:
                print("Metrics already collected for "+file+", skipping metrics collection...")


prepare_tmp_dir(TMPONTS,delete=False)
RO = prepare_ro(TMPDIR,overwrite=False)
merge_files_in_corpus(CORPORA,TMPONTS,overwrite=False)
collect_data(TMPONTS=TMPONTS,DATADIR=DATADIR,overwrite=False)