PURL=http://purl.obolibrary.org/obo/

robot query --use-graphs false -f csv -I $PURL"hp/src/ontology/hp-edit.owl" --query chebi_terms.sparql hp_chebi.txt
robot query --use-graphs false -f csv -I $PURL"mp/mp-edit.owl" --query chebi_terms.sparql mp_chebi.txt
robot query --use-graphs false -f csv -I $PURL"zp/zp-base.owl" --query chebi_terms.sparql zp_chebi.txt
robot query --use-graphs false -f csv -I $PURL"wbphenotype/wbphenotype-base.owl" --query chebi_terms.sparql wbphenotype_chebi.txt