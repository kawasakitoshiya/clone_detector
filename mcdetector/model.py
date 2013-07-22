"""model

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
        similarity += (float)(num_same_elem)/(float)(max(len(attrs1),len(attrs2)))*(1.0-rate_name)
        return similarity

    def replace_containments_with_nodes(self):
        """We replace class node contains attribute nodes (including operations)
        with a new node which has new name represented with
        a hash generated from the class name and other attributes
        
        elements of graph["nodes"] must be sorted by their id 
        or we have to refactor this method
        """
        
        #collect nodes which meta-class is Class 
        class_nodes=[]
        for i in range(len(self.graph["nodes"])):
            node = self.graph["nodes"][i]
            if node["meta_class"] == "simpleclassdiagram.Class":
                class_nodes.append(node)
        
        #generate a transitions according to the number of nodes
        transitions=[]
        for i in range(len(self.graph["nodes"])): 
            transitions.append([])
        
        #transitons represents to which nodes a node has edges 
        #transitions[2] = [4,7] means node2 has edges to node4 and node7
        for i in range(len(self.graph["edges"])):
            edge=self.graph["edges"][i]
            source=int(edge["source"])
            target=int(edge["target"])
            transitions[source].append(target)
        
        #gather the names of attributes and operations which a Class node owns
        #then sort the names and connect them
        #and minify names by making a hash from the connected string
        #add the attributes and operations to nodes_to_remove
        nodes_to_remove=[False]*len(self.graph["nodes"])
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
            represent_num=0
            for chara in represent_string:
                represent_num += ord(chara)
            class_nodes[i]["name"] = "mini."+str(represent_num) #replace class node's name with represent string
        
        #if edge is connected to a node to remove
        #add the edge to edges_to_remove
        edges_to_remove=[False]*len(self.graph["edges"])
        for edge in self.graph["edges"]:
            edge_need = False
            source=edge["source"]
            target=edge["target"]
            for i in range(len(nodes_to_remove)):
                if nodes_to_remove[i]:
                    if i == source or i == target:
                        edges_to_remove[edge["id"]]=True
        
        #we throw old graph away and create new graph
        #so we create new_nodes and new_edges
        #by iterating the old nodes and old edges
        #according to nodes_to_reomve and edges_to_remove
        new_nodes=[]
        for i in range(len(nodes_to_remove)):
            if not nodes_to_remove[i]:
                new_nodes.append(self.graph["nodes"][i])
        new_edges=[]
        for i in range(len(edges_to_remove)):
            if not edges_to_remove[i]:
                new_edges.append(self.graph["edges"][i])
                
        #assign new id
        old2new=[-1]*len(self.graph["nodes"])
        for (i,new_node) in  zip(range(len(new_nodes)),new_nodes):
            old2new[new_node["id"]]=i
        for node in new_nodes:
            node["id"]=old2new[node["id"]]
        for edge in new_edges:
            edge["source"]=old2new[edge["source"]]
            edge["target"]=old2new[edge["target"]]
        
        #update the graph by new_nodes and new_edges
        self.graph["nodes"] = new_nodes
        self.graph["edges"] = new_edges
        return self.graph
        
    def clooca2graph(self, branch, version):
        """This method receives the whole JSON of clooca's project
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
        
        