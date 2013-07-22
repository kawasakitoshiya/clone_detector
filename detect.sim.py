"""detect.py

I mainly uses this file to write main excutions
(c) Toshiya Kawasaki 2013
"""

import sys 
from mcdetector.model import Model
from mcdetector.agm import AGM
from mcdetector.translator import AGMTranslator

if __name__ == '__main__':
    
    minify=0
    all_nodes_connected=True
    
    fp_clooca_in = 'work/clooca.in.xml'
    fp_clooca_out = "work/clooca.out.xml"
    fp_clooca_in_gml = "work/clooca.in.gml"
    fp_clooca_out_gml = "work/clooca.out.gml"

    graphs=[]
    model=Model("./data/test.json")
    model.clooca2graph("master","HEAD")
    if minify==1:
        model.replace_containments_with_nodes_by_making_hash()
    graphs.append(model.graph)
    
    model2=Model("./data/test2.json")
    model2.clooca2graph("master","HEAD")
    if minify==1:
        model2.replace_containments_with_nodes_by_making_hash()
    graphs.append(model2.graph)

    trans = AGMTranslator()
    trans.replace_containments_with_nodes_by_similarity(graphs[0],graphs[1],0.8)
    
