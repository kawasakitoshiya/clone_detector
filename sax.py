"""This file provides original SAX"""

import re


class Sax(object):
    """Sax"""
    t_open=0
    t_close=1
    t_alone=2
    def __init__(self, file_path):
        """ """
        self.file_path = file_path
        self.json = {}

    def eval_line(self, line, callback_for_line):
        end_index = line.index('>')
        element={}
        if line[end_index-1] == "/":
            element["type"]=self.t_alone
        elif line[1] == "/":
            element["type"]=self.t_close
        else:
            element["type"]=self.t_open
        
        list = line[1:end_index-1].split(' ')
        
        rest="".join(list[1:])
        element["attributes"]={}
        element["tag"] = list[0]
        pattern = re.search(r' (.)+=(.)',rest)
        print pattern.group()
        return
        if len(list)>1:
            for elem in list[1:]:
                key_value=elem.split("=")
                key=key_value[0].strip()
                print key_value,list
                element["attributes"][key]=key_value[1].strip()
        callback_for_line(element)
    
    def parse(self, callback_for_line):
        with open(self.file_path) as lines:
            for line in lines:
                start_index = line.index('<')
                self.eval_line(line[start_index:], callback_for_line)
                try:
                    #TODO: deal with line which have more than one tags
                    pass
                except ValueError as value_error:
                    print "Not a tag line."
                except Exception as e:
                    print e
        
if __name__ == '__main__':
    sax = Sax("./agm.graphml")
    
    def cb(data):
        print data["type"]
    
    sax.parse(cb)