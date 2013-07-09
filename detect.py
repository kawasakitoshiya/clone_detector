import sys 
from model import Model


if __name__ == '__main__':
    model=Model("./data/test.json")
    model.model2agm("master","HEAD")