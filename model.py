"""model.py

This file is for clooca's model
(c) Toshiya Kawasaki 2013
"""
import json

class Model(object):
    """Model class provides a dictionary model from file path
    self.graph=
    {
        "nodes":[{"id":<int>,"name":<string>,"meta_classs":<string>},...],
        "edges":[{"id":<int>,"source":<int>,"target":<int>,"edge_type":<"directed" or "directed">,"type":<string>},...]
    }
    
    """
    def __init__(self, file_path):
        """receive a path to the json(txt) file and decode it to dictionary"""
        self.file_path = file_path
        file_pointer = open(self.file_path, "r")
        self.model = json.loads(file_pointer.read())
        file_pointer.close()
        #print self.model
    def replace_containments_with_nodes(self):
        """We replace class node contains attribute nodes (including operations)
        with a new node which has new name represented with
        a hash generated from the class name and other attributes
        
        elements of graph["nodes"] must be sorted by their id 
        or we have to refactor this method
        """
        class_nodes=[]
        nodes_to_remove=[False]*len(self.graph["nodes"])
        for i in range(len(self.graph["nodes"])):
            node = self.graph["nodes"][i]
            if node["meta_class"] == "simpleclassdiagram.Class":
                class_nodes.append(node)
        
        transitions=[]
        for i in range(len(self.graph["nodes"])): 
            transitions.append([])
        
        for i in range(len(self.graph["edges"])):
            edge=self.graph["edges"][i]
            source=int(edge["source"])
            target=int(edge["target"])
            transitions[source].append(target)
            
        for i in range(len(class_nodes)):
            node_id = class_nodes[i]["id"]
            represent_string=""
            attributes=[]
            represent_string += class_nodes[i]["name"]
            class_containments=transitions[node_id]
            for j in range(len(class_containments)):
                attr_node = class_containments[j]
                nodes_to_remove[attr_node]=True
                attributes.append(self.graph["nodes"][attr_node]["name"])
            attributes.sort()
            for item in attributes:
                represent_string += "." + item
            class_nodes[i]["name"] = represent_string #replace class node's name with represent string
        new_nodes=[]
        for i in range(len(nodes_to_remove)):
            if not nodes_to_remove[i]:
                new_nodes.append(self.graph["nodes"][i])
        self.graph["nodes"] = new_nodes
        
        new_edges=[]
        edges_to_remove=[False]*len(self.graph["edges"])
        for edge in self.graph["edges"]:
            edge_need = False
            source=edge["source"]
            target=edge["target"]
            for i in range(len(nodes_to_remove)):
                if nodes_to_remove[i]:
                    if i == source or i == target:
                        edges_to_remove[edge["id"]]=True
        for i in range(len(edges_to_remove)):
            if not edges_to_remove[i]:
                new_edges.append(self.graph["edges"][i])
        self.graph["edges"] = new_edges
        return self.graph
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
            if _class.has_key("attr"):
                for key in _class["attr"]:
                    attr = _class["attr"][key]
                    attr_id = attr["_sys_parent_uri"]+attr["_sys_name"]
                    uri2id[attr_id]=no_inc
                    _edges.append({"source":_id,"target":attr_id,"type":"owned_member"})
                    nodes.append({
                            "id":no_inc,
                            "name":attr["name"],
                            "type":attr["type"],
                            "meta_class":attr["_sys_meta"]
                            })
                    no_inc = no_inc + 1
            if _class.has_key("operation"):
                for key in _class["operation"]:
                    operation=_class["operation"][key]
                    operation_id = operation["_sys_parent_uri"]+operation["_sys_name"]
                    uri2id[operation_id]=no_inc
                    _edges.append({"source":_id,"target":operation_id,"type":"owned_member"})
                    nodes.append({
                            "id":no_inc,
                            "name":operation["name"],
                            "type":operation["type"],
                            "meta_class":operation["_sys_meta"]
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
                        "name":"association", #is naming these nodes "association" correct ?
                        "meta_class":asso["_sys_meta"]
                    })
                    _edges.append({"source":asso_id,"target":asso["source"],"type":"owned_member","edge_type":"undirected"})
                    _edges.append({"source":asso_id,"target":asso["target"],"type":"owned_member","edge_type":"undirected"})
                    no_inc = no_inc + 1
        edges=[]
        for asso in _edges:
            edges.append({
                "id":edges_no,
                "target":uri2id[asso["target"]],
                "source":uri2id[asso["source"]],
                "type":asso["type"],
                "edge_type":"undirected"
            })
            edges_no = edges_no + 1
        self.graph={"nodes":nodes,"edges":edges}
        return self.graph
        
        