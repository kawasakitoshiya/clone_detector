"""detect.py

I mainly uses this file to write main excutions
(c) Toshiya Kawasaki 2013
"""

import sys 
from mcdetector.model import Model
from mcdetector.agm import AGM
from mcdetector.translator import AGMTranslator

def main():
    
    minify=1
    all_nodes_connected=True
    
    fp_clooca_in = 'work/clooca.in.xml'
    fp_clooca_out = "work/clooca.out.xml"
    fp_clooca_in_gml = "work/clooca.in.gml"
    fp_clooca_out_gml = "work/clooca.out.gml"

    graphs=[]
    model=Model("./data/large1.json")
    model.clooca2graph("master","HEAD")
    if minify==1:
        model.replace_containments_with_nodes_by_making_hash()
    graphs.append(model.graph)
    
    model2=Model("./data/large2.json")
    model2.clooca2graph("master","HEAD")
    if minify==1:
        model2.replace_containments_with_nodes_by_making_hash()
    graphs.append(model2.graph)

    trans0 = AGMTranslator()
    agm_xml = trans0.graph2agm(graphs)
    fp_clooca_in = 'work/clooca.in.xml'
    f = open(fp_clooca_in, 'w')
    f.write(agm_xml)
    f.close()
    trans=AGMTranslator()
    trans.agm2gml(fp_clooca_in,fp_clooca_in_gml ,0,True,all_nodes_connected)
    agm=AGM()
    agm.mine_with_file(fp_clooca_in,fp_clooca_out,100)
    trans2=AGMTranslator()
    if minify==1:
        trans2.agm2gml(fp_clooca_out,fp_clooca_out_gml ,0,True,all_nodes_connected)
    else:
        trans2.agm2gml(fp_clooca_out,fp_clooca_out_gml ,0,True,all_nodes_connected)
        
if __name__ == '__main__':
    main()
