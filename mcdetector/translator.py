"""translator

Translator provides translations which
    dictionary type to 
(c) Toshiya Kawasaki 2013
"""

import sys
import re
import xml.sax
import xml.sax.handler
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import datetime
from xml.dom import minidom

from Queue import Queue

from util.util import *

class Handler(xml.sax.handler.ContentHandler):
    """This class translates AGM's graphml xml file
    to the graph format with dictionary object
    """
    def __init__(self):
        """We keep these variables as instance variables.
        old graphs will be remained
        if we use these as class variables 
        """
        self.in_graph = False
        self.in_vertex = False
        self.in_edge = False
        self.nest = {}
        self.graphs=[]
        self.dic = {}
        
    def startElement(self, name, attrs):
        """
        Begin analysing if Tag "Graph" appears
        if in Graph tag and find "Vertex" 
            we make nest objected and assign their node
        or "Edge" tag
            we make nest objected and assign their node and source and target
        then we will find "VertexLabel" or "EdgeLabel"
            adds the label to nest
        """
        if name == "Graph":
            self.dic={"id":int(attrs.getValue("graphId")),"node":[], "edge":[]}
            self.in_graph = True
        if self.in_graph:
            if name == "Vertex":
                if not self.in_vertex:
                    self.nest = {}
                    self.in_vertex = True
                    try:
                        self.nest["id"] = int(attrs.getValue("vertexId"))
                    except:
                        pass
            elif name == "Edge":
                if not self.in_edge:
                    self.nest = {}
                    self.in_edge = True
                    try:
                        #self.nest["id"] = attrs.getValue("edgeId")
                        self.nest["source"] = int(attrs.getValue("bgnVertexId"))
                        self.nest["target"] = int(attrs.getValue("endVertexId"))
                    except:
                        pass
            elif name == "VertexLabel":
                self.nest["label"] = attrs.getValue("value")
            elif name == "EdgeLabel":
                self.nest["label"] = attrs.getValue("value")

    def endElement(self, name):
        if name == "Graph":
            self.graphs.append(self.dic)
        elif self.in_vertex:
            self.in_vertex = False
            self.dic["node"].append(self.nest)
        elif self.in_edge:
            self.in_edge = False
            self.dic["edge"].append(self.nest)
        
        elif name == "GraphML":
            print "end parse"
        pass
    
    def characters(self, content):
        pass
        return

class AGMTranslator(object):
    """We can optionally use label which followed by graph number and node number 
    because crypt doesn't allow duplicate label
    """
    
    def is_all_nodes_connected(self,graph):
        """We judge if all nodes in the given graph is connected
        by using breath first search
        because a graph cannot be a fragment if it has a isolated node
        We deal with the graph as a undirected graph
        because task of this method is judge if all node
        is connected 
        """
        max_id=0
        for node in graph["node"]:
            if max_id < node["id"]:
                max_id=node["id"]
        all_nodes = max_id
        
        has_arrived=[True]*all_nodes
        
        #to treat the diversed node id 
        for node in graph["node"]:
            has_arrived[node["id"]-1]=False
        
        transitions=[]
        reversed_transitions=[]
        for i in range(all_nodes): 
            transitions.append([])
            reversed_transitions.append([])
        node_arrived = 0
        for i in range(len(graph["edge"])):
            edge=graph["edge"][i]
            source=int(edge["source"])-1
            target=int(edge["target"])-1
            transitions[source].append(target)
            reversed_transitions[target].append(source)
        start = int(graph["node"][0]["id"])-1
        queue=Queue()
        queue.put(start)
        def has_arrived_all(_has_arrived):
            for i in range(len(_has_arrived)):
                if _has_arrived[i] == False:
                    return False
            return True
        while not queue.empty():
            current = int(queue.get())
            if has_arrived[current]:
                continue
            has_arrived[current]=True
            for next in transitions[current]:
                next = int(next)
                queue.put(next)
            for next in reversed_transitions[current]:
                next = int(next)
                queue.put(next)
        
        if not has_arrived_all(has_arrived):
            return False
        return True
        
    def compare_classes(self, class1, class2):
        """compare the elements in classes
        First, map the elements 
        Second, calculate the similarity if the name of class is same
            Now the formula is (sim_name_of_class)*rate_name +sigma(sim_elem/((1.0-rate_name)/num_elem))
        
        I don't know which to use to determine the rate_of_similarity 
        
        Input format is...
        {
            name:<string>,
            elements:[<string>,...]
        }
        
        returns similarity [0,1]
        
        !!!TODO:
            we assumed weight of class name is 0.5
            and elements has wights that is (0.5 div size elements)
            It might better to use other weight for class name
            
            and now we don't separate attributes and operations
            It might better to get similarity respectively
            because name(:=attribute) and name(:=operation) will be judged as same
            
        """
        
        rate_name=0.5
        similarity=0
        if class1["name"]==class2["name"]:
            sim_name=1.0
            similarity+=sim_name*rate_name;
        attrs1=class1["elements"]
        attrs1.sort()
        attrs2=class2["elements"]
        attrs2.sort()
        num_same_elem=0
        for i in range(len(attrs1)):
            for j in range(i,len(attrs2)):
                if attrs1[i] == attrs2[j]:
                    num_same_elem += 1
                    continue
        if max(len(attrs1),len(attrs2))==0:  #if both classes dont have any attributes
            similarity += 1.0*(1.0-rate_name)
        else:
            similarity += (float)(num_same_elem)/(float)(max(len(attrs1),len(attrs2)))*(1.0-rate_name)
        return similarity
    
    def replace_containments_with_nodes_by_similarity(self, graph1, graph2, threshold):
        """We replace class node contains attribute nodes (including operations)
        with a new node which has new name represented with
        a non special sequential name if similarity between classes is larger than threshold
        
        elements of graph["nodes"] must be sorted by their id 
        or we have to refactor this method
        
        FEATURE
            this method calculates the similarity between two classes
            and replaces their name if similarity is larger than threshold
            so, classes almost same will be replaced by same named node
        
        CONSTRAINT
            this method can deal with just two classes
            we need additional approach to deal with more than 2 classes
        
        Steps:
            1. we makes class-nodes and transitions respectively
            2. for each class-nodes of class1 we calculate similarity and if similarity is larger than threshold, we change names
            3. we generate new graph by picking up only class-nodes and associated associate-node
        """
        ###########
        ##   Class1
        ##########
        #collect nodes which meta-class is Class1 
        class_nodes1=[]
        for i in range(len(graph1["nodes"])):
            node = graph1["nodes"][i]
            if node["meta_class"] == "simpleclassdiagram.Class":
                class_nodes1.append(node)
        
        #generate a transitions according to the number of nodes
        transitions1=[]
        class_containments_list1=[]
        for i in range(len(graph1["nodes"])): 
            transitions1.append([])
            class_containments_list1.append([])
            
        #transitons represents to which nodes a node has edges 
        for i in range(len(graph1["edges"])):
            edge=graph1["edges"][i]
            source=int(edge["source"])
            target=int(edge["target"])
            transitions1[source].append(target)
            if graph1["nodes"][source]["meta_class"] == "simpleclassdiagram.Class":
                class_containments_list1[source].append(graph1["nodes"][target]["name"])
        
        ###########
        ##   Class2
        ##########
        #collect nodes which meta-class is Class2
        class_nodes2=[]
        class_containments_list2=[]
        for i in range(len(graph2["nodes"])):
            node = graph2["nodes"][i]
            if node["meta_class"] == "simpleclassdiagram.Class":
                class_nodes2.append(node)
                
        
        #generate a transitions according to the number of nodes
        transitions2=[]
        for i in range(len(graph2["nodes"])): 
            transitions2.append([])
            class_containments_list2.append([])
        
        #transitons represents to which nodes a node has edges 
        for i in range(len(graph2["edges"])):
            edge=graph2["edges"][i]
            source=int(edge["source"])
            target=int(edge["target"])
            transitions2[source].append(target)
            if graph2["nodes"][source]["meta_class"] == "simpleclassdiagram.Class":
                class_containments_list2[source].append(graph2["nodes"][target]["name"])
        
        #############
        ## start comparing
        #############
        
        for i in range(len(class_nodes1)):
            for j in range(i,len(class_nodes2)):
                cls1={
                    "name":class_nodes1[i]["name"],
                    "elements":class_containments_list1[i]
                }
                cls2={
                    "name":class_nodes2[j]["name"],
                    "elements":class_containments_list2[j]
                }
                if self.compare_classes(cls1, cls2) > threshold:
                    print "Yahoo!",cls1["name"]
        pass
    
    def graphs2gml(self, graphs, out, min_node ,labeled, all_nodes_connected):
        """Input format
            graphs is ...
            [{
                "id":<int>
                "node":[{"id":<int>,"label":<string>},...],
                "edge":[{"source":<int>,"target":<int>,"label":<string>},...]
            },...]
        
        """
        file_pointer = open(out, "w")
        #header
        gml_string=""
        gml_string+='Creater\t"TK"\n'
        gml_string+="Version\t1.0\n"
        
        graphes_added_to_gml=0
        for i in range(len(graphs)):
            if len(graphs[i]["node"]) < min_node:
                continue
            graph=graphs[i]
            if not self.is_all_nodes_connected(graph):
                color='"#ffd700"'
                if all_nodes_connected:
                    continue
            else:
                color='"#ffc0cb"'
            #graph
            gml_string+="graph\t[\n"
            #node
            gml_string+="\tid\t"+str(graph["id"])+"\n"
            num_node = 0
            for node in graph["node"]:
                id = str(node["id"]+i*100)
                root_index=str(node["id"]+i*100)
                gml_string+="\tnode\t[\n"
                gml_string+="\t\troot_index\t"+root_index+"\n"
                gml_string+="\t\tid\t"+id+"\n"
                gml_string+="\t\tgraphics\t[\n"
                
                gml_string+="\t\t\tx\t"+str(num_node*100)+"\n"
                gml_string+="\t\t\ty\t"+str(num_node%2*100+graphes_added_to_gml*300)+"\n"
                gml_string+="\t\t\tw\t50\n"
                gml_string+="\t\t\th\t50\n" 
                gml_string+="\t\t\tfill\t"+color+"\n"
                gml_string+="\t\t]\n" #end graphics
                if labeled:
                    if node.has_key("label"):
                        gml_string+="\t\tlabel\t\""+node["label"]+"."+str(i)+"."+str(num_node)+"\"\n"
                    else:
                        gml_string+="\t\tlabel\t\""+str(i)+"."+str(num_node)+"\"\n"
                gml_string+="\t]\n" #end node
                num_node = num_node+1
            #edge
            for edge in graph["edge"]:
                #id = str(int(edge["id"])*-1)
                target=str(edge["target"]+i*100)
                source=str(edge["source"]+i*100)
                gml_string+="\tedge\t[\n"
                #gml_string+="\t\troot_index\t"+id+"\n")
                gml_string+="\t\ttarget\t"+target+"\n"
                gml_string+="\t\tsource\t"+source+"\n"
                if labeled and edge.has_key("label"):
                    gml_string+="\t\tlabel\t\""+edge["label"]+"."+str(i)+"."+str(num_node)+"\"\n"
                gml_string+="\t]\n"
            #end graph
            gml_string+="]\n"
            graphes_added_to_gml = graphes_added_to_gml +1
        #footer
        gml_string+='Title\t"TestNetwork"\n'
        file_pointer.write(gml_string)
        file_pointer.close()
        
    
    def agm2gml(self, fp, out,  min_node, labeled, all_nodes_connected):
        self.parser = xml.sax.make_parser()
        self.handler=Handler()
        self.parser.setContentHandler(self.handler)
        self.parser.parse(fp)
        #print handler.graphs
        #print self.handler.graphs
        self.graphs2gml(self.handler.graphs, out, min_node, labeled, all_nodes_connected)
        
    def prettify(cls,elem):
        """Return a pretty-printed XML string for the Element"""
        rough_string = tostring(elem, encoding="utf-8",)
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="    ",encoding="utf-8")

    def graph2agm(self, _graphs):
        """receive a graph in dictionary and convert to xml object
        you should know that dic object has underbar prefix
        """
        
        root = Element('GraphML')
        root.set('version', '0.1')
        header = SubElement(root,"Header",{"copyright":"hogehoge","description":"xt2gml"})
        
        node_names={}
        edge_names={}
        
        graph_data = SubElement(root,"GraphData")
        i_graph=1
        for _graph in _graphs:
        
            #vertexes for a graph
            vertexes=[]
            for _node in _graph["nodes"]:
                vertex=Element("Vertex",{"vertexId":str(_node["id"]+1),"dimension":str(1)})
                if _node.has_key("name"):
                    vertex_label=SubElement(vertex,"VertexLabel",{"field":"node_name","value":_node["name"]})
                    node_names[_node["name"]]=True
                vertexes.append(vertex)
                    
            #edges for a graph
            edges=[]
            for _edge in _graph["edges"]:
                edge=Element("Edge",{
                        "edgeId":str(_edge["id"]+1),
                        "dimension":str(1),
                        "bgnVertexId":str(_edge["source"]+1),
                        "endVertexId":str(_edge["target"]+1),
                        "edgeType":_edge["edge_type"]
                        })
                #print _edge
                if _edge.has_key("type"):
                    edge_label=SubElement(edge,"EdgeLabel",{"field":"edge_name","value":_edge["type"]})
                    edge_names[_edge["type"]]=True
                edges.append(edge)
                #edge_names[]
            graph = SubElement(graph_data,"Graph",{"graphId":str(i_graph)})
            i_graph=i_graph+1
            graph.extend(vertexes)
            graph.extend(edges)
            
        #header
        data_dictionary = SubElement(header,"DataDictionary",{"numberOfFields":str(2)})
        node_name_field = SubElement(data_dictionary,"DataField",{"name":"node_name","optype":"categorical"})
        node_name_keys=[]
        for key in node_names:
            node_name_keys.append(Element("Value",{"value":key}))
        node_name_field.extend(node_name_keys)
        
        edge_name_field = SubElement(data_dictionary,"DataField",{"name":"edge_name","optype":"categorical"})
        SubElement(edge_name_field,"Value",{"value":"owned_member"})
        return self.prettify(root)
    


if __name__ == '__main__':
    
    argvs = sys.argv 
    argc = len(argvs)
    
    agm = AGMTranslator()
    if argc == 1:
        agm.agm2gml("files/agm.utf8.xml", "output/o.gml",0,False)
    elif argc == 3:
        agm.agm2gml(argvs[1], argvs[2],0,False)
    elif argc == 4 and argvs[3]=="-l":
        agm.agm2gml(argvs[1], argvs[2],0,True)
    else:
        print "invalid arguments"

