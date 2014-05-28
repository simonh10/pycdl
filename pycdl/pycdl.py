"""
Module pycdl
"""

__author__ = 'simon'


import sys
import logging
from xml.dom import minidom
import traceback


logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')

class CDL():
    XML_CDL='xml_cdl'
    def __init__(self,flavour=XML_CDL):
        self._flavour=flavour
        self._cdl_string=None
        self._color_decisions=[]

    def load(self,filename):
        with open(filename) as f:
            self.read(f)

    def read(self,filehandle):
        cdl_string=filehandle.read()
        self.loads(cdl_string)


    def loads(self,cdl_string):
        self._cdl_string=cdl_string
        if self._flavour==CDL.XML_CDL:
            self.parseXML(cdl_string)

    def parseXML(self,cdl_string):
        xmldoc = minidom.parseString(cdl_string)
        for n in xmldoc.getElementsByTagName('ColorDecision'):
            color_decision=ColorDecision(n)
            self._color_decisions.append(color_decision)

    def firstColorDecision(self):
        if len(self._color_decisions) > 0:
            return self._color_decisions[0]
        else:
            raise Exception("No Color Decision Available")


    def __repr__(self):
        rep_list=[]
        for c in self._color_decisions:
            rep_list.append(str(c))
        return "\n".join(rep_list)


class ColorDecision():
    def __init__(self,color_decision_tree,id=None):
        self._decision_tree=color_decision_tree
        self._corrections=[]
        self._id=id
        self.loadDOM(self._decision_tree)

    def loadDOM(self,decision_dom):
        try:
            self._id=decision_dom._get_id()
            logging.log(logging.DEBUG,"id for color decision set to "+str(self._id))
        except Exception as e:
            logging.log(logging.DEBUG,"No id attribute set for color decision")
        color_corrections=decision_dom.getElementsByTagName('ColorCorrection')
        for cc in color_corrections:
            color_correction=ColorCorrection(cc)
            self._corrections.append(color_correction)

    def __repr__(self):
        rep_list=[]
        for c in self._corrections:
            rep_list.append(str(c))
        return "\n".join(rep_list)

    def firstCorrection(self):
        if len(self._corrections) > 0:
            return self._corrections[0]
        else:
            raise Exception("No Color Correction Available")


class ColorCorrection():
    def __init__(self,color_correction_tree):
        self._correction_tree=color_correction_tree
        self._slope=(1.0,1.0,1.0)
        self._power=(1.0,1.0,1.0)
        self._offset=(0.0,0.0,0.0)
        self._saturation=1.0
        self.loadDOM(color_correction_tree)

    def loadDOM(self,correction_dom):
        try:
            sop_node=correction_dom.getElementsByTagName('SOPNode')[0]
            slope_node=sop_node.getElementsByTagName('Slope')[0]
            offset_node=sop_node.getElementsByTagName('Offset')[0]
            power_node=sop_node.getElementsByTagName('Power')[0]
            self.slope=ColorCorrection.getFloatTupleFromNode(slope_node)
            self.offset=ColorCorrection.getFloatTupleFromNode(offset_node)
            self.power=ColorCorrection.getFloatTupleFromNode(power_node)
            sat_node=correction_dom.getElementsByTagName('SatNode')[0]
            saturation_node=sat_node.getElementsByTagName('Saturation')[0]
            self.saturation=ColorCorrection.getFloatFromNode(saturation_node)
        except Exception as e:
            logging.log(logging.ERROR, "Unable to process Color Correction ")
            logging.log(logging.ERROR, e)
            logging.log(logging.ERROR, traceback.format_exc())

    @staticmethod
    def getFloatFromNode(node):
        children=node.childNodes
        rc = []
        for n in children:
            if n.nodeType == n.TEXT_NODE:
                rc.append(n.data)
        return float(''.join(rc))

    @staticmethod
    def getFloatTupleFromNode(node):
        children=node.childNodes
        rc = []
        for n in children:
            if n.nodeType == n.TEXT_NODE:
                rc.append(n.data)
        return ColorCorrection.getFloatTupleFromText(''.join(rc))

    @staticmethod
    def getFloatTupleFromText(text_string):
        values=text_string.split(' ')
        for i in range(len(values)):
            try:
                values[i]=float(values[i])
            except Exception as e:
                logging.log(logging.ERROR,"Error processing numbers for parameter")
        return values

    @property
    def slope(self,value):
        self._slope=value

    @property
    def slope(self):
        return self._slope

    @property
    def power(self,value):
        self._power=value

    @property
    def power(self):
        return self._power

    @property
    def offset(self,value):
        self._offset=value

    @property
    def offset(self):
        return self._offset

    @property
    def saturation(self,value):
        self._saturation=value

    @property
    def saturation(self):
        return self._saturation

    def __repr__(self):
        return ','.join((str(self.slope),str(self.power),str(self.offset),str(self.saturation)))

if __name__ == "__main__":
    cdl=CDL()
    cdl.load(sys.argv[1])
    correction=cdl.firstColorDecision().firstCorrection()
    print correction


