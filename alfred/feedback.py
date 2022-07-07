# -*- coding: utf-8 -*-
from xml.etree import ElementTree
import xml.sax.saxutils as saxutils
import os, copy, random

from alfred.core import *

class Item(object):
    def __init__(self, **kwargs):
        self.content = {
            'title'     : kwargs.get('title', ''),
            'subtitle'  : kwargs.get('subtitle', ''),
            'icon'      : kwargs.get('icon', 'icon.png')
        }

        it = kwargs.get('icontype', '').lower()
        self.icon_type = it if it in ['fileicon', 'filetype'] else None

        valid = kwargs.get('valid', None)
        if isinstance(valid, (str)) and valid.lower() == 'no':
            valid = 'no'
        elif isinstance(valid, bool) and not valid:
            valid = 'no'
        else:
            valid = None

        self.attrb = {
            'uid'           : kwargs.get('uid', '{0}.{1}'.format(bundleID(), random.getrandbits(40))),
            'arg'           : kwargs.get('arg', None),
            'valid'         : valid,
            'autocomplete'  : kwargs.get('autocomplete', None),
            'type'          : kwargs.get('type', None)
        }

        content = {}
        for key in self.content.keys():
            if self.content[key] is not None:
                content[key] = self.content[key]
        self.content = content

        attrb = {}
        for key in self.attrb.keys():
            if self.attrb[key] is not None:
                attrb[key] = self.attrb[key]
        self.attrb = attrb

    def copy(self):
        return copy.copy(self)

    def getXMLElement(self):
        item = ElementTree.Element('item', self.attrb)
        for (k, v) in self.content.items():
            attrb = {}
            if k == 'icon' and self.icon_type:
                attrb['type'] = self.icon_type
            sub = ElementTree.SubElement(item, k, attrb)
            sub.text = v
        return item

class Feedback(object):
    def __init__(self):
        self.items = []

    def addItem(self, **kwargs):
        item = kwargs.pop('item', None)
        if not isinstance(item, Item):
            item = Item(**kwargs)
        self.items.append(item)

    def clean(self):
        self.items = []

    def isEmpty(self):
        return not bool(self.items)

    def get(self, unescape = False):
        ele_tree = ElementTree.Element('items')
        for item in self.items:
            ele_tree.append(item.getXMLElement())
        print(ele_tree)
        res = ElementTree.tostring(ele_tree, encoding='utf-8').decode("utf-8")
        if unescape:
            return saxutils.unescape(res)
        return res

    def output(self):
        print(self.get())