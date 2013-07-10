"""detect.py

I mainly uses this file to write main excutions
(c) Toshiya Kawasaki 2013
"""

import sys 
from model import Model
from agm import AGM
from translator import AGMTranslator

if __name__ == '__main__':
    
    flag=False
    
    graphs=[]
    model=Model("./data/test.json")
    model.clooca2graph("master","HEAD")
    if flag:
        model.replace_containments_with_nodes()
    graphs.append(model.graph)
    
    model2=Model("./data/test2.json")
    model2.clooca2graph("master","HEAD")
    if flag:
        model2.replace_containments_with_nodes()
    graphs.append(model2.graph)

    model3=Model("./data/test3.json")
    model3.clooca2graph("master","HEAD")
    if flag:
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
    trans.agm2gml(fp_clooca_in,fp_clooca_in_gml ,0,True)
    fp_clooca_out = "work/clooca.out.xml"
    agm=AGM()
    agm.mine_with_file(fp_clooca_in,fp_clooca_out,100)
    
    trans2=AGMTranslator()
    fp_clooca_out_gml = "work/clooca.out.gml"
    trans2.agm2gml(fp_clooca_out,fp_clooca_out_gml ,4,True)
    