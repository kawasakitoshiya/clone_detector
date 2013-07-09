"""detect.py

I mainly uses this file to write main excutions
(c) Toshiya Kawasaki 2013
"""

import sys 
from model import Model
from agm import AGM
from translator import AGMTranslator

if __name__ == '__main__':
    graphs=[]
    model=Model("./data/test.json")
    graphs.append(model.clooca2graph("master","HEAD"))
    model2=Model("./data/test2.json")
    graphs.append(model2.clooca2graph("master","HEAD"))
    model3=Model("./data/test3.json")
    graphs.append(model3.clooca2graph("master","HEAD"))
    
    agm_xml = AGMTranslator().graph2agm(graphs)
    fp_clooca_in = 'work/clooca.in.xml'
    f = open(fp_clooca_in, 'w') 
    f.write(agm_xml)
    f.close()
    
    fp_clooca_out = "work/clooca.out.xml"
    agm=AGM()
    agm.mine_with_file(fp_clooca_in,fp_clooca_out,100)
    
    trans=AGMTranslator()
    fp_clooca_out_gml = "work/clooca.out.gml"
    trans.agm2gml(fp_clooca_out,fp_clooca_out_gml ,4,True)
    