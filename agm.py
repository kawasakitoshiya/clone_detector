import commands

class AGM(object):
    """This class is just a wrapper of musashi-agm. just it"""
    def __init__(self):
        pass
    def mine_with_file(self, fp_in, fp_out, support):
        command="agm -S "+str(support)+" -i "+fp_in+" -o"+fp_out
        print commands.getoutput(command)
    