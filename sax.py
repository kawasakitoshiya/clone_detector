"""This file provides original SAX"""

import re
import xml.sax
import xml.sax.handler


class Handler(xml.sax.handler.ContentHandler):
    in_graph=False
    dic={"node":[],"edge":[]}
    def startElement(self, name, attrs):
        if name == "Graph":
            self.in_graph = True
        if self.in_graph:
            if name == "Vertex":
                nest={}
                nest["id"]=attrs.getValue("vertexId")
                self.dic["node"].append(nest)
            elif name == "Edge":
                nest={}
                nest["id"]=attrs.getValue("edgeId")
                nest["source"]=attrs.getValue("bgnVertexId")
                nest["target"]=attrs.getValue("endVertexId")
                self.dic["edge"].append(nest)
            elif name == "VertexLabel":
                pass
            elif name == "EdgeLabel":
                pass
        """"
        print "Start: " + name
        print "names",attrs.getNames()
        for key in attrs.getNames():
            
            print "types",attrs.getType(key)
            print "values",attrs.getValue(key)
        """

    def endElement(self, name):
        #print "End: " + name
        if name == "GraphML":
            print "end parse"
        pass
    
    def characters(self, content):
        #print "character:" + content
        return

class AGMTranslator(object):
    
    def dic2graphml(self, dic, out):
        file_pointer = open(out, "w")
        
        #header
        file_pointer.write('Creater\t"TK"\n')
        file_pointer.write("Version\t1.0\n")
        #graph
        file_pointer.write("graph\t[\n")
        #node
        num_node=0
        for node in dic["node"]:
            id = node["id"]
            file_pointer.write("\tnode\t[\n")
            file_pointer.write("\t\troot_index\t"+id+"\n")
            file_pointer.write("\t\tid\t"+id+"\n")
            #file_pointer.write("\t\tlabel\t"+node[label]+"\n")
            file_pointer.write("\t]\n")
            num_node=num_node+1
        #edge
        for edge in dic["edge"]:
            id = str(int(edge["id"])*-1)
            target=edge["target"]
            source=edge["source"]
            file_pointer.write("\tedge\t[\n")
            file_pointer.write("\t\troot_index\t"+id+"\n")
            file_pointer.write("\t\ttarget\t"+target+"\n")
            file_pointer.write("\t\tsource\t"+source+"\n")
            #file_pointer.write("\t\tlabel\t"+edge[label]+"\n")
            file_pointer.write("\t]\n")
        #end graph
        file_pointer.write("]\n")
        #footer
        file_pointer.write('Title\t"TestNetwork"\n')
        file_pointer.close()
        
    
    def agm2graphml(self, fp, out):
        parser = xml.sax.make_parser()
        handler=Handler()
        parser.setContentHandler(handler)
        parser.parse(fp)
        print handler.dic
        self.dic2graphml(handler.dic, out)
    


if __name__ == '__main__':
    agm = AGMTranslator()
    agm.agm2graphml("./utf8.xml", "o.gml")

