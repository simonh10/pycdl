"""
Module pycdl
"""

__author__ = 'simon'

import sys
import logging
from xml.dom import minidom
import traceback


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

    def __init__(self, flavour=XML_CDL):
        self._flavour = flavour
        self._cdl_string = None
        self._color_decisions = []


    def __getitem__(self, item):
        """ returns ColorDecision by index
        """
        return self._color_decisions[item]

    def __len__(self):
        """
        gets length of color decisions for iterating over color decisions
        """
        return len(self._color_decisions)


    def append(self, color_decision):
        self._color_decisions.append(color_decision)

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
        self._cdl_string = cdl_string
        if self._flavour == CDL.XML_CDL:
            self.parse_xml(cdl_string)

    def parse_xml(self, cdl_string):
        """
        Parse CDL XML string into ColorDecision objects
        """
        xmldoc = minidom.parseString(cdl_string)
        for node in xmldoc.getElementsByTagName('ColorDecision'):
            color_decision = ColorDecision(node)
            self._color_decisions.append(color_decision)

    def first_color_decision(self):
        """
        returns the first color decision in the list, simple function,
        throws exception if no color decisions
        """
        if len(self._color_decisions) > 0:
            return self._color_decisions[0]
        else:
            raise Exception("No Color Decision Available")


    def __repr__(self):
        """
        returns string representation of CDL
        """
        rep_list = []
        for color_decision in self._color_decisions:
            rep_list.append(str(color_decision))
        return "\n".join(rep_list)


class ColorDecision(object):
    """
    A singular color decision can contain multiple color corrections
    """

    def __init__(self, color_decision_node=None, decision_id=None):
        """
        initialise object with a color decision dom object, optional
        """
        self._decision_tree = color_decision_node
        self._corrections = []
        self._decision_id = decision_id
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
            color_correction = ColorCorrection(correction)
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


class ColorCorrection(object):
    """
    An individual color correction object
    """
    def __init__(self, color_correction_node=None):
        """
        initialise object with a color correction dom object, optional
        """
        self._correction_tree = color_correction_node
        self._slope = (1.0, 1.0, 1.0)
        self._power = (1.0, 1.0, 1.0)
        self._offset = (0.0, 0.0, 0.0)
        self._saturation = 1.0
        if color_correction_node:
            self.load_dom(color_correction_node)

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
        except Exception as exception:
            logging.log(logging.ERROR, "Unable to process Color Correction ")
            logging.log(logging.ERROR, exception)
            logging.log(logging.ERROR, traceback.format_exc())

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
        return ColorCorrection.get_float_tuple_from_text(''.join(rchildren))

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
        return values

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


def main():
    """
    main function used for testing the library
    """
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    cdl = CDL()
    cdl.load(sys.argv[1])
    correction = cdl.first_color_decision().first_correction()
    logging.log(logging.DEBUG, correction)


if __name__ == "__main__":
    main()


