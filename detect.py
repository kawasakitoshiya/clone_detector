import sys 
from model import Model,Translator


if __name__ == '__main__':
    graphs=[]
    model=Model("./data/test.json")
    graphs.append(model.clooca2graph("master","HEAD"))
    model2=Model("./data/test2.json")
    graphs.append(model2.clooca2graph("master","HEAD"))
    print Translator().graph2agm(graphs)