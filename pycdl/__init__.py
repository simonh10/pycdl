#-*- coding: utf-8 -*-
"""
Python CDL parsing library
"""

__version__ = '0.5.4'


__author__ = 'simon'

import sys
import logging
import json
import os
import re
import StringIO
from xml.dom import minidom
import traceback
allow_edls = False
try:
    import edl
    allow_edls = True
except Exception as e:
    allow_edls = False

class CDL(object):
    """ The CDL

    Holds :class:`.ColorDecision` instances. It can be indexed to reach each
     of the :class: `.ColorDecision` s like::

    >>> cdl = CDL(flavour=CDL.XML_CDL)
    >>> cdl.append(ColorDecision(color_decision_node))
    >>> cdl[0]

    :param str flavour: Optional cdl flavour definition defaults to XML, other
     flavours to be added later.
      `flavour` can be skipped
    """

    XML_CDL = 'xml_cdl'
    EDL_CDL = 'edl_cdl'
    COLOR_DECISION = 'COLOR_DECISION'
    COLOR_CORRECTION = 'COLOR_CORRECTION'

    def __init__(self, flavour=XML_CDL, filename=None, timebase="24"):
        self._edls_enabled = allow_edls
        self._timebase = timebase
        self._flavour = flavour
        self._cdl_string = None
        self._color_items = []
        self._item_type = CDL.COLOR_DECISION
        self._filename = None
        if filename:
            self._filename = os.path.basename(filename)
            self.load(filename)


    def __getitem__(self, item):
        """ returns ColorDecision by index
        """
        return self._color_items[item]

    def __len__(self):
        """
        gets length of color decisions for iterating over color decisions
        """
        return len(self._color_items)

    def edls_enabled(self):
        return self._edls_enabled

    def append(self, color_item):
        self._color_items.append(color_item)

    def load(self, filename):
        """
        Loads CDL from filename, passes to the read function for loading
        """
        with open(filename) as filehandle:
            self.read(filehandle)

    def read(self, filehandle):
        """
        Reads CDL from Filehandle, passed to loads for processing
        """
        cdl_string = filehandle.read()
        self.loads(cdl_string)


    def loads(self, cdl_string):
        """
        Loads CDL from string, depending on the flavour definition it passes
         to the processing function
        """
        if cdl_string and len(cdl_string) > 0:
            self._cdl_string = cdl_string
            if self._flavour == CDL.XML_CDL:
                self.parse_xml(cdl_string)
            elif self._flavour == CDL.EDL_CDL:
                self.parse_edl(cdl_string)
            else:
                raise Exception("Invalid CDL type specified")
        else:
            raise Exception("Empty CDL string")
                

    def parse_edl(self, cdl_string):
        if self._edls_enabled:
            self.item_type = CDL.COLOR_CORRECTION
            parser = edl.Parser(self._timebase)
            edl_io = StringIO.StringIO(cdl_string)
            edl_list = parser.parse(edl_io)
            for event in edl_list:
                color_correction = ColorCorrection(cdl_edl_strings=event.get_comments(),source_file=self._filename)
                self._color_items.append(color_correction)        

    def get_dom(self, cdl_string):
        return minidom.parseString(cdl_string)

    def parse_xml(self, cdl_string):
        """
        Parse CDL XML string into ColorDecision objects
        """
        xmldoc = self.get_dom(cdl_string)
        if len(xmldoc.getElementsByTagName('ColorDecision')) > 0:
            self._item_type = CDL.COLOR_DECISION
            for node in xmldoc.getElementsByTagName('ColorDecision'):
                color_decision = ColorDecision(node, source_file=self._filename)
                self._color_items.append(color_decision)
        elif len(xmldoc.getElementsByTagName('ColorCorrection')) > 0:
            self._item_type = CDL.COLOR_CORRECTION
            for node in xmldoc.getElementsByTagName('ColorCorrection'):
                color_correction = ColorCorrection(node, source_file=self._filename)
                self._color_items.append(color_correction)            
        else:
            raise Exception("No color decisions found")

    def first_color_item(self):
        """
        returns the first color item in the list, simple function,
        throws exception if no color item
        """
        if len(self._color_items) > 0:
            return self._color_items[0]
        else:
            raise Exception("No Color Item Available")


    def __repr__(self):
        """
        returns string representation of CDL
        """
        rep_list = []
        for color_item in self._color_items:
            rep_list.append(str(color_item))
        return "\n".join(rep_list)

    def get_item_type(self):
        return self._item_type

    def get_color_items(self):
        return self._color_items

class ColorDecision(object):
    """
    A singular color decision can contain multiple color corrections
    """

    def __init__(self, color_decision_node=None, decision_id=None, source_file=None):
        """
        initialise object with a color decision dom object, optional
        """
        self._decision_tree = color_decision_node
        self._corrections = []
        self._decision_id = decision_id
        self._source_file = source_file
        if color_decision_node:
            self.load_dom(self._decision_tree)

    def __getitem__(self, item):
        """
        Returns color correction object based on index
        """
        return self._corrections[item]

    def __len__(self):
        """
        Returns number of color corrections available
        """
        return len(self._corrections)


    def append(self, color_correction):
        self._corrections.append(color_correction)

    def load_dom(self, decision_dom):
        """
        Load the color decision from a dom node passed to it.
        """
        try:
            self._decision_id = decision_dom._get_id()
            logging.log(logging.DEBUG,
                        "id for color decision set to " + str(self._decision_id))
        except Exception as exception:
            logging.log(logging.DEBUG,
                        "No id attribute set for color decision")
            logging.log(logging.DEBUG,
                        exception)
        color_corrections = decision_dom.getElementsByTagName('ColorCorrection')
        for correction in color_corrections:
            color_correction = ColorCorrection(correction, source_file=self._source_file)
            self.append(color_correction)

    def __repr__(self):
        """
        Rteurns a string representation of the color decision
        """
        rep_list = []
        for correction in self._corrections:
            rep_list.append(str(correction))
        return "\n".join(rep_list)

    def first_correction(self):
        """
        Returns the first available correction in the system throws exception
         if none available
        """
        if len(self._corrections) > 0:
            return self._corrections[0]
        else:
            raise Exception("No Color Correction Available")
        
    def get_corrections(self):
        return self._corrections;


class ColorCorrection(object):
    """
    An individual color correction object
    """
    def __init__(self, color_correction_node=None, cdl_edl_strings=None, source_file=None):
        """
        initialise object with a color correction dom object, optional
        """
        self._correction_tree = color_correction_node
        self._slope = (1.0, 1.0, 1.0)
        self._power = (1.0, 1.0, 1.0)
        self._offset = (0.0, 0.0, 0.0)
        self._saturation = 1.0
        self._id = None
        self._source_file = source_file
        self._cdl_matchers = [r"\*\s*ASC_SOP \((\-*\d\.\d+) (\-*\d\.\d+) (\-*\d\.\d+)\)\((\-*\d\.\d+) (\-*\d\.\d+) (\-*\d\.\d+)\)\((\-*\d\.\d+) (\-*\d\.\d+) (\-*\d\.\d+)\)", r"\*\s*ASC_SAT (\-*\d\.\d+)", r"\*\s*FROM CLIP NAME\:\s+(\w+)"]
        if color_correction_node:
            self.load_dom(color_correction_node)
        elif cdl_edl_strings:
            for s in cdl_edl_strings:
                self.process_edl_string(s)
                

    def process_edl_string(self, s):
        if re.match(self._cdl_matchers[0], s):
            m = re.match(self._cdl_matchers[0], s)
            self._slope = (float(m.group(1)),float(m.group(2)), float(m.group(3)))
            self._offset = (float(m.group(4)),float(m.group(5)), float(m.group(6)))
            self._power = (float(m.group(7)),float(m.group(8)), float(m.group(9)))
        if re.match(self._cdl_matchers[1], s):
            m = re.match(self._cdl_matchers[1], s)
            self._saturation = float(m.group(1))
        if re.match(self._cdl_matchers[2], s):
            m = re.match(self._cdl_matchers[2], s)
            self._id = m.group(1)

    def to_JSON(self):
        struct = {
            "slope":self._slope,
            "power":self._power,
            "offset":self._offset,
            "saturation":self.saturation,
            "id":self._id
        }
        return json.dumps(struct)

    def load_dom(self, correction_dom):
        """
        Load the color correction from a dom node passed to it. Does not throw
         exception but logs parsing errors to the
         ERROR log output
        """
        try:
            sop_node = correction_dom.getElementsByTagName('SOPNode')[0]
            slope_node = sop_node.getElementsByTagName('Slope')[0]
            offset_node = sop_node.getElementsByTagName('Offset')[0]
            power_node = sop_node.getElementsByTagName('Power')[0]
            self.slope = ColorCorrection.get_float_tuple_from_node(slope_node)
            self.offset = ColorCorrection.get_float_tuple_from_node(offset_node)
            self.power = ColorCorrection.get_float_tuple_from_node(power_node)
            sat_node = correction_dom.getElementsByTagName('SatNode')[0]
            saturation_node = sat_node.getElementsByTagName('Saturation')[0]
            self.saturation = ColorCorrection.get_float_from_node(saturation_node)
            self._id = ColorCorrection.get_attribute_value_by_name(correction_dom,"id")
        except Exception as exception:
            logging.log(logging.ERROR, "Unable to process Color Correction ")
            logging.log(logging.ERROR, exception)
            logging.log(logging.ERROR, traceback.format_exc())

    @staticmethod
    def get_attribute_value_by_name(node,attribute_name):
        value = None
        for k in node.attributes.keys():
            if str(k) == str(attribute_name):
                value = node.attributes[k].value
        return value
    
    @staticmethod
    def get_float_from_node(node):
        """
        Returns the floating point number contained within the node passed to it
        """
        children = node.childNodes
        rchildren = []
        for node in children:
            if node.nodeType == node.TEXT_NODE:
                rchildren.append(node.data)
        return float(''.join(rchildren))

    @staticmethod
    def get_float_tuple_from_node(node):
        """
        Returns the floating point numbers as a list contained within the node
         passed to it
        """
        children = node.childNodes
        rchildren = []
        for node in children:
            if node.nodeType == node.TEXT_NODE:
                rchildren.append(node.data)
        return tuple(ColorCorrection.get_float_tuple_from_text(''.join(rchildren)))

    @staticmethod
    def get_float_tuple_from_text(text_string):
        """
        Returns the floating point numbers as a list contained within the text
         passed to it
        """
        values = text_string.split(' ')
        for i in range(len(values)):
            try:
                values[i] = float(values[i])
            except Exception as exception:
                logging.log(logging.ERROR, "Error processing numbers for parameter")
                logging.log(logging.ERROR, exception)
        return tuple(values)

    def set_correction_id(self,correction_id):
        self._id = correction_id
        
    def get_correction_id(self):
        return self._id

    correction_id = property(get_correction_id, set_correction_id)

    @property
    def filename(self):
        return self._source_file
    
    @property
    def slope(self):
        return self._slope

    @slope.setter
    def slope(self, value):
        self._slope = value

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, value):
        self._power = value

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def saturation(self):
        return self._saturation

    @saturation.setter
    def saturation(self, value):
        self._saturation = value

    def __repr__(self):
        """
        Returns a string representation of the color correction
        """
        return ','.join((str(self.slope),
                         str(self.power),
                         str(self.offset),
                         str(self.saturation)))

