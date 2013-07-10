"""translator.py

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
        all_nodes = len(graph["node"])
        has_arrived=[False]*all_nodes
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
        
    def graphs2gml(self, graphs, out, min_node ,labeled ):
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
        file_pointer.write('Creater\t"TK"\n')
        file_pointer.write("Version\t1.0\n")
        
        graphes_added_to_gml=0
        for i in range(len(graphs)):
            if len(graphs[i]["node"]) < min_node:
                continue
            graph=graphs[i]
            if not self.is_all_nodes_connected(graph):
                color='"#ffd700"'
                continue
            else:
                color='"#ffc0cb"'
            #graph
            file_pointer.write("graph\t[\n")
            #node
            file_pointer.write("\tid\t"+str(graph["id"])+"\n")
            num_node = 0
            for node in graph["node"]:
                id = str(node["id"]+i*100)
                root_index=str(node["id"]+i*100)
                file_pointer.write("\tnode\t[\n")
                file_pointer.write("\t\troot_index\t"+root_index+"\n")
                file_pointer.write("\t\tid\t"+id+"\n")
                file_pointer.write("\t\tgraphics\t[\n")
                
                file_pointer.write("\t\t\tx\t"+str(num_node*100)+"\n")
                file_pointer.write("\t\t\ty\t"+str(num_node%2*100+graphes_added_to_gml*300)+"\n")
                file_pointer.write("\t\t\tw\t50\n")
                file_pointer.write("\t\t\th\t50\n") 
                file_pointer.write("\t\t\tfill\t"+color+"\n")
                file_pointer.write("\t\t]\n") #end graphics
                if labeled:
                    if node.has_key("label"):
                        file_pointer.write("\t\tlabel\t\""+node["label"]+"."+str(i)+"."+str(num_node)+"\"\n")
                    else:
                        file_pointer.write("\t\tlabel\t\""+str(i)+"."+str(num_node)+"\"\n")
                file_pointer.write("\t]\n") #end node
                num_node = num_node+1
            #edge
            for edge in graph["edge"]:
                #id = str(int(edge["id"])*-1)
                target=str(edge["target"]+i*100)
                source=str(edge["source"]+i*100)
                file_pointer.write("\tedge\t[\n")
                #file_pointer.write("\t\troot_index\t"+id+"\n")
                file_pointer.write("\t\ttarget\t"+target+"\n")
                file_pointer.write("\t\tsource\t"+source+"\n")
                if labeled and edge.has_key("label"):
                    file_pointer.write("\t\tlabel\t\""+edge["label"]+"."+str(i)+"."+str(num_node)+"\"\n")
                file_pointer.write("\t]\n")
            #end graph
            file_pointer.write("]\n")
            graphes_added_to_gml = graphes_added_to_gml +1
        #footer
        file_pointer.write('Title\t"TestNetwork"\n')
        file_pointer.close()
        
    
    def agm2gml(self, fp, out,  min_node, labeled):
        self.parser = xml.sax.make_parser()
        self.handler=Handler()
        self.parser.setContentHandler(self.handler)
        self.parser.parse(fp)
        #print handler.graphs
        self.graphs2gml(self.handler.graphs, out, min_node, labeled)
        
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

