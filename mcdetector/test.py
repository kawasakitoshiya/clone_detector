"""test 

this is a test for module test

(c) Toshiya Kawasaki 2013
"""


from model import *  
from translator import *  
import unittest
import copy

class AGMTranslatorClassTestCase(unittest.TestCase):
    def setUp(self):
        self.translator=AGMTranslator() 
        pass
    def tearDown(self):
        pass

    def test_compare_class_is_same(self):
        class1={
            "name":"class1",
            "elements":[
                "att1",
                "att2",
                "att3"
            ]
        }
        class2={
            "name":"class1",
            "elements":[
                "att3",
                "att1",
                "att2"
            ]
        }
        similarity=self.translator.compare_classes(class1,class2)
        self.assertEqual(similarity, 1.0)
        
    def test_compare_class_is_almost_same(self):
        class1={
            "name":"class1",
            "elements":[
                "att1",
                "att2",
                "att3",
                "att4",
                "att5",
                "att6",
            ]
        }
        class2={
            "name":"class1",
            "elements":[
                "att3",
                "att1",
                "att2",
                "attdsa"
            ]
        }
        similarity=self.translator.compare_classes(class1,class2)
        self.assertEqual(similarity, 0.75)
    def test_replace_containments_with_nodes_by_similarity(self):
        
        nodes=[]
        n_index=0
        
        edges=[]
        e_index=0
        #Class1
        #nodes [1]->[2,3,4,5]
        node_cls1={"id":n_index,"name":"Class1","meta_class":"simpleclassdiagram.Class"}
        cls1_index=n_index
        nodes.append(node_cls1)
        n_index += 1
        
        for i in range(4): 
            attr = {"id":n_index,"name":"Class1_"+str(i),"meta_class":"simpleclassdiagram.Attribute"}
            edge={"id":e_index,"edge_type":"undirected","type":"owned_member","source":cls1_index,"target":n_index}
            edges.append(edge)
            nodes.append(attr)
            n_index+=1
            e_index+=1
            
        #Class2
        #nodes [6]->[7,8,9,10]
        node_cls2={"id":n_index,"name":"Class2","meta_class":"simpleclassdiagram.Class"}
        cls2_index=n_index
        nodes.append(node_cls2)
        n_index+=1
        
        for i in range(4): 
            attr = {"id":n_index,"name":"Class1_"+str(i),"meta_class":"simpleclassdiagram.Attribute"}
            edge={"id":e_index,"edge_type":"undirected","type":"owned_member","source":cls2_index,"target":n_index}
            edges.append(edge)
            nodes.append(attr)
            n_index+=1
            e_index+=1
        
        #association between cls1 and cls2  simpleclassdiagram.Association
        node_asso12={"id":n_index,"name":"association","meta_class":"simpleclassdiagram.Association"}
        asso_index=n_index
        nodes.append(node_asso12)
        n_index+=1
        edge={"id":e_index,"edge_type":"undirected","type":"owned_member","source":asso_index,"target":cls1_index}
        edges.append(edge)
        e_index+=1
        edge={"id":e_index,"edge_type":"undirected","type":"owned_member","source":asso_index,"target":cls2_index}
        edges.append(edge)
        e_index+=1        
        
        graph_base={"nodes":nodes,"edges":edges}
        graph_comp = copy.deepcopy(graph_base)
        
        #add extra attribute to Class1
        graph_comp["nodes"].append({"id":n_index,"name":"Class1_x","meta_class":"simpleclassdiagram.Attribute"})
        extra_cls1_index=n_index
        n_index+=1
        graph_comp["edges"].append({"id":e_index,"edge_type":"undirected","type":"owned_member","source":cls1_index,"target":extra_cls1_index})
        e_index+=1
        
        #add copy of class1
        node_cls1={"id":n_index,"name":"Class1","meta_class":"simpleclassdiagram.Class"}
        cls1_index=n_index
        graph_comp["nodes"].append(node_cls1)
        n_index += 1
        
        for i in range(4): 
            attr = {"id":n_index,"name":"Class1_"+str(i),"meta_class":"simpleclassdiagram.Attribute"}
            edge={"id":e_index,"edge_type":"undirected","type":"owned_member","source":cls1_index,"target":n_index}
            graph_comp["edges"].append(edge)
            graph_comp["nodes"].append(attr)
            n_index+=1
            e_index+=1
        
        self.translator.replace_containments_with_nodes_by_similarity(graph_base,graph_comp,0.75)
        print graph_base
        print graph_comp
        
        pass
    

if __name__ == "__main__":
    unittest.main()