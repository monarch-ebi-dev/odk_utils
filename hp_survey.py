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


DATADIR = "/ws/hp_analysis/hp/data"
INFDIFFJAR = "/ws/phenoworkbench/patternanalytics/target/infdiff.jar"
AXIOMMETRICSJAR="/ws/phenoworkbench/patternanalytics/target/metrics.jar"
HP = "/ws/hp_analysis/hp/hp.owl"
HP_VERSIONS = "/ws/hp_analysis/hp/hp-versions"
BRANCHES = "/ws/hp_analysis/hp/branches.txt"
TIMEOUT="60m"

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

def collect_data_ontology(o1_path,o2_path,DATA):
    print("Collecting data for: "+o1_path+" and "+o2_path)
    global INFDIFFJAR
    global TIMEOUT
    global BRANCHES

    try:
        check_call(['gtimeout',TIMEOUT,'java', '-jar', '-Xms2G', "-Xmx10G", INFDIFFJAR,o1_path,o2_path,BRANCHES,DATA])
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


def collect_data(TMPONTS,DATADIR,overwrite=True):
    print("Collecting data..")
    global HP
    o1_path = os.path.join(HP)
    f1 = os.path.basename(o1_path)
    for f2 in os.listdir(TMPONTS):
        o2_path = os.path.join(TMPONTS, f2)
        d_path = os.path.join(DATADIR, "diff_"+f1+"___"+f2+".csv")
        if os.path.isfile(o1_path) and os.path.isfile(o2_path) and not f1.startswith("."):
            if overwrite or not os.path.isfile(d_path):
                print("")
                collect_data_ontology(o1_path,o2_path,d_path)
            else:
                print("Data was already collected for "+f1+" and "+f2+", skipping data collection...")




collect_data(TMPONTS=HP_VERSIONS,DATADIR=DATADIR,overwrite=False)

