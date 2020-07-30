#!/bin/sh
# Part of closure

set -e 
sparql_u=partofsparql.ru
sparql_q=partofsparql.sparql
ROOT=obo:UBERON_0000019
RELATION=obo:BFO_0000050

sparql="prefix owl: <http://www.w3.org/2002/07/owl#> 
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
prefix obo: <http://purl.obolibrary.org/obo/> 
INSERT { ?t ${RELATION}_x ?y . } 
WHERE { ?t rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty $RELATION ;
    owl:someValuesFrom ?y ]  .
    FILTER(isIRI(?y))}"

echo $sparql > $sparql_u

sparql="prefix owl: <http://www.w3.org/2002/07/owl#> 
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
prefix obo: <http://purl.obolibrary.org/obo/> 
SELECT ?t WHERE {?t (${RELATION}_x|rdfs:subClassOf)* $ROOT .}"

echo $sparql > $sparql_q

robot query --input uberon_edit.obo --update $sparql_u -o uberon_po.obo
robot query --input uberon_po.obo --query $sparql_q part_of_isa.tsv


