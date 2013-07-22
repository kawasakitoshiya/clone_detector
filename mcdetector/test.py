"""test 

this is a test for module test

(c) Toshiya Kawasaki 2013
"""


from model import *  
from translator import *  
import unittest

class AGMTranslatorClassTestCase(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_compare_class_is_same(self):
        translator=AGMTranslator() 
        class1={
            "name":"class1",
            "elements":[
                "att1",
                "att2",
                "att3"
            ]
        }
        class2={
            "name":"class1",
            "elements":[
                "att3",
                "att1",
                "att2"
            ]
        }
        similarity=translator.compare_classes(class1,class2)
        self.assertEqual(similarity, 1.0)
        
    def test_compare_class_is_almost_same(self):
        translator=AGMTranslator() 
        class1={
            "name":"class1",
            "elements":[
                "att1",
                "att2",
                "att3",
                "att4",
                "att5",
                "att6",
            ]
        }
        class2={
            "name":"class1",
            "elements":[
                "att3",
                "att1",
                "att2",
                "attdsa"
            ]
        }
        similarity=translator.compare_classes(class1,class2)
        self.assertEqual(similarity, 0.75)

if __name__ == "__main__":
    unittest.main()