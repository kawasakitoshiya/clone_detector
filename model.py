"""Model 

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
    def model2agm(self, branch, version):
        """This method receives the whole json of clooca's project
        and branch and version to be converted
        """
        # is "root" correct ?
        uri2id={}
        nodes=[]
        _edges=[]
        no_inc=0
        classes = self.model["branch"][branch][version]["model"]["root"]["classes"]
        for key in classes:
            _class = classes[key]
            _id = _class["_sys_parent_uri"]+"."+_class["_sys_name"]
            uri2id[_id]=no_inc
            nodes.append({"id":no_inc,"name":_class["name"],"meta_class":_class["_sys_meta"]})
            
            no_inc = no_inc + 1
            for key in _class["attr"]:
                attr_id = _class["attr"][key]["_sys_parent_uri"]+_class["attr"][key]["name"]
                uri2id[attr_id]=no_inc
                _edges.append({"source":_id,"target":attr_id})
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
                    _edges.append(asso)
        edges=[]
        edges_no=0
        for asso in _edges:
            edges.append({"id":edges_no,"target":uri2id[asso["target"]],"source":uri2id[asso["source"]]})
            edges_no = edges_no + 1
        graph={"nodes":nodes,"edges":edges}
        
        
        
        
        