from functools import reduce

from rfc5389stunserver.constants import AttrType
from rfc5389stunserver.stun_attribute import STUNAttribute

'''
errorcode = 420の場合のみ
'''


class UnknownAttributes(STUNAttribute):
    def __init__(self, attributes=[]):
        self.type = AttrType.UNKNOWN_ATTRIBUTES
        self.attributes = attributes

    @property
    def length(self):
        return len(self.attributes) * 2

    @property
    def value(self):
        return reduce(lambda v, x: v + x,
                      map(lambda x: x.to_bytes(2, 'big'), self.attributes))

    def addAttr(self, attr):
        self.attributes.append(attr)
