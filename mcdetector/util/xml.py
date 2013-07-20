class XMLUtil(object):
    @classmethod
    def tab_str(cls,num_tab):
        if num_tab <= 0:
            raise Exception(0,"num_tab should be larger than 0.")
        return "\t"*num_tab