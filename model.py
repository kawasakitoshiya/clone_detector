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
        print self.model