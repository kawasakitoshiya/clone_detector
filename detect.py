"""detect.py

I mainly uses this file to write main excutions
(c) Toshiya Kawasaki 2013
"""

import sys 
from mcdetector.model import Model
from mcdetector.agm import AGM
from mcdetector.translator import AGMTranslator

if __name__ == '__main__':
    
    minify=False
    all_nodes_connected = True
    
    graphs=[]
    model=Model("./data/test.json")
    model.clooca2graph("master","HEAD")
    if minify:
        model.replace_containments_with_nodes()
    graphs.append(model.graph)
    
    model2=Model("./data/test2.json")
    model2.clooca2graph("master","HEAD")
    if minify:
        model2.replace_containments_with_nodes()
    graphs.append(model2.graph)

    model3=Model("./data/test3.json")
    model3.clooca2graph("master","HEAD")
    if minify:
        model3.replace_containments_with_nodes()
    graphs.append(model3.graph)
    trans0 = AGMTranslator()
    agm_xml = trans0.graph2agm(graphs)

    fp_clooca_in = 'work/clooca.in.xml'
    f = open(fp_clooca_in, 'w') 
    f.write(agm_xml)
    f.close()
    trans=AGMTranslator()
    fp_clooca_in_gml = "work/clooca.in.gml"
    trans.agm2gml(fp_clooca_in,fp_clooca_in_gml ,0,True,all_nodes_connected)
    fp_clooca_out = "work/clooca.out.xml"
    agm=AGM()
    agm.mine_with_file(fp_clooca_in,fp_clooca_out,100)
    trans2=AGMTranslator()
    fp_clooca_out_gml = "work/clooca.out.gml"
    if minify:
        trans2.agm2gml(fp_clooca_out,fp_clooca_out_gml ,0,True,all_nodes_connected)
    else:
        trans2.agm2gml(fp_clooca_out,fp_clooca_out_gml ,4,True,all_nodes_connected)
    