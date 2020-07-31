#!/usr/bin/env bash

ontology_path="/Users/matentzn/ws/upheno-dev/src/curation/upheno-release/all/upheno_all_with_relations.owl";
c1_list="/Users/matentzn/ws/upheno-dev/src/curation/tmp/mp-class-hierarchy.txt";
c2_list="/Users/matentzn/ws/upheno-dev/src/curation/tmp/hp-class-hierarchy.txt";
root="http://purl.obolibrary.org/obo/UPHENO_0001001";
data_path_out="/Users/matentzn/ws/upheno-dev/src/curation/upheno-release/all/upheno_semantic_similarity.csv";
java -Xmx11G -jar target/upheno-semanticsimilarity.jar $ontology_path $c1_list $c2_list $root $data_path_out