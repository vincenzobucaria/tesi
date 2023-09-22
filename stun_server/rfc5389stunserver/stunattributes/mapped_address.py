import ipaddress
import logging

from rfc5389stunserver.constants import AttrType
from rfc5389stunserver.stun_attribute import STUNAttribute

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
This attribute is used only by servers for achieving backwards compatibility
with RFC 3489 [RFC3489] clients.
"""


class MappedAddress(STUNAttribute):
    def __init__(self, port: int, ipaddr: str):
        self.type = AttrType.MAPPED_ADDRESS
        self.port = port
        self.ipaddr = ipaddress.ip_address(ipaddr)
        self.isIPv6 = self.ipaddr.version == 6

    @property
    def value(self):
        return ((0).to_bytes(1, 'big') +
                self.addr_faimily.to_bytes(1, 'big') +
                self.port.to_bytes(2, 'big') +
                self.ipaddr.packed)

    @property
    def length(self):
        if (self.isIPv6):
            return 1 + 1 + 2 + 16
        else:
            return 1 + 1 + 2 + 4

    @property
    def addr_faimily(self):
        if (self.isIPv6):
            return 0x02
        else:
            return 0x01
