"""model.py

This file is for model
(c) Toshiya Kawasaki 2013
"""
import json

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
                    _edges.append({"source":asso_id,"target":asso["source"],"type":"owned_member"})
                    _edges.append({"source":asso_id,"target":asso["target"],"type":"owned_member"})
                    no_inc = no_inc + 1
        edges=[]
        for asso in _edges:
            edges.append({"id":edges_no,"target":uri2id[asso["target"]],"source":uri2id[asso["source"]],"type":asso["type"]})
            edges_no = edges_no + 1
        graph={"nodes":nodes,"edges":edges}
        return graph
        
        