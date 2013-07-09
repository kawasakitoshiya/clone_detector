"""Model 

This file is for model
(c) Toshiya Kawasaki 2013
"""
import json

#to export xml 
import csv
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import datetime
from xml.dom import minidom

class Translator(object):
    @classmethod
    def prettify(self,elem):
        """Return a pretty-printed XML string for the Element"""
        rough_string = tostring(elem, encoding="utf-8",)
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="    ",encoding="utf-8")

    @classmethod
    def graph2agm(self, _graphs):
        """receive a graph in dictionary and convert to xml object
        you should know that dic object has underbar prefix
        """
        
        edge_type="undirected"
        
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
                        "edgeType":edge_type
                        })
                #print _edge
                if _edge.has_key("type"):
                    #edge_label=SubElement(edge,"EdgeLabel",{"field":"edge_name","value":_edge["type"]})
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
    

class Model(object):
    """Model class provides a dictionary model from file path"""
    def __init__(self, file_path):
        """receive a path to the json(txt) file and decode it to dictionary"""
        self.file_path = file_path
        file_pointer = open(self.file_path, "r")
        self.model = json.loads(file_pointer.read())
        file_pointer.close()
        #print self.model

    def clooca2graph(self, branch, version):
        """This method receives the whole json of clooca's project
        and branch and version to be converted
        """
        # is "root" correct ?
        uri2id={}
        nodes=[]
        _edges=[]
        no_inc=0
        edges_no=0
        classes = self.model["branch"][branch][version]["model"]["root"]["classes"]
        for key in classes:
            _class = classes[key]
            _id = _class["_sys_parent_uri"]+"."+_class["_sys_name"]
            uri2id[_id]=no_inc
            nodes.append({"id":no_inc,"name":_class["name"],"meta_class":_class["_sys_meta"]})
            
            no_inc = no_inc + 1
            for key in _class["attr"]:
                attr_id = _class["attr"][key]["_sys_parent_uri"]+_class["attr"][key]["_sys_name"]
                uri2id[attr_id]=no_inc
                _edges.append({"source":_id,"target":attr_id,"type":"owned_member"})
                nodes.append({
                        "id":no_inc,
                        "name":_class["attr"][key]["name"],
                        "type":_class["attr"][key]["type"],
                        "meta_class":_class["attr"][key]["_sys_meta"]
                        })
                no_inc = no_inc + 1
            assos = _class["srcAssociations"]
            for key in assos:
                asso = assos[key]
                if not len(asso)==0:
                    asso_id = asso["_sys_parent_uri"]+asso["_sys_name"]
                    uri2id[asso_id]=no_inc
                    #we may need name for association
                    nodes.append({
                        "id":no_inc,
                        "meta_class":asso["_sys_meta"]
                    })
                    _edges.append({"source":asso_id,"target":asso["source"],"type":"owned_member"})
                    _edges.append({"source":asso_id,"target":asso["target"],"type":"owned_member"})
                    no_inc = no_inc + 1
        edges=[]
        for asso in _edges:
            edges.append({"id":edges_no,"target":uri2id[asso["target"]],"source":uri2id[asso["source"]],"type":asso["type"]})
            edges_no = edges_no + 1
        graph={"nodes":nodes,"edges":edges}
        return graph
        
        