"""
Module pycdl_test
"""

__author__ = 'simon'

import unittest
import os
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

sys.path.append("..")
from pycdl import CDL, ColorDecision, ColorCorrection
data_path = "data"


class CDLTestCase(unittest.TestCase):
    def setUp(self):
        logging.info("Setup")
        self.cdl = CDL(filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), data_path, "test_color_correction.ccc"))
    
    def test_load(self):
        self.assertIsNotNone(self.cdl.first_color_item())

    def test_item_type(self):
        self.assertEqual(self.cdl.get_item_type(),CDL.COLOR_CORRECTION)
        
    def test_correction(self):
        cc_items = self.cdl.get_color_items()
        self.assertTrue(len(cc_items) == 1)
        self.assertIsInstance(cc_items[0], ColorCorrection)

    def test_correction_values(self):
        cc_items = self.cdl.get_color_items()
        self.assertTrue(len(cc_items) == 1)
        self.assertEqual(cc_items[0].correction_id, "test_shot_v1")
        self.assertEqual(cc_items[0].saturation, 1.0)
        self.assertEqual(cc_items[0].slope, (1.0, 1.0, 1.0))
        self.assertEqual(cc_items[0].offset, (0.0, 0.0, 0.0))
        self.assertEqual(cc_items[0].power, (1.0, 1.0, 1.0))
        

class CorrectionEDLTestCase(unittest.TestCase):
    def setUp(self):
        self.cc = ColorCorrection(
                cdl_edl_strings=[
                    "*ASC_SOP (0.9491 0.9552 0.9853)(0.1494 0.1645 0.2036)(1.5717 1.5728 1.5539)",
                    "*ASC_SAT 0.75",
                    "*FROM CLIP NAME:  dra_001_0002_v0003"
                ]
            )
    
    def test_cc(self):
        self.assertEqual(self.cc.correction_id,"dra_001_0002_v0003")
        self.assertEqual(self.cc.slope,(0.9491,0.9552,0.9853))
        self.assertEqual(self.cc.offset,(0.1494,0.1645,0.2036))
        self.assertEqual(self.cc.power,(1.5717,1.5728,1.5539))
        self.assertEqual(self.cc.saturation,0.75)

class CDLEDLTestCase(unittest.TestCase):
    def setUp(self):
        self.cdl = CDL(flavour=CDL.EDL_CDL,filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), data_path, "test_edl_cdl.edl"), timebase="24")
    
    def test_loaded_values(self):
        if self.cdl.edls_enabled():
            cc_items = self.cdl.get_color_items()
            self.assertEqual(len(cc_items), 3)
            self.assertIsInstance(cc_items[0],ColorCorrection)
        else:
            self.skipTest("EDL library not available, skipping")
    
    def test_loaded_cdl_first_item(self):
        if self.cdl.edls_enabled():
            cc_items = self.cdl.get_color_items()
            cc = cc_items[0]
            self.assertEqual(cc.slope,(0.8111,0.8112,0.8113))
            self.assertEqual(cc.offset,(0.2111,0.2112,0.2113))
            self.assertEqual(cc.power,(1.8111,1.8112,1.8113))
            self.assertEqual(cc.saturation,0.91)
            self.assertEqual(cc.correction_id,"dra_001_0001_v0001")
        else:
            self.skipTest("EDL library not available, skipping")

    def test_loaded_cdl_second_item(self):
        if self.cdl.edls_enabled():
            cc_items = self.cdl.get_color_items()
            cc = cc_items[1]
            self.assertEqual(cc.slope,(0.8121,0.8122,0.8123))
            self.assertEqual(cc.offset,(0.2121,0.2122,0.2123))
            self.assertEqual(cc.power,(1.8121,1.8122,1.8123))
            self.assertEqual(cc.saturation,0.82)
            self.assertEqual(cc.correction_id,"dra_001_0002_v0001")
        else:
            self.skipTest("EDL library not available, skipping")

    def test_loaded_cdl_third_item(self):
        if self.cdl.edls_enabled():
            cc_items = self.cdl.get_color_items()
            cc = cc_items[2]
            self.assertEqual(cc.slope,(0.8131,0.8132,0.8133))
            self.assertEqual(cc.offset,(0.2131,0.2132,0.2133))
            self.assertEqual(cc.power,(1.8131,1.8132,1.8133))
            self.assertEqual(cc.saturation,0.73)
            self.assertEqual(cc.correction_id,"dra_001_0003_v0001")
        else:
            self.skipTest("EDL library not available, skipping")
