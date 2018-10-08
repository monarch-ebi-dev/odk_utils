import sys
import pandas as pd


#tsv = sys.argv[1]
#entities = sys.argv[2]
#suffix = sys.argv[3]
tsv = 'https://zfin.org/downloads/phenoGeneCleanData_fish.txt'
#tsv = 'https://zfin.org/downloads/phenotype_fish.txt'
id_map = '/ws/zebrafish-phenotype-ontology-build/zp-ids.csv'
# Read column names from file

df_zfin = pd.read_csv(tsv, sep='\t', header=None)
df_map = pd.read_csv(id_map, header=None)
df_map.columns = ["ID", "IRI"]

print(df_zfin.shape)
print(df_map.shape)


ids =  df_zfin[3].map(str) + "-" + df_zfin[5].map(str)+"-"+ df_zfin[7].map(str)+"-"+ df_zfin[9].map(str)+"-"+ df_zfin[12].map(str)+"-"+ df_zfin[14].map(str)+"-"+ df_zfin[16].map(str);
ids = ids.str.replace("nan-","0-")
ids = ids.str.replace("-nan","-0")
print(ids.head(2))

kb = df_zfin[[0,2,11,18,20,21,22,23,24]]
kb.columns = ["ZFINID", "GENEID","PHENOTYPETAG","FISHID","STARTSTAGEID","ENDSTAGEID","FISHENVIRONMENTID","PUBLICATIONID","FIGUREID"]
#kb.loc[:,'ANID'] = ids
kb = kb.assign(ANID=ids.values)
kb = kb.merge(df_map, left_on='ANID', right_on='ID', how='left')
kb.head(3)


preamble = """@prefix : <http://zfin.org/zp/annotations#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <http://zfin.org/zp/annotations> .

<http://zfin.org/zp/annotations> rdf:type owl:Ontology .


#################################################################
#    Annotation properties
#################################################################

###  http://zfin.org/zp/annotations#hasZFINID
:hasZFINID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasGENEID
:hasGENEID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .
           
###  http://zfin.org/zp/annotations#hasPHENOTYPETAG
:hasPHENOTYPETAG rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasFISHID
:hasFISHID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasSTARTSTAGEID
:hasSTARTSTAGEID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .
           
###  http://zfin.org/zp/annotations#hasENDSTAGEID
:hasENDSTAGEID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasFISHENVIRONMENTID
:hasFISHENVIRONMENTID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasPUBLICATIONID
:hasPUBLICATIONID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasFIGUREID
:hasFIGUREID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasAssociatedEQID
:hasAssociatedEQID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

#################################################################
#    Object Properties
#################################################################

###  http://zfin.org/zp/annotations#hasPhenotype
:hasPhenotype rdf:type owl:ObjectProperty .


#################################################################
#    Classes
#################################################################

"""
main = ""

iris = list(set(kb[kb.IRI.notnull()]["IRI"]))
###  http://purl.obolibrary.org/obo/ZP_0021318
for iri in iris:
    main += """### %s
<%s> rdf:type owl:Class ;
        :hasX "%s" . 

""" % (iri,iri,kb[kb.IRI==iri]['ANID'].iloc[0])

main += """
#################################################################
#    Individuals
#################################################################

"""

###  http://www.semanticweb.org/matentzn/ontologies/2018/9/untitled-ontology-320#testI

for index, row in kb.iterrows():
   main += """
:ZPK_%s rdf:type owl:NamedIndividual ,
        [ rdf:type owl:Restriction ;
          owl:onProperty :hasPhenotype ;
          owl:someValuesFrom <%s>
        ] ;
        :hasZFINID %s ;
        :hasGENEID "%s" ;
        :hasPHENOTYPETAG "%s" ;
        :hasFISHID "%s" ;
        :hasSTARTSTAGEID "%s" ;
        :hasENDSTAGEID "%s" ;
        :hasFISHENVIRONMENTID "%s" ;
        :hasPUBLICATIONID "%s" ;
        :hasFIGUREID "%s" .

""" % (row['ZFINID'], row['IRI'], row['ZFINID'], row['GENEID'], row['PHENOTYPETAG'], row['FISHID'], row['STARTSTAGEID'], row['ENDSTAGEID'], row['FISHENVIRONMENTID'], row['PUBLICATIONID'], row['FIGUREID'])

o = preamble + main

text_file = open("kb_zp.ttl", "w")
text_file.write("%s" % o)
text_file.close()
kb.to_csv("zp_annotations_to_iri.txt", sep = '\t', index=False)
