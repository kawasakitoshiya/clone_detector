"""This file provides original SAX"""

import re
import xml.sax
import xml.sax.handler


class Handler(xml.sax.handler.ContentHandler):
    in_graph = False
    in_vertex = False
    in_edge = False
    nest = {}
    dic = {"node":[], "edge":[]}
    def startElement(self, name, attrs):
        if name == "Graph":
            self.in_graph = True
        if self.in_graph:
            if name == "Vertex":
                self.nest = {}
                self.in_vertex = True
                self.nest["id"] = attrs.getValue("vertexId")
            elif name == "Edge":
                self.nest = {}
                self.in_edge = True
                self.nest["id"] = attrs.getValue("edgeId")
                self.nest["source"] = attrs.getValue("bgnVertexId")
                self.nest["target"] = attrs.getValue("endVertexId")
            elif name == "VertexLabel":
                self.nest["label"] = attrs.getValue("value")
            elif name == "EdgeLabel":
                self.nest["label"] = attrs.getValue("value")

    def endElement(self, name):
        if self.in_vertex:
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
    """We cant use 'label because gml doesnt allow duplicate label name'"""
    def dic2graphml(self, dic, out):
        file_pointer = open(out, "w")
        
        #header
        file_pointer.write('Creater\t"TK"\n')
        file_pointer.write("Version\t1.0\n")
        #graph
        file_pointer.write("graph\t[\n")
        #node
        num_node = 0
        for node in dic["node"]:
            id = node["id"]
            file_pointer.write("\tnode\t[\n")
            file_pointer.write("\t\troot_index\t"+id+"\n")
            file_pointer.write("\t\tid\t"+id+"\n")
            file_pointer.write("\t\tgraphics\t[\n")
            
            file_pointer.write("\t\t\tx\t"+str(num_node*100)+"\n")
            file_pointer.write("\t\t\ty\t"+str(num_node%2*100)+"\n")
            file_pointer.write("\t\t\tw\t50\n")
            file_pointer.write("\t\t\th\t50\n")
            file_pointer.write("\t\t]\n") #end graphics
            
            file_pointer.write("\t\tlabel\t\""+node["label"]+"\"\n")
            file_pointer.write("\t]\n") #end node
            num_node = num_node+1
        #edge
        for edge in dic["edge"]:
            id = str(int(edge["id"])*-1)
            target=edge["target"]
            source=edge["source"]
            file_pointer.write("\tedge\t[\n")
            file_pointer.write("\t\troot_index\t"+id+"\n")
            file_pointer.write("\t\ttarget\t"+target+"\n")
            file_pointer.write("\t\tsource\t"+source+"\n")
            #file_pointer.write("\t\tlabel\t\""+edge["label"]+"\"\n")
            file_pointer.write("\t]\n")
        #end graph
        file_pointer.write("]\n")
        #footer
        file_pointer.write('Title\t"TestNetwork"\n')
        file_pointer.close()
        
    
    def agm2gml(self, fp, out):
        parser = xml.sax.make_parser()
        handler=Handler()
        parser.setContentHandler(handler)
        parser.parse(fp)
        print handler.dic
        self.dic2graphml(handler.dic, out)
    


if __name__ == '__main__':
    agm = AGMTranslator()
    agm.agm2gml("./utf8.xml", "output/o.gml")

