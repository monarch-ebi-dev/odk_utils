#!/bin/sh

set -e

TOOLSDIR=~/tools
ROBOT=v1.7.0
OWLTOOLS=2020-04-06

mkdir -p $TOOLSDIR


wget https://github.com/owlcollab/owltools/releases/download/$OWLTOOLS/owltools -O $TOOLSDIR/owltools && \
    wget https://github.com/owlcollab/owltools/releases/download/$OWLTOOLS/ontology-release-runner -O $TOOLSDIR/ontology-release-runner && \
    wget https://github.com/owlcollab/owltools/releases/download/$OWLTOOLS/owltools-oort-all.jar -O $TOOLSDIR/owltools-oort-all.jar && \
    chmod +x $TOOLSDIR/owltools && \
    chmod +x $TOOLSDIR/ontology-release-runner && \
    chmod +x $TOOLSDIR/owltools-oort-all.jar
    
    
#ROBOT_JAR=https://github.com/ontodev/robot/releases/download/$ROBOT/robot.jar
ROBOT_JAR=https://build.obolibrary.io/job/ontodev/job/robot/job/master/lastSuccessfulBuild/artifact/bin/robot.jar
wget $ROBOT_JAR -O $TOOLSDIR/robot.jar && \
    wget https://raw.githubusercontent.com/ontodev/robot/$ROBOT/bin/robot -O $TOOLSDIR/robot && \
    chmod +x $TOOLSDIR/robot && \
    chmod +x $TOOLSDIR/robot.jar

