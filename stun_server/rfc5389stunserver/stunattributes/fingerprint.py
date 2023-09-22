import binascii

from rfc5389stunserver.constants import AttrType
from rfc5389stunserver.stun_attribute import STUNAttribute


class Fingerprint(STUNAttribute):
    def __init__(self, data: bytes):
        self.type = AttrType.FINGERPRINT
        self.xor_value = 0x5354554e
        self.value = binascii.crc32(data) ^ self.xor_value

    @property
    def len(self):
        return len(self.value)
