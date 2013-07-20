"""test 

this is a test for module test

(c) Toshiya Kawasaki 2013
"""


from xml import *  
import unittest

class XMLUtilClassTestCase(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_tab_str(self):
        self.assertEqual("\t", XMLUtil().tab_str(1))
        self.assertEqual("\t\t\t\t", XMLUtil().tab_str(4))
        
        self.assertRaises(Exception, lambda: XMLUtil().tab_str(0))
        self.assertRaises(Exception, lambda: XMLUtil().tab_str(-1))

if __name__ == "__main__":
    unittest.main()